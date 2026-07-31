RAG_SYSTEM_PROMPT = """You are a RAG context formatter for proposal generation.
Your job is to organize retrieved knowledge base chunks into a concise, relevant context block
that will help a proposal writer generate accurate, compelling content."""

RAG_CONTEXT_TEMPLATE = """Organize the following retrieved knowledge base chunks into a structured context block.
Focus on relevance to the project domain and features. Output valid JSON:

{{
  "domain_insights": ["relevant domain-specific insights"],
  "technical_insights": ["relevant technical information"],
  "best_practices": ["relevant best practices"],
  "relevant_case_studies": ["brief relevant examples"],
  "key_considerations": ["important notes for this proposal"]
}}

Project domain: {domain}
Project description: {description}

Retrieved chunks:
{rag_chunks}
"""
