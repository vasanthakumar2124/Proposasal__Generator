from app.engines.team_engine import TeamEngine


class TestTeamEngineTimelineScaling:
    def setup_method(self):
        self.engine = TeamEngine()

    def _run(self, module_count, total_weeks, complexity="medium"):
        phases = [{"name": f"P{i}", "duration_weeks": 1} for i in range(max(total_weeks, 1))]
        return self.engine.run({
            "module_data": {"modules": [{"name": f"M{i}"} for i in range(module_count)]},
            "industry_data": {"complexity": complexity},
            "timeline_data": {"phases": phases},
        })

    def test_short_project_stays_small(self):
        result = self._run(module_count=4, total_weeks=8)
        assert result["team_scale"] == "small"

    def test_long_small_project_bumps_to_medium(self):
        result = self._run(module_count=4, total_weeks=20)
        assert result["team_scale"] == "medium"

    def test_long_medium_project_bumps_to_large(self):
        result = self._run(module_count=8, total_weeks=26)
        assert result["team_scale"] == "large"

    def test_very_long_small_bumps_to_large(self):
        result = self._run(module_count=3, total_weeks=30)
        assert result["team_scale"] == "medium"
