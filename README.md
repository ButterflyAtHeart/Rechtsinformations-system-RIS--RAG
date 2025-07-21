# Large SQL File Notice

The `init.sql` file required for database initialization is **not included** in this repository due to its large size (~700 MB).

Please download `init.sql` from the provided cloud storage link and place it in the project root directory:

- [Download init.sql](YOUR_CLOUD_STORAGE_LINK_HERE)

After downloading, you can start the application as described below.

---

# RIS RAG

RIS RAG is a Retrieval-Augmented Generation (RAG) application for legal document search and question answering, leveraging PostgreSQL with pgvector for vector search and LLMs for natural language understanding.

## Features
- Downloads and parses German legal documents from the  [official API](https://testphase.rechtsinformationen.bund.de)
- Stores documents, articles, and paragraphs in a PostgreSQL database with vector embeddings
- Uses LLMs (Llama-3) and embedding models via IONOS API
- Provides a Chainlit-based chat interface for legal Q&A
- Dockerized setup for easy deployment

## Project Structure
- `app.py`: Main application logic, Chainlit chat, database connection, LLM configuration
- `download_data.ipynb`: Notebook for downloading, parsing, and inserting legal data into the database
- `db_schema.py`: SQLAlchemy models for Document, Article, Paragraph
- `init.sql`: SQL initialization script for database tables
- `docker-compose.yml` & `Dockerfile`: Container setup for app and database
- `requirements.txt`: Python dependencies
- `v1/legislation/eli/`, `bgbl/`, etc.: Directory structure for downloaded legal documents

## Setup & Usage

### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Environment Variables
Create a `.env` file with the following variables:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
IONOS_TOKEN=your_ionos_api_token
```

### Start the Application
1. Build and start containers:
   ```bash
   docker-compose up --build
   ```
2. Access the Chainlit chat interface at [http://localhost:8000](http://localhost:8000)

### Data Download & Database Initialization
- Use `download_data.ipynb` to fetch and insert legal documents into the database. **or** load in the init.sql as it contains all information.
- The notebook covers:
  - Downloading ZIP files from the API
  - Parsing XML files
  - Inserting data into PostgreSQL
  - Calculating vector embeddings

## API & Models
- LLMs and embedding models are accessed via the IONOS API (see `app.py` and notebook for usage).
- Supported models: Llama-3, BGE-M3 embeddings

## License
This project is for research and educational purposes. See individual files for license details.
