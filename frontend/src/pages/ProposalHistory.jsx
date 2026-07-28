import { useEffect, useState } from "react";

import API from "../api/axios";


function ProposalHistory(){

    const [proposals,setProposals] = useState([]);



    const fetchHistory = async()=>{

        try{

            const response = await API.get(
                "/ai/history"
            );


            setProposals(
                response.data.data
            );


        }
        catch(error){

            console.log(error);

        }

    };



    useEffect(()=>{

        fetchHistory();

    },[]);



    return (

        <div>

            <h1>
                Proposal History
            </h1>


            {
                proposals.map(
                    (proposal)=>(
                        
                    <div key={proposal._id}>


                        <h3>
                        {
                          proposal.proposal.project_name
                        }
                        </h3>


                        <p>
                        Created:
                        {
                          new Date(
                            proposal.created_at
                          ).toLocaleDateString()
                        }
                        </p>


                        <button>
                            View Proposal
                        </button>


                    </div>

                    )
                )
            }


        </div>

    )

}


export default ProposalHistory;