from app.agents.rubric_checker import (
    check_proposal,
    check_word_count,
    check_section_density,
    check_generic_phrases,
    no_placeholder_leak,
    NARRATIVE_MIN_WORDS,
)


class TestPlaceholderDetection:
    def test_engine_list_repr_not_flagged(self):
        doc = {
            "sections": {
                "timeline": {
                    "phases": [
                        {
                            "phase": 4,
                            "name": "Sprint 2 - Feature Development",
                            "activities": ["Feature modules", "Frontend pages"],
                            "deliverables": ["Feature modules", "Integrated frontend"],
                        }
                    ]
                }
            }
        }
        assert no_placeholder_leak(doc) == []

    def test_placeholder_bracket_text_still_flagged(self):
        doc = {"sections": {"security": {"authentication": "signed within [Month 1] timeframe"}}}
        assert "security" in no_placeholder_leak(doc)

    def test_placeholder_string_still_flagged(self):
        doc = {"sections": {"terms": {"confidentiality": "TBD"}}}
        assert "terms" in no_placeholder_leak(doc)


class TestWordCountThresholds:
    def test_sparse_narrative_section_flagged(self):
        doc = {"sections": {"executive_summary": {"business_overview": "short and thin text"}}}
        issues = check_word_count(doc)
        assert any("executive_summary" in i for i in issues)

    def test_dense_narrative_section_passes(self):
        text = " ".join("word" for _ in range(NARRATIVE_MIN_WORDS + 10))
        doc = {"sections": {"executive_summary": {"business_overview": text}}}
        assert check_word_count(doc) == []

    def test_engine_sections_not_checked(self):
        doc = {"sections": {"pricing": {"one_time_cost": 1000}}}
        assert check_word_count(doc) == []

    def test_conclusion_exempt(self):
        doc = {"sections": {"conclusion": {"summary": "short"}}}
        assert check_word_count(doc) == []


class TestSectionDensity:
    def test_sparse_narrative_flagged(self):
        doc = {"sections": {"executive_summary": {"business_overview": "just a few words here"}}}
        issues = check_section_density(doc)
        assert any("executive_summary" in i for i in issues)

    def test_sparse_about_company_flagged(self):
        doc = {"sections": {"about_company": {"who_we_are": "only two fields filled, no depth"}}}
        issues = check_section_density(doc)
        assert any("about_company" in i for i in issues)

    def test_full_section_passes(self):
        text = " ".join("word" for _ in range(250))
        doc = {"sections": {"security": {"authentication": text}}}
        assert check_section_density(doc) == []

    def test_missing_section_skipped(self):
        assert check_section_density({"sections": {}}) == []

    def test_table_sections_not_checked(self):
        doc = {"sections": {"pricing": {"one_time_cost": 1000}}}
        assert check_section_density(doc) == []


class TestGenericPhrases:
    def test_two_plus_banned_phrases_flagged(self):
        text = "state-of-the-art platform with seamless user experience and robust functionality"
        doc = {"sections": {"security": {"authentication": text}}}
        issues = check_generic_phrases(doc)
        assert any("security" in i for i in issues)

    def test_single_banned_phrase_tolerated(self):
        text = "We build a state-of-the-art solution for the client."
        doc = {"sections": {"executive_summary": {"business_overview": text}}}
        assert check_generic_phrases(doc) == []

    def test_check_proposal_fails_on_genericness(self):
        text = "best-in-class and industry-leading and seamless user experience"
        doc = {"sections": {"terms": {"confidentiality": text}}}
        result = check_proposal(doc)
        assert result.passed is False
        assert result.genericness_issues

    def test_check_proposal_fails_on_density(self):
        doc = {"sections": {"executive_summary": {"business_overview": "tiny"}}}
        result = check_proposal(doc)
        assert result.passed is False
        assert result.density_issues
