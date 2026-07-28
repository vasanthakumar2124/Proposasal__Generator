from app.models.proposal_model import proposal_collection
from app.schemas.proposal_schema import ProposalCreate
from bson import ObjectId


async def create_proposal(proposal: ProposalCreate):
    proposal_data = proposal.model_dump()

    result = await proposal_collection.insert_one(proposal_data)

    proposal_data["_id"] = str(result.inserted_id)

    return proposal_data


async def get_all_proposals():
    proposals = []

    async for proposal in proposal_collection.find():
        proposal["_id"] = str(proposal["_id"])
        proposals.append(proposal)

    return proposals


async def get_proposal(proposal_id: str):
    proposal = await proposal_collection.find_one(
        {"_id": ObjectId(proposal_id)}
    )

    if proposal:
        proposal["_id"] = str(proposal["_id"])

    return proposal


async def update_proposal(
    proposal_id: str,
    proposal: ProposalCreate
):
    result = await proposal_collection.update_one(
        {"_id": ObjectId(proposal_id)},
        {"$set": proposal.model_dump()}
    )

    return result.modified_count


async def delete_proposal(proposal_id: str):
    result = await proposal_collection.delete_one(
        {"_id": ObjectId(proposal_id)}
    )

    return result.deleted_count