import sys; sys.path.insert(0, 'backend')
from app.graph.nodes import _merge_system_sections


def _timeline_phases():
    return [
        {"phase": 1, "name": "Discovery & Architecture", "duration_weeks": 3,
         "activities": ["Stakeholder interviews", "System architecture"]},
        {"phase": 2, "name": "Design Sprint", "duration_weeks": 3,
         "activities": ["UX research", "UI design"]},
        {"phase": 3, "name": "Sprint 1 - Core Platform", "duration_weeks": 4,
         "activities": ["Backend foundation", "Auth system"]},
    ]


class TestMethodologySection:
    def test_methodology_never_contains_bare_integers(self):
        final = {}
        _merge_system_sections(
            final,
            {"timeline_data": {"phases": _timeline_phases()}},
            {},
        )
        assert "methodology" in final
        phases = final["methodology"]["phases"]
        assert phases, "methodology must have phases"
        for phase in phases:
            assert isinstance(phase, str), f"phase must be a string, got {phase!r}"
            assert not phase.isdigit(), f"phase must not be a bare digit string: {phase!r}"
            assert len(phase) > 15, f"phase must be descriptive (>15 chars): {phase!r}"

    def test_methodology_phases_match_timeline_names(self):
        final = {}
        _merge_system_sections(
            final,
            {"timeline_data": {"phases": _timeline_phases()}},
            {},
        )
        joined = " ".join(final["methodology"]["phases"])
        assert "Discovery & Architecture" in joined
        assert "Design Sprint" in joined
        assert "Sprint 1 - Core Platform" in joined

    def test_methodology_skips_phases_without_names(self):
        final = {}
        _merge_system_sections(
            final,
            {"timeline_data": {"phases": [{"phase": 1}, {"phase": 2}]}},
            {},
        )
        assert "methodology" not in final
