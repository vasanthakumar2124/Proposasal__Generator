from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from app.schemas.proposal_schema import (
    ProposalRequest,
    ProposalResponse,
)

from app.graph.workflow import build_workflow

from app.services.generated_proposal_service import (
    save_generated_proposal,
    get_generated_proposals,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Proposal Generator"]
)


workflow = build_workflow()



@router.post(
    "/generate",
    response_model=ProposalResponse
)
async def generate_proposal(request: ProposalRequest):

    result = workflow.invoke(
        {
            "requirement": request.requirement
        }
    )


    await save_generated_proposal(
        {
            "requirement": request.requirement,
            **result
        }
    )


    proposal = result["proposal"]


    return ProposalResponse(
        proposal_id=proposal["proposal_id"],
        project_name=proposal["project_name"],
        generated_date=proposal["generated_date"],
        proposal=proposal["proposal_content"],
        pdf_file=result["pdf_file"]
    )



@router.get(
    "/history"
)
async def proposal_history():

    proposals = await get_generated_proposals()


    return {
        "status": "success",
        "count": len(proposals),
        "data": proposals
    }



@router.get("/download/{filename}")
async def download_pdf(filename:str):

    file_path = f"generated/{filename}"


    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )


    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )