import { useState } from "react";
import { useNavigate } from "react-router-dom";

import API from "../api/axios";


function GenerateProposal() {

    const [requirement, setRequirement] = useState("");

    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();



    const generateProposal = async () => {

        if (!requirement) {
            alert("Please enter requirement");
            return;
        }


        try {

            setLoading(true);


            const response = await API.post(
                "/ai/generate",
                {
                    requirement: requirement
                }
            );


            console.log(response.data);


            // send proposal data to result page

            navigate(
                "/result",
                {
                    state: response.data
                }
            );


        } catch(error) {

            console.log(error);

            alert("Proposal generation failed");

        }
        finally {

            setLoading(false);

        }

    };



    return (

        <div>

            <h1>
                AI Proposal Generator
            </h1>


            <textarea

                placeholder="Enter project requirement..."

                value={requirement}

                onChange={
                    (e)=>setRequirement(e.target.value)
                }

                rows="8"

                cols="50"

            />


            <br/>


            <button
                onClick={generateProposal}
                disabled={loading}
            >

            {
                loading
                ?
                "Generating..."
                :
                "Generate Proposal"
            }


            </button>


        </div>

    )

}


export default GenerateProposal;