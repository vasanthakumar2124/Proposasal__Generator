import logging
import re
from typing import Any

from app.templates.section_rules import SECTION_RULES

logger = logging.getLogger("proposalcraft.rubric_checker")

PLACEHOLDER_PATTERNS = re.compile(
    r"(\b(not specified|tbd|to be determined|to be decided|lorem ipsum|todo|n/a|none)\b|\[[^\]]{1,40}\])",
    re.IGNORECASE,
)

_PLACEHOLDER_STRINGS = {"", "not specified", "tbd", "to be determined", "to be decided", "lorem ipsum", "todo", "n/a", "none"}
_PLACEHOLDER_NUMBERS = {0, 0.0}

# LLM-written narrative sections (prose-heavy). These must be substantial:
# 5-7 sentences per field per the writer prompt, so a 120-word floor only
# catches genuinely truncated output.
NARRATIVE_SECTIONS = {
    "executive_summary",
    "client_understanding",
    "proposed_solution",
    "security",
    "terms",
}
NARRATIVE_MIN_WORDS = 120
# Structurally dense sections (tables/lists) need less prose but still a floor.
STRUCTURAL_MIN_WORDS = 60

# Estimated rendered words per full A4 page at 12pt body / 1.65 line-height
# with the current 20mm 18mm 20mm margins.
TARGET_WORDS_PER_PAGE = 400
DENSITY_MIN_FILL = 0.5

# Phrases the writer prompt already prohibits — enforced here so a violation
# becomes a retry signal instead of just a prompt rule.
BANNED_GENERIC_PHRASES = [
    "state-of-the-art",
    "state of the art",
    "seamless user experience",
    "robust functionality",
    "best-in-class",
    "best in class",
    "industry-leading",
    "industry leading",
]


def _is_placeholder(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip().lower() in _PLACEHOLDER_STRINGS
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return val in _PLACEHOLDER_NUMBERS
    if isinstance(val, (list, dict)):
        return len(val) == 0
    return False


class RubricCheckResult:
    def __init__(self):
        self.missing_sections: list[str] = []
        self.placeholder_sections: list[str] = []
        self.number_mismatches: list[str] = []
        self.word_count_issues: list[str] = []
        self.density_issues: list[str] = []
        self.genericness_issues: list[str] = []
        self.passed: bool = True

    def fail(self) -> bool:
        self.passed = False
        return False

    @property
    def failed_sections(self) -> set[str]:
        return set(self.missing_sections) | set(self.placeholder_sections)

    def __repr__(self) -> str:
        issues = []
        if self.missing_sections:
            issues.append(f"missing={self.missing_sections}")
        if self.placeholder_sections:
            issues.append(f"placeholders={self.placeholder_sections}")
        if self.number_mismatches:
            issues.append(f"num_mismatch={self.number_mismatches}")
        if self.word_count_issues:
            issues.append(f"wc_issues={self.word_count_issues}")
        if self.density_issues:
            issues.append(f"density_issues={self.density_issues}")
        if self.genericness_issues:
            issues.append(f"generic_issues={self.genericness_issues}")
        return f"RubricCheckResult(passed={self.passed}, {'; '.join(issues)})" if issues else f"RubricCheckResult(passed={self.passed})"


def required_sections_present(document: dict, section_rules: dict | None = None) -> list[str]:
    rules = section_rules or SECTION_RULES
    sections = document.get("sections", document)
    missing = []
    for sec_name, rule in rules.items():
        if sec_name in ("cover_page", "table_of_contents"):
            continue
        if rule.get("generated_by") == "rag":
            continue
        if rule.get("required", False):
            sec_data = sections.get(sec_name)
            if _is_placeholder(sec_data):
                missing.append(sec_name)
            elif isinstance(sec_data, dict):
                has_content = any(
                    not _is_placeholder(v)
                    for v in sec_data.values()
                )
                if not has_content:
                    missing.append(sec_name)
    return missing


def no_placeholder_leak(document: dict) -> list[str]:
    sections = document.get("sections", document)
    flagged = []
    for sec_name, sec_data in sections.items():
        if sec_name in ("cover_page", "table_of_contents"):
            continue
        text = _section_to_text(sec_data)
        if PLACEHOLDER_PATTERNS.search(text):
            flagged.append(sec_name)
        elif _is_placeholder(sec_data):
            flagged.append(sec_name)
    return flagged


def numbers_match_engine_output(document: dict, engine_context: dict) -> list[str]:
    sections = document.get("sections", document)
    mismatches = []

    pricing_data = engine_context.get("pricing_data", {})
    timeline_data = engine_context.get("timeline_data", {})

    pricing_section = sections.get("pricing", {})
    if isinstance(pricing_section, dict):
        _check_number(pricing_section, "one_time_cost", pricing_data, "one_time_cost", mismatches)
        _check_number(pricing_section, "monthly_cost", pricing_data, "monthly_cost", mismatches)
        _check_number(pricing_section, "annual_cost", pricing_data, "annual_cost", mismatches)

    timeline_section = sections.get("timeline", {})
    if isinstance(timeline_section, dict):
        _check_number(timeline_section, "total_duration_months", timeline_data, "total_duration_months", mismatches)
        _check_number(timeline_section, "total_duration_weeks", timeline_data, "total_duration_weeks", mismatches)
        _check_number(timeline_section, "phase_count", timeline_data, "phase_count", mismatches)

    return mismatches


def check_word_count(document: dict, max_words: int = 5000) -> list[str]:
    sections = document.get("sections", document)
    rules = SECTION_RULES
    issues = []
    for sec_name, sec_data in sections.items():
        rule = rules.get(sec_name)
        if sec_name in ("cover_page", "table_of_contents"):
            continue
        text = _section_to_text(sec_data)
        word_count = len(text.split())
        is_llm_written = rule is None or rule.get("generated_by") == "llm"
        if not is_llm_written:
            continue
        if sec_name == "conclusion":
            continue
        floor = NARRATIVE_MIN_WORDS if sec_name in NARRATIVE_SECTIONS else STRUCTURAL_MIN_WORDS
        if word_count < floor:
            issues.append(f"{sec_name}: {word_count} words (min {floor})")
        if word_count > max_words:
            issues.append(f"{sec_name}: {word_count} words (max {max_words})")
    return issues


def check_section_density(
    document: dict,
    target_words_per_page: int = TARGET_WORDS_PER_PAGE,
    min_fill: float = DENSITY_MIN_FILL,
) -> list[str]:
    """Estimate rendered page fill per narrative section (word count vs a full
    A4 page) and flag any section under ~50% fill so the writer gets a retry
    signal instead of shipping a sparse section."""
    sections = document.get("sections", document)
    issues = []
    for sec_name in sorted(NARRATIVE_SECTIONS | {"about_company"}):
        sec_data = sections.get(sec_name)
        if sec_data is None:
            continue
        text = _section_to_text(sec_data)
        word_count = len(text.split())
        fill = word_count / target_words_per_page
        if fill < min_fill:
            issues.append(
                f"{sec_name}: {word_count} words (~{fill:.0%} page fill, min {min_fill:.0%})"
            )
    return issues


def check_generic_phrases(document: dict, max_hits: int = 1) -> list[str]:
    """Flag sections containing 2+ banned generic phrases. The writer prompt
    already prohibits these; this turns the rule into an enforceable check."""
    sections = document.get("sections", document)
    flagged = []
    for sec_name, sec_data in sections.items():
        if sec_name in ("cover_page", "table_of_contents"):
            continue
        text = _section_to_text(sec_data).lower()
        hits = sum(phrase in text for phrase in BANNED_GENERIC_PHRASES)
        if hits > max_hits:
            flagged.append(f"{sec_name}: {hits} banned generic phrases")
    return flagged


def check_proposal(document: dict, engine_context: dict | None = None) -> RubricCheckResult:
    result = RubricCheckResult()

    missing = required_sections_present(document)
    if missing:
        result.missing_sections = missing
        result.fail()

    placeholders = no_placeholder_leak(document)
    if placeholders:
        result.placeholder_sections = placeholders
        result.fail()

    if engine_context:
        mismatches = numbers_match_engine_output(document, engine_context)
        if mismatches:
            result.number_mismatches = mismatches
            result.fail()

    wc_issues = check_word_count(document)
    if wc_issues:
        result.word_count_issues = wc_issues
        result.fail()

    density_issues = check_section_density(document)
    if density_issues:
        result.density_issues = density_issues
        result.fail()

    generic_issues = check_generic_phrases(document)
    if generic_issues:
        result.genericness_issues = generic_issues
        result.fail()

    return result


def _section_to_text(sec_data: Any) -> str:
    if isinstance(sec_data, str):
        return sec_data
    parts: list[str] = []
    _flatten_text(sec_data, parts)
    return " ".join(parts)


def _flatten_text(value: Any, parts: list[str]) -> None:
    """Collect only string leaves. Python/JSON list reprs (e.g. "['Feature
    modules', 'Integrated frontend']") must never reach placeholder pattern
    matching, or short engine arrays get misflagged as placeholder brackets."""
    if isinstance(value, str):
        parts.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            _flatten_text(v, parts)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _flatten_text(item, parts)


def _check_number(section: dict, section_key: str, engine: dict, engine_key: str, mismatches: list) -> None:
    sec_val = section.get(section_key)
    eng_val = engine.get(engine_key)
    if sec_val is not None and eng_val is not None:
        try:
            if abs(float(sec_val) - float(eng_val)) > 0.01:
                mismatches.append(f"pricing.{section_key}: doc={sec_val} vs engine={eng_val}")
        except (ValueError, TypeError):
            pass
