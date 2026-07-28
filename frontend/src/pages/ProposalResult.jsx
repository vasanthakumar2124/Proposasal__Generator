import { useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown";

function ProposalResult() {

    const location = useLocation();
    const proposal = location.state;

    if (!proposal) {
        return <h2>No proposal found.</h2>;
    }

    const downloadPDF = () => {
        if (!proposal.pdf_file) return;

        window.open(
            `http://localhost:8000/ai/download/${proposal.pdf_file.split("/").pop()}`
        );
    };

    return (
        <div
            style={{
                maxWidth: "900px",
                margin: "40px auto",
                padding: "20px",
                fontFamily: "Arial"
            }}
        >
            <h1>Generated Proposal</h1>

            <h2>{proposal.project_name}</h2>

            <p>
                <strong>Generated Date:</strong> {proposal.generated_date}
            </p>

            <hr />

            <ReactMarkdown>
                {proposal.proposal_content}
            </ReactMarkdown>

            <br />

            {proposal.pdf_file && (
                <button onClick={downloadPDF}>
                    Download PDF
                </button>
            )}
        </div>
    );
}

export default ProposalResult;