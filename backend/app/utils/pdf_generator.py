from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image
)
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

from datetime import datetime
import os
import re


def create_pdf(
    proposal_text,
    output_path,
    requirement,
    prepared_by="AI Proposal Generator"
):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    # ----------------------------------------------------
    # Requirement Data
    # ----------------------------------------------------

    project_name = requirement.get(
        "project_name",
        "Software Project"
    )

    client_name = requirement.get(
        "client_name",
        "Confidential Client"
    )

    company_name = requirement.get(
        "company_name",
        ""
    )

    proposal_version = requirement.get(
        "proposal_version",
        "1.0"
    )

    # ----------------------------------------------------
    # Cover Page Styles
    # ----------------------------------------------------

    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=28,
        alignment=TA_CENTER,
        textColor=HexColor("#1F3A5F"),
        spaceAfter=25,
    )

    cover_heading = ParagraphStyle(
        "CoverHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=TA_CENTER,
        textColor=HexColor("#666666"),
        spaceAfter=5,
    )

    cover_value = ParagraphStyle(
        "CoverValue",
        parent=styles["Normal"],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=HexColor("#000000"),
        spaceAfter=18,
    )

    # ----------------------------------------------------
    # Proposal Styles
    # ----------------------------------------------------

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    title.textColor = HexColor("#0B5394")

    h2 = styles["Heading2"]
    h2.textColor = HexColor("#1F4E79")

    h3 = styles["Heading3"]

    normal = styles["BodyText"]

    # ----------------------------------------------------
    # Proposal ID & Date
    # ----------------------------------------------------

    today = datetime.now()

    proposal_id = f"PROP-{today.strftime('%Y%m%d')}-001"

    proposal_date = today.strftime("%d %B %Y")

    # ----------------------------------------------------
    # Story
    # ----------------------------------------------------

    story = []

    # ====================================================
    # COVER PAGE
    # ====================================================

    story.append(Spacer(1, 40))

    # Company Logo (Optional)
    logo_path = "app/assets/logo.png"

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=100,
            height=100
        )
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 20))

    # Proposal Heading

    story.append(
        Paragraph(
            "PROPOSAL",
            cover_title
        )
    )

    story.append(
        Paragraph(
            project_name,
            cover_value
        )
    )

    story.append(Spacer(1, 25))

    # Prepared For

    story.append(
        Paragraph(
            "<b>Prepared For</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            client_name,
            cover_value
        )
    )

    # Prepared By

    story.append(
        Paragraph(
            "<b>Prepared By</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            prepared_by,
            cover_value
        )
    )

    # Proposal ID

    story.append(
        Paragraph(
            "<b>Proposal ID</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            proposal_id,
            cover_value
        )
    )

    # Date

    story.append(
        Paragraph(
            "<b>Date</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            proposal_date,
            cover_value
        )
    )

    # Version

    story.append(
        Paragraph(
            "<b>Version</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            f"Version {proposal_version}",
            cover_value
        )
    )

    story.append(Spacer(1, 20))

    # Confidential

    story.append(
        Paragraph(
            "<b>CONFIDENTIAL</b>",
            cover_heading
        )
    )

    story.append(
        Paragraph(
            "This proposal contains confidential business information intended only for the recipient.",
            normal
        )
    )

    # Next Page

    story.append(PageBreak())

    # ====================================================
    # EXISTING PROPOSAL CONTENT
    # ====================================================

    for line in proposal_text.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 12))
            continue

        # Heading 1
        if line.startswith("# "):

            heading = line.replace("# ", "")
            heading = re.sub(r"^\d+\.\s*", "", heading)

            story.append(
                Paragraph(
                    heading,
                    title
                )
            )

        # Heading 2
        elif line.startswith("## "):

            heading = line.replace("## ", "")
            heading = re.sub(r"^\d+\.\s*", "", heading)

            story.append(
                Paragraph(
                    heading,
                    h2
                )
            )

        # Heading 3
        elif line.startswith("### "):

            heading = line.replace("### ", "")
            heading = re.sub(r"^\d+\.\s*", "", heading)

            story.append(
                Paragraph(
                    heading,
                    h3
                )
            )

        # Horizontal Line
        elif line == "---":

            story.append(
                Paragraph(
                    "<font color='grey'>__________________________________________________</font>",
                    normal
                )
            )

        # Bullet Points
        elif line.startswith("- "):

            story.append(
                Paragraph(
                    f"• {line[2:]}",
                    normal
                )
            )

        # Bold Field
        elif line.startswith("**") and ":" in line:

            text = line.replace("**", "")

            parts = text.split(":", 1)

            if len(parts) == 2:

                story.append(
                    Paragraph(
                        f"<b>{parts[0]}:</b> {parts[1]}",
                        normal
                    )
                )

            else:

                story.append(
                    Paragraph(
                        text,
                        normal
                    )
                )

        # Normal Paragraph
        else:

            story.append(
                Paragraph(
                    line,
                    normal
                )
            )

        story.append(Spacer(1, 8))

    doc.build(story)

    return output_path