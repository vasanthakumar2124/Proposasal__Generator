from fastapi import APIRouter, HTTPException

from app.schemas.proposal_schema import ProposalCreate
from app.services.proposal_service import (
    create_proposal,
    get_all_proposals,
    get_proposal,
    update_proposal,
    delete_proposal,
)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.post("/")
async def create(proposal: ProposalCreate):
    return await create_proposal(proposal)


@router.get("/")
async def get_all():
    return await get_all_proposals()


@router.get("/{proposal_id}")
async def get_one(proposal_id: str):
    proposal = await get_proposal(proposal_id)

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return proposal


@router.put("/{proposal_id}")
async def update(proposal_id: str, proposal: ProposalCreate):
    updated = await update_proposal(proposal_id, proposal)

    if updated == 0:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {"message": "Proposal updated successfully"}


@router.delete("/{proposal_id}")
async def delete(proposal_id: str):
    deleted = await delete_proposal(proposal_id)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {"message": "Proposal deleted successfully"}