import json
import logging
from datetime import datetime, timezone

from bson import ObjectId

from app.models.generated_proposal_model import generated_proposal_collection

logger = logging.getLogger("proposalcraft.generated_proposal_service")


class GeneratedProposalService:
    async def generate(
        self,
        client_input: str,
        org_id: str,
        user_id: str,
        domain: str | None = None,
        project_type: str | None = None,
    ) -> dict:
        from app.graph.workflow import proposal_workflow

        initial_state = {
            "raw_client_input": client_input,
            "domain": domain,
            "project_type": project_type,
            "requirements": None,
            "rag_context": None,
            "business_context": None,
            "proposal_draft": None,
            "review": None,
            "final_proposal": None,
            "error": None,
        }

        try:
            final_state = await proposal_workflow.ainvoke(initial_state)
        except Exception as e:
            logger.error("Workflow failed: %s", e, exc_info=True)
            final_state = {**initial_state, "error": str(e)}

        proposal_content = final_state.get("final_proposal") or final_state.get("proposal_draft") or {}
        reqs = final_state.get("requirements") or {}
        error = final_state.get("error")
        business_context = final_state.get("business_context")

        rubric_check = None
        if isinstance(proposal_content, dict):
            try:
                from app.agents.rubric_checker import check_proposal

                rubric_result = check_proposal(proposal_content, business_context)
                rubric_check = {
                    "passed": rubric_result.passed,
                    "missing_sections": rubric_result.missing_sections,
                    "placeholder_sections": rubric_result.placeholder_sections,
                    "number_mismatches": rubric_result.number_mismatches,
                    "word_count_issues": rubric_result.word_count_issues,
                }
                logger.info("Rubric check result: %s", rubric_result)
            except Exception as e:
                logger.warning("Rubric check failed: %s", e, exc_info=True)

        title = reqs.get("project_name", "Untitled Proposal") if isinstance(reqs, dict) else "Untitled Proposal"

        company_name = ""
        company_logo = ""
        try:
            from app.services.organization_service import OrganizationService

            org = await OrganizationService().get_organization(org_id)
            company_name = getattr(org, "name", "") or ""
            branding = getattr(org, "branding", None)
            company_logo = getattr(branding, "logo_url", "") or ""
        except Exception as e:
            logger.warning("Could not resolve organization name: %s", e)

        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        new_id = ObjectId()
        doc = {
            "_id": new_id,
            "title": title,
            "client_input": client_input,
            "sections": proposal_content if isinstance(proposal_content, dict) else {"content": str(proposal_content)},
            "requirements": reqs,
            "business_context": business_context,
            "review": final_state.get("review"),
            "status": "draft" if not error else "error",
            "error": error,
            "organization_id": org_id,
            "company_name": company_name,
            "company_logo": company_logo,
            "proposal_id": f"PROP-{date_str}-{str(new_id)[-4:].upper()}",
            "created_by": user_id,
            "version": 1,
            "ai_generated": True,
            "generation_metadata": {"rubric_check": rubric_check},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await generated_proposal_collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        logger.info("Generated proposal '%s' (%s) as %s", title, doc["_id"], doc["proposal_id"])
        return doc

    async def list_proposals(self, org_id: str) -> list[dict]:
        cursor = generated_proposal_collection.find(
            {"organization_id": org_id}
        ).sort("created_at", -1)
        proposals = []
        async for p in cursor:
            p["_id"] = str(p["_id"])
            proposals.append(p)
        return proposals

    async def get_proposal(self, proposal_id: str) -> dict | None:
        from bson import ObjectId
        p = await generated_proposal_collection.find_one({"_id": ObjectId(proposal_id)})
        if p:
            p["_id"] = str(p["_id"])
        return p

    async def delete_proposal(self, proposal_id: str) -> bool:
        result = await generated_proposal_collection.delete_one({"_id": ObjectId(proposal_id)})
        return result.deleted_count > 0
