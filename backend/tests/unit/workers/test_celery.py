from app.workers.celery_app import celery_app
from app.workers.tasks import generate_proposal_task


def test_celery_app_registers_generate_proposal_task():
    assert "generate_proposal" in celery_app.tasks
    assert celery_app.conf.task_default_queue == "proposalcraft"


def test_generate_proposal_task_registered():
    assert generate_proposal_task.name == "generate_proposal"
