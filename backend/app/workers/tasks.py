import logging

from app.workers.celery_app import celery_app
from app.workers.worker_loop import run_async

logger = logging.getLogger("proposalcraft.workers.tasks")


@celery_app.task(name="generate_proposal", bind=True, max_retries=1)
def generate_proposal_task(
    self,
    doc_id: str,
    client_input: str,
    org_id: str,
    user_id: str,
    domain: str | None = None,
    project_type: str | None = None,
) -> dict:
    logger.info("Task started: proposal %s (user %s)", doc_id, user_id)
    try:
        return run_async(_generate(doc_id, client_input, org_id, user_id, domain, project_type))
    except Exception as e:
        logger.error("Task failed for proposal %s: %s", doc_id, e, exc_info=True)
        raise self.retry(exc=e, countdown=30) from e


async def _generate(
    doc_id: str,
    client_input: str,
    org_id: str,
    user_id: str,
    domain: str | None,
    project_type: str | None,
) -> dict:
    from app.infrastructure.database.mongodb import connect_to_mongodb, ensure_indexes
    from app.services.generated_proposal_service import GeneratedProposalService

    await connect_to_mongodb()
    await ensure_indexes()
    svc = GeneratedProposalService()
    return await svc.run_and_finalize(
        doc_id=doc_id,
        client_input=client_input,
        org_id=org_id,
        user_id=user_id,
        domain=domain,
        project_type=project_type,
    )
