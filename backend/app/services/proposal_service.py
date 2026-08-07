from datetime import datetime, timezone
from typing import Optional

from app.config.constants import ProposalStatus
from app.domain.entities.proposal import Proposal
from app.domain.events import (
    DomainEvent,
    EVENT_PROPOSAL_CREATED,
    EVENT_PROPOSAL_STATUS_CHANGED,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import ProposalRepository
from app.infrastructure.database.mongo_repositories.proposal_repo import MongoProposalRepository
from app.infrastructure.log.audit import create_audit_log
from app.infrastructure.events.bus import event_bus
from app.lifecycle.machine import transition
from app.services.proposal_version_service import ProposalVersionService


class ProposalService:
    def __init__(self, proposal_repo: Optional[ProposalRepository] = None) -> None:
        self.proposal_repo = proposal_repo or MongoProposalRepository()
        self.version_service = ProposalVersionService()

    async def create_proposal(self, data: dict, org_id: str, user_id: str) -> Proposal:
        proposal = Proposal(organization_id=org_id, created_by=user_id, **data)
        proposal = await self.proposal_repo.create(proposal)
        await create_audit_log(org_id, user_id, "proposal.create", "proposal", proposal.id)
        await event_bus.publish(
            DomainEvent(
                event_type=EVENT_PROPOSAL_CREATED,
                organization_id=org_id,
                user_id=user_id,
                resource_type="proposal",
                resource_id=proposal.id,
                payload={"title": proposal.title},
            )
        )
        return proposal

    async def get_proposal(self, proposal_id: str) -> Proposal:
        proposal = await self.proposal_repo.get_by_id(proposal_id)
        if not proposal:
            raise EntityNotFoundError("Proposal", proposal_id)
        return proposal

    async def update_proposal(self, proposal_id: str, data: dict) -> Proposal:
        proposal = await self.get_proposal(proposal_id)
        for key, value in data.items():
            if value is not None and hasattr(proposal, key):
                setattr(proposal, key, value)
        proposal.updated_at = datetime.now(timezone.utc)
        updated = await self.proposal_repo.update(proposal)
        await self.version_service.create_version(
            proposal_id,
            proposal.organization_id,
            proposal.created_by,
            title=proposal.title,
            sections=proposal.sections,
            note="edited",
        )
        return updated

    async def transition_status(self, proposal_id: str, target: str, user_id: str) -> Proposal:
        """Move a proposal through the lifecycle state machine, recording
        each transition as an activity event."""
        proposal = await self.get_proposal(proposal_id)
        current = proposal.status.value if hasattr(proposal.status, "value") else str(proposal.status)
        transition(current, target)
        proposal.status = ProposalStatus(target)
        if target == "approved":
            proposal.approved_by = user_id
        proposal.updated_at = datetime.now(timezone.utc)
        updated = await self.proposal_repo.update(proposal)
        await event_bus.publish(
            DomainEvent(
                event_type=EVENT_PROPOSAL_STATUS_CHANGED,
                organization_id=proposal.organization_id,
                user_id=user_id,
                resource_type="proposal",
                resource_id=proposal_id,
                payload={"from": current, "to": target},
            )
        )
        return updated

    async def delete_proposal(self, proposal_id: str) -> None:
        await self.get_proposal(proposal_id)
        await self.proposal_repo.delete(proposal_id)

    async def list_proposals(self, org_id: str, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> list[Proposal]:
        return await self.proposal_repo.get_by_organization(org_id, skip=skip, limit=limit, status=status)

    async def update_section(self, proposal_id: str, section_name: str, content: dict) -> Proposal:
        proposal = await self.get_proposal(proposal_id)
        proposal.sections[section_name] = content
        proposal.updated_at = datetime.now(timezone.utc)
        updated = await self.proposal_repo.update(proposal)
        await self.version_service.create_version(
            proposal_id,
            proposal.organization_id,
            proposal.created_by,
            title=proposal.title,
            sections=proposal.sections,
            note=f"edited section: {section_name}",
        )
        return updated
