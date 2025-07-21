import dspy

import chainlit as cl
from typing import Optional
import os
from dotenv import load_dotenv
from db_schema import Document, Article, Paragraph
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine.url import URL

# Load environment variables from .env file
load_dotenv()
api_token = os.getenv('IONOS_TOKEN')



# Database connection parameters
db_params = {
    'host': os.environ.get("DB_HOST", "db"),  
    'database': os.environ.get("DB_NAME", "default_df"),
    'username': os.environ.get("DB_USER", "default_user"),
    'password': os.environ.get("DB_PASSWORD", "default_password"),
    'port': '5432',
    'drivername': 'postgresql+psycopg2',
    "query": {}
}

def db_connect(db_params):
    """Create SQLAlchemy engine instance using db_params."""
    return create_engine(URL(**db_params))

def create_deals_table(engine):
    """Create tables defined in DeclarativeBase metadata."""
    DeclarativeBase.metadata.create_all(engine)

def db_session(db_params):
    """Create and return a new database session."""
    engine = db_connect(db_params)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# Initialize DB session and ensure vector extension is enabled
session = db_session(db_params)
session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
session.commit()

# Configure LLMs and embedder
llm_llama = dspy.LM(
    "openai/meta-llama/Llama-3.3-70B-Instruct",
    base_url="https://openai.inference.de-txl.ionos.com/v1",
    api_key=api_token,
)
embedder = dspy.Embedder(
    "openai/BAAI/bge-m3",
    api_base="https://openai.inference.de-txl.ionos.com/v1",
    api_key=api_token,
)
dspy.configure(lm=llm_llama)


# Define the signature for the legal RAG task
k=5
class LegalRAGSignature(dspy.Signature):
    """You are a helpful assistant. Use only the provided legal documents to answer user queries.Reference them when using them."""
    message_history: list[dict[str, str]] = dspy.InputField()
    sources: list[dict] = dspy.InputField()
    answer: str = dspy.OutputField()

# Initialize the predictor with the defined signature
predictor = dspy.Predict(LegalRAGSignature)


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Simple password authentication for Chainlit."""
    if (username, password) == ("test_user", "digitalservice"):
        return cl.User(
            identifier="test_user", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def start_chat():
    """Initialize message history on chat start."""
    cl.user_session.set("message_history", [])


async def show_stream(output_stream, text_elements: Optional[list[cl.Text]] = None):
    """Stream output to Chainlit message."""
    message_history = cl.user_session.get("message_history")
    msg = cl.Message(content="", elements=text_elements)
    output = None
    async for part in output_stream:
        try:
            if type(part) == dspy.Prediction or type(part) == tuple:
                output = part
            if isinstance(part, dspy.streaming.StreamResponse):
                await msg.stream_token(part.chunk)

        except Exception as e:
            print(e, "PART", part, "TYPE:", type(part))
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
    return output

@cl.on_message
async def main(message: cl.Message):
    """Main handler for incoming messages."""

    # Append to message history
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    # Embed the query from message history
    query_vector = embedder([str(message_history)])[0].tolist()

    # Retrieve top-k relevant documents
    relevant_laws = session.scalars(
        select(Document).order_by(Document.embedding.l2_distance(query_vector)).limit(k)
    ).all()
    sources = [{"title": r.title} for r in relevant_laws]
    # For each document, retrieve top-k relevant sections
    for i, relevant_law in enumerate(relevant_laws):
        uri = relevant_law.uri
        sources[i]["relevant_sections"] = session.scalars(
            select(Article)
            .where(Article.document_uri == uri)
            .order_by(Article.embedding.l2_distance(query_vector))
            .limit(k)
        ).all()
    
    # Create text elements for Chainlit for referencing
    text_elements = []
    for source_idx, source in enumerate(sources):
        source_name = source["title"]
        text_elements.append(
            cl.Text(
                content="\n\n".join([str(s) for s in source["relevant_sections"]]), 
                name=source_name, 
                display="side"
            )
        )
    print(text_elements)
    # Generate response using the predictor
    stream = dspy.streamify(predictor, stream_listeners=[dspy.streaming.StreamListener(signature_field_name="answer")],)
    answer = await show_stream(stream(message_history=message_history, sources=sources), text_elements=text_elements)
