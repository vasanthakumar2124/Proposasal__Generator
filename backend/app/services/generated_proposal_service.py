from datetime import datetime

from app.models.generated_proposal_model import (
    generated_proposal_collection,
)



async def save_generated_proposal(data: dict):

    data["created_at"] = datetime.utcnow()

    result = await generated_proposal_collection.insert_one(data)

    return str(result.inserted_id)



async def get_generated_proposals():

    proposals = []

    cursor = generated_proposal_collection.find().sort(
        "created_at",
        -1
    )


    async for proposal in cursor:

        proposal["_id"] = str(proposal["_id"])

        proposals.append(proposal)


    return proposals