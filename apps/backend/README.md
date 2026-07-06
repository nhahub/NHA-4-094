# Document Upload & Ingestion Pipeline (NHA-4-094 Backend)

This is the document ingestion pipeline backend for the NHA-4-094 AI Study Platform, an AI-powered educational assistant. It validates, parses, chunks, and embeds uploaded PDF files, storing metadata in PostgreSQL and chunk vectors in pgvector.

---

## Technical Stack & Key Decisions

- **Framework**: FastAPI (using standard ASGI entry point and routes).
- **Supabase**: Uses the official Python client (`supabase` package) for database operations (Postgrest) and PDF storage (Supabase Storage). No complex SQLAlchemy/Alembic ORMs are used.
- **Asynchronous Processing**: FastAPI's built-in `BackgroundTasks` executes document parsing, chunking, and embedding generation out-of-band to prevent blocking client requests.
- **Embeddings**: Uses **Cloudflare Workers AI BGE-M3** (`@cf/baai/bge-m3`) executing on Cloudflare's Edge. It produces **1024-dimensional** vectors.
- **pgvector**: Stores text chunks alongside 1024-dimensional embeddings, with an HNSW cosine similarity index to support fast semantic search.

---

## File Structure

```text
apps/backend/
├── app/
│   ├── api/v1/documents.py        # PDF Upload & Ingestion Status endpoints
│   ├── core/config.py             # Environment configurations
│   ├── db/
│   │   ├── migrations/
│   │   │   └── 001_init_documents.sql # PG Schema setup for documents + chunks + pgvector
│   │   ├── repositories/
│   │   │   ├── document_repository.py # Document DB CRUD functions
│   │   │   └── chunk_repository.py    # Chunk DB CRUD functions
│   │   └── supabase_client.py     # Initialized Supabase Client
│   ├── schemas/document_schema.py # Pydantic schemas for requests/responses
│   ├── services/document_service.py # Orchestrates file upload flow and checks duplicates
│   ├── workers/document_worker.py # Background task worker wrapper
│   ├── ai_system/
│   │   ├── providers/
│   │   │   └── embedding_client.py # Local sentence-transformers client
│   │   └── ingestion/
│   │       ├── document_validator.py # Validates size, mime-type, magic bytes (%PDF)
│   │       ├── pdf_parser.py       # Extracts page-by-page text using PyPDF
│   │       ├── cleaner.py          # Cleans whitespace and newlines, preserving headings
│   │       ├── chunker.py          # Paragraph-aware character chunker with overlap
│   │       ├── metadata_generator.py # Enriches chunk database rows with contextual info
│   │       └── ingestion_pipeline.py # Linear orchestration (parsing -> chunking -> embedding)
│   └── main.py                    # Root FastAPI Entrypoint
└── tests/
    ├── unit/                      # Unit tests (cleaner, chunker, validator)
    └── integration/               # Integration tests (mocked endpoints and flows)
```

---

## Ingestion Pipeline Flow

```mermaid
graph TD
    A[POST /upload] --> B[Validate PDF extension, size, magic bytes]
    B --> C[Compute SHA256 file hash]
    C --> D{Check duplicate in DB?}
    D -- Yes --> E[Return existing ID & Status]
    D -- No --> F[Create Document row in DB: upload_status = 'uploaded']
    F --> G[Upload raw PDF to Supabase Storage]
    G --> H[Update DB storage_path: upload_status = 'stored']
    H --> I[Trigger BackgroundTask]
    I --> J[Return HTTP 202 Accepted]
    
    subgraph Background Tasks
        K[Download PDF bytes from Storage] --> L[Set status = 'parsing']
        L --> M[Extract text page-by-page]
        M --> N[Set status = 'chunking']
        N --> O[Clean text & split into paragraph-aware chunks]
        O --> P[Set status = 'embedding']
        P --> Q[Generate chunk vectors with sentence-transformers]
        Q --> R[Batch insert chunks + vectors into pgvector]
        R --> S[Set status = 'ready']
        M -- Error --> T[Set status = 'failed']
    end
```

---

## Database Schema (PostgreSQL + pgvector)

Ensure your database runs the SQL script under `app/db/migrations/001_init_documents.sql`:
- **Uniqueness constraint**: `UNIQUE (user_id, file_hash)` ensures users cannot upload duplicate files.
- **pgvector column**: `embedding vector(1024)` matches the dimension of the default embedding model (`@cf/baai/bge-m3`).
- **Semantic index**: Uses an HNSW cosine similarity index for fast similarity queries.

> [!WARNING]
> If you change the embedding model name (`EMBEDDING_MODEL_NAME`) to a model that outputs a different number of dimensions (e.g. OpenAI models at 1536), you **MUST** update `vector(1024)` in `001_init_documents.sql` to match.

---

## API Endpoints

### 1. Upload Document
* **Endpoint**: `POST /api/v1/documents/upload`
* **Format**: `multipart/form-data`
* **Field**: `file` (PDF file)
* **Response (New)**:
  ```json
  {
    "document_id": "835c1ba3-500b-4b13-8a02-ef681b93f0b2",
    "status": "processing",
    "message": "Document uploaded successfully and is being processed."
  }
  ```
* **Response (Duplicate)**:
  ```json
  {
    "document_id": "835c1ba3-500b-4b13-8a02-ef681b93f0b2",
    "status": "ready",
    "message": "Document already uploaded."
  }
  ```

### 2. Poll Ingestion Status
* **Endpoint**: `GET /api/v1/documents/{document_id}/status`
* **Response**:
  ```json
  {
    "document_id": "835c1ba3-500b-4b13-8a02-ef681b93f0b2",
    "status": "ready",
    "page_count": 24,
    "chunk_count": 92,
    "error_message": null
  }
  ```

---

## Supabase Project Setup & Connection

Follow these step-by-step instructions to configure your live Supabase project.

### 1. Create a Supabase Project
- Log in to the [Supabase Dashboard](https://supabase.com).
- Click **New Project**, select your organization, and configure the project name, database password, and region.
- Wait for the project database to spin up.

### 2. Enable pgvector and uuid-ossp Extensions
- Go to the **SQL Editor** in the left sidebar of your Supabase dashboard.
- Create a new query and run the following command to enable the required extensions:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  CREATE EXTENSION IF NOT EXISTS vector;
  ```
- Alternatively, you can enable them in **Database -> Extensions** in the Supabase UI.

### 3. Run Migrations Manually in Supabase SQL Editor
- Open the SQL migration file [001_init_documents.sql](file:///c:/Users/omara/OneDrive/Desktop/Machine%20Leraning%20DEPI%20/Mega%20Project/NHA-4-094/apps/backend/app/db/migrations/001_init_documents.sql).
- Copy the entire SQL content of that migration file.
- Paste it into the Supabase **SQL Editor** and click **Run**. This creates the `documents` and `document_chunks` tables with the required unique constraints and the HNSW index on the embedding field.

### 4. Create the Private Storage Bucket `study-documents`
- In the left sidebar of your Supabase dashboard, click on **Storage**.
- Click **New Bucket**.
- Set the Bucket Name to exactly: `study-documents`.
- Toggle the bucket settings to make it **Private** (do not toggle public access). This ensures raw PDFs are stored securely and require authorized backend requests to read.
- Click **Save**.

### 5. Configure `.env`
- In the `apps/backend` root, rename `.env.example` to `.env` or create a new `.env` file.
- Fill in the values from your Supabase Dashboard settings (**Project Settings -> API**):
  - `SUPABASE_URL`: The Project URL (e.g. `https://your-project-id.supabase.co`).
  - `SUPABASE_SERVICE_ROLE_KEY`: The secret service role key (labeled `service_role` / `secret` key). This key bypasses Row Level Security (RLS) to allow the ingestion pipeline to insert data.
  - `SUPABASE_STORAGE_BUCKET`: `study-documents`
  - `MAX_UPLOAD_SIZE_MB`: `10`
  - `EMBEDDING_MODEL_NAME`: `all-MiniLM-L6-v2`

### 6. Verify Connection
Run the connection checker script to verify your credentials, database tables, and storage buckets:
```bash
python scripts/check_supabase_connection.py
```
A successful connection output will look like this:
```text
============================================================
          SUPABASE LIVE CONNECTION & SCHEMA CHECKER
============================================================
SUPABASE_URL: https://your-project-id.supabase.co
SUPABASE_STORAGE_BUCKET: study-documents
EMBEDDING_MODEL_NAME: all-MiniLM-L6-v2
...
[1/4] Connecting to Supabase...
 -> SUCCESS: Supabase client successfully initialized.

[2/4] Checking 'documents' table exists...
 -> SUCCESS: 'documents' table is reachable in the database.

[3/4] Checking 'document_chunks' table exists...
 -> SUCCESS: 'document_chunks' table is reachable in the database.

[4/4] Checking storage bucket 'study-documents' exists...
 -> SUCCESS: Storage bucket 'study-documents' exists and is accessible.

============================================================
CONGRATULATIONS: Backend is successfully connected to Supabase!
============================================================
```

---

## Local Development & Testing

### 1. Run Tests
Ensure dependencies are installed and run the test suite:
```bash
python -m pytest tests/
```

### 2. Start the Server
Run the local FastAPI server using Uvicorn:
```bash
python -m uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`. You can inspect the interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 3. Test Ingestion via Swagger UI
- Open a web browser and go to `http://localhost:8000/docs`.
- Click on the `POST /api/v1/documents/upload` endpoint.
- Click **Try it out**.
- Click **Choose File** under the `file` field, and select a valid PDF file.
- Click **Execute**.
- Under the response body, you will see a success message:
  ```json
  {
    "document_id": "uuid-value",
    "status": "processing",
    "message": "Document uploaded successfully and is being processed."
  }
  ```
- Copy the returned `document_id`.
- Click on the `GET /api/v1/documents/{document_id}/status` endpoint.
- Click **Try it out**.
- Paste your `document_id` into the `document_id` field.
- Click **Execute**.
- If the background worker has finished, you will see:
  ```json
  {
    "document_id": "uuid-value",
    "status": "ready",
    "page_count": 5,
    "chunk_count": 14,
    "error_message": null
  }
  ```

---

## Live Table Verification in Supabase Dashboard
After uploading a document and seeing its status change to `ready`, you can verify the results inside the Supabase project:
- **Storage**: Go to **Storage -> study-documents** and verify that the PDF has been saved at `users/00000000-0000-0000-0000-000000000000/documents/{document_id}/{filename}`.
- **Documents Table**: Check the `documents` table in **Table Editor** to see the metadata row status updated to `ready`, with the correct page count and chunk count.
- **Document Chunks Table**: Check the `document_chunks` table to see all parsed text chunks, page starts, page ends, chunk metadata, and their 1024-dimensional `embedding` vectors.

---

## Supabase Shared Teammate Project Integration & Deployment Details

The integration of the FastAPI backend with the shared Supabase project ref `fkslyoxceczyhfhfldms` has been successfully completed. Below are the key deployment rules and architectural constraints:

### 1. Database Schema Migrations
- **Applied Migrations**:
  - `001_init_documents.sql`: Configures pgvector and initializes the `documents` and `document_chunks` tables.
  - `002_memory_personalization.sql`: Initializes tables for personalized memory (e.g. `chat_sessions`, `messages`, `memory_items`, `user_learning_profiles`, `planner_context`, etc.).
  - `004_memory_enhancements.sql`: Adds tables/views for learning schedules, mistake tracking, and evolved persona history.
- **Skipped Migrations**:
  - `003_update_embedding_dimension.sql`: **Skipped in production**. Because the target Supabase project database was empty, migrations were run cleanly from scratch. Therefore, the base table `document_chunks` was directly initialized with `vector(1024)` in `001_init_documents.sql`, rendering the destructive migration `003` redundant and skipped.
- **Embedding Vectors**: Hardcoded to `vector(1024)` to match the Cloudflare Workers AI BGE-M3 model (`@cf/baai/bge-m3`).

### 2. Private Storage Buckets
- The `study-documents` bucket is configured as a **private** bucket in Supabase Storage.
- Download/upload links are signed or generated with server-side authorization.

### 3. Server-side service_role Authority
- The backend utilizes the `SUPABASE_SERVICE_ROLE_KEY` to initialize its client. This grants the ingestion workers authority to read/write records and bypass Row-Level Security (RLS) constraints.
- **Security Constraint**: The `service_role` key must **never** be exposed in client code or frontend static assets. The client/frontend communicates exclusively with the backend via REST API using a mock or JWT user identifier.

### 4. Required Deployment Environment Variables (Backend)

Ensure your host environment defines these parameters:
```bash
# Supabase settings
SUPABASE_URL=https://fkslyoxceczyhfhfldms.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key  # Backend-only secret
SUPABASE_STORAGE_BUCKET=study-documents
DATABASE_URL=postgresql://postgres.fkslyoxceczyhfhfldms:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require  # Pooled connection string

# Cloudflare settings for BGE-M3
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_AI_BASE_URL=https://api.cloudflare.com/client/v4

# Configuration limits
MAX_UPLOAD_SIZE_MB=10
```

