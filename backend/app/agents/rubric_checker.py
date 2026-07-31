import logging
import re
from typing import Any

from app.templates.section_rules import SECTION_RULES

logger = logging.getLogger("proposalcraft.rubric_checker")

PLACEHOLDER_PATTERNS = re.compile(
    r"\b(not specified|tbd|to be determined|to be decided|lorem ipsum|todo|n/a|none)\b",
    re.IGNORECASE,
)

_PLACEHOLDER_STRINGS = {"", "not specified", "tbd", "to be determined", "to be decided", "lorem ipsum", "todo", "n/a", "none"}
_PLACEHOLDER_NUMBERS = {0, 0.0}


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


def check_word_count(document: dict, min_words: int = 40, max_words: int = 5000) -> list[str]:
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
        if is_llm_written and word_count < min_words and sec_name != "conclusion":
            issues.append(f"{sec_name}: {word_count} words (min {min_words})")
        if word_count > max_words:
            issues.append(f"{sec_name}: {word_count} words (max {max_words})")
    return issues


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

    return result


def _section_to_text(sec_data: Any) -> str:
    if isinstance(sec_data, str):
        return sec_data
    if isinstance(sec_data, dict):
        parts = []
        for v in sec_data.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts.extend(str(item) for item in v)
        return " ".join(parts)
    if isinstance(sec_data, list):
        return " ".join(str(item) for item in sec_data)
    return str(sec_data)


def _check_number(section: dict, section_key: str, engine: dict, engine_key: str, mismatches: list) -> None:
    sec_val = section.get(section_key)
    eng_val = engine.get(engine_key)
    if sec_val is not None and eng_val is not None:
        try:
            if abs(float(sec_val) - float(eng_val)) > 0.01:
                mismatches.append(f"pricing.{section_key}: doc={sec_val} vs engine={eng_val}")
        except (ValueError, TypeError):
            pass
