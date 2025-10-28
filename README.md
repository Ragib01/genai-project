# RAG Application with Fine-Tuned Model

This project is a RAG (Retrieval-Augmented Generation) application that utilizes a fine-tuned model named "qwen3-4b-customer-support".

## Setup

### 1. Environment Variables

Copy the `.env.example` file to `.env` and update the values according to your setup:

```bash
cp .env.example .env
```

Required environment variables:
- `POSTGRES_DB_URL`: PostgreSQL database connection URL (e.g., `postgresql://user:password@localhost:5432/dbname`)
- `LM_STUDIO_API_KEY`: API key for LM Studio (default: `lm-studio`)
- `LM_STUDIO_BASE_URL`: Base URL for LM Studio API (default: `http://localhost:1234/v1`)
- `RAG_AGENT_MODEL`: Fine-tuned model name (default: `qwen3-4b-customer-support`)

### 2. Dependencies

This project uses the `agno` package.

To install the required packages, run the following command:

```bash
pip install -r requirements.txt
```

### 3. Vectorization

Before running the main application, you need to vectorize your documents:

```bash
python vectorizer.py
```

This will process the documents in the `documents/` folder and create embeddings in the vector database.

### 4. Running the Application

To run the application, execute the following command:

```bash
python main.py
```

## API Documentation

The API documentation is available at the following URL:

[http://localhost:7777](API documentation)


