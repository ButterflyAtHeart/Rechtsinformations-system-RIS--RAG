# Chainlit App for RIS RAG

This Chainlit app provides a conversational interface for german legal document search and question answering using Retrieval-Augmented Generation (RAG).

## Database
As a database 2500 german law and executive orders were downloaded from [here](https://testphase.rechtsinformationen.bund.de/). After that they were parsed and inserted into a postresql database.

## Models
- **LLMs:**
  - Llama-3 (via IONOS API)
- **Embedding Model:**
  - BGE-M3 (via IONOS API)

These models enable semantic search and natural language understanding for legal queries.

## Capabilities
- Secure user authentication
- Natural language queries over German legal documents
- References to relevant legal sources in responses
- Powered by LLMs and vector search

## Source Code
See the main application logic in [`Github`](https://github.com/ButterflyAtHeart/Rechtsinformations-system-RIS--RAG).
