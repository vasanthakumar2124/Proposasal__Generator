import json

from app.rag.retriever import search_documents

from app.llm.prompts import RAG_FORMATTER_PROMPT

from app.llm.client import generate_response


class RAGAgent:


    def __init__(self):
        self.name = "RAG Agent"



    def create_search_query(self, requirement):

        query = f"""
        Find similar software proposals.

        Project:
        {requirement.get("project_name")}

        Domain:
        {requirement.get("domain")}

        Required areas:

        - Executive Summary
        - Features
        - Technology Stack
        - Timeline
        - Pricing

        """

        return query



    def run(self, requirement):

        # Step 1: Create search query

        query = self.create_search_query(
            requirement
        )


        # Step 2: Retrieve relevant documents from Qdrant

        documents = search_documents(
            query
        )


        # Step 3: Prepare retrieved context

        context = "\n\n".join(
            [
                doc["content"]
                for doc in documents
            ]
        )


        # Step 4: Format context using LLM

        prompt = RAG_FORMATTER_PROMPT.format(
            context=context
        )


        response = generate_response(
            prompt
        )


        # Step 5: Convert JSON string to Python dictionary

        try:

            formatted_context = json.loads(
                response
            )


        except json.JSONDecodeError:

            formatted_context = {
                "raw_context": response
            }



        # Step 6: Return structured RAG output

        return {

            "search_query": query,

            "retrieved_context": formatted_context

        }