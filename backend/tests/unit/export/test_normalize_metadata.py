from app.export.normalize import normalize_proposal

OBJECTID_PATTERN = r"^[0-9a-fA-F]{24}$"


class TestNormalizeMetadata:
    def test_metadata_constructed_from_db_fields(self):
        raw = {
            "title": "Bus Website",
            "organization_id": "org_abc",
            "created_at": "2026-07-30T10:00:00Z",
            "version": 1,
            "status": "draft",
        }
        result = normalize_proposal(raw)
        meta = result["metadata"]
        assert meta["proposal_title"] == "Bus Website"
        assert meta["company_name"] == ""
        assert meta["date"] == "2026-07-30"
        assert meta["version"] == "1"
        assert meta["status"] == "draft"

    def test_company_name_never_organization_id(self):
        raw = {
            "title": "Bus Website",
            "organization_id": "507f1f77bcf86cd799439011",
            "created_at": "2026-07-30T10:00:00Z",
        }
        result = normalize_proposal(raw)
        company_name = result["metadata"]["company_name"]
        assert not __import__("re").match(OBJECTID_PATTERN, company_name), (
            f"company_name leaked organization_id: {company_name!r}"
        )

    def test_company_logo_defaults_to_data_uri(self):
        raw = {"title": "Bus Website"}
        result = normalize_proposal(raw)
        logo = result["metadata"]["company_logo"]
        assert logo.startswith("data:image/")

    def test_company_logo_uses_explicit_value(self):
        raw = {"title": "Bus Website", "company_logo": "/tmp/custom.png"}
        result = normalize_proposal(raw)
        assert result["metadata"]["company_logo"].startswith("data:image/")

    def test_metadata_not_overwritten_when_already_present(self):
        raw = {
            "metadata": {
                "proposal_title": "Custom Title",
                "subtitle": "custom",
                "client_name": "Client",
                "company_name": "Company",
                "date": "2026-01-01",
                "version": "2.0",
                "status": "approved",
            },
            "title": "DB Title",
        }
        result = normalize_proposal(raw)
        meta = result["metadata"]
        assert meta["proposal_title"] == "Custom Title"
        assert meta["date"] == "2026-01-01"

    def test_metadata_uses_defaults_for_missing_fields(self):
        raw = {}
        result = normalize_proposal(raw)
        meta = result["metadata"]
        assert meta["proposal_title"] == "Proposal"
        assert meta["version"] == "1.0"
