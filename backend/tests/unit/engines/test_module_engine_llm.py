import sys; sys.path.insert(0, 'backend')
from app.engines.module_engine import ModuleEngine


class FakeLLM:
    def __init__(self, result):
        self.result = result

    def generate_json(self, prompt, **kwargs):
        return self.result


class TestModuleEngine:
    def setup_method(self):
        self.context = {
            "domain": "custom",
            "project_type": "web_app",
            "description": "Peer-to-peer car marketplace where users list used cars, search with filters, chat with sellers, and book test drives.",
            "project_domain_description": "Peer-to-peer car marketplace with listings, search, buyer/seller messaging",
            "core_features": ["car listings", "search filters", "chat", "test drive booking"],
        }

    def test_llm_modules_used_when_provided(self):
        llm = FakeLLM({"core_modules": [
            {"name": "Car Listing Management", "description": "Create, edit, and publish vehicle listings with photos and specs."},
            {"name": "Search & Filtering", "description": "Full-text and faceted search over listings with price, make, model filters."},
            {"name": "Buyer-Seller Messaging", "description": "In-app chat between buyers and sellers with negotiation threads."},
        ], "advanced_modules": [
            {"name": "Test Drive Booking", "description": "Scheduling test drives and seller availability."},
        ]})
        engine = ModuleEngine(llm)
        result = engine.run(self.context)
        assert result["module_source"] == "llm"
        names = [m["name"] for m in result["modules"]]
        assert "Car Listing Management" in names
        assert "POS System" not in names

    def test_llm_parse_error_falls_back_to_lookup(self):
        engine = ModuleEngine(FakeLLM({"_parse_error": "bad json"}))
        result = engine.run(self.context)
        assert result["module_source"] == "llm"
        assert result["module_count"] >= 1

    def test_llm_invalid_output_falls_back_to_lookup(self):
        engine = ModuleEngine(FakeLLM({"core_modules": [], "advanced_modules": []}))
        result = engine.run(self.context)
        assert result["module_count"] >= 1

    def test_no_llm_uses_lookup(self):
        engine = ModuleEngine()
        result = engine.run(self.context)
        assert result["module_source"] == "lookup"

    def test_validation_filters_junk_entries(self):
        llm = FakeLLM({"core_modules": [
            {"name": "X", "description": "too short"},
            {"name": "Valid Module", "description": "A real module with a proper project-specific description."},
            {"name": "Valid Module", "description": "duplicate name should be dropped"},
            "not a dict",
        ]})
        result = ModuleEngine(llm).run(self.context)
        names = [m["name"] for m in result["modules"]]
        assert names == ["Valid Module"]

    def test_no_description_falls_back_to_lookup(self):
        from app.engines.industry_engine import IndustryEngine
        ind = IndustryEngine().run({"domain": "retail"})
        engine = ModuleEngine(FakeLLM({"core_modules": []}))
        result = engine.run({"industry_data": ind})
        assert result["module_count"] >= 3
        assert result["module_source"] == "lookup"
