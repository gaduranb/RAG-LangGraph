# Banking Login & Security Helper - Architecture

## System Overview

```mermaid
graph TB
    User[User] -->|HTTP Request| Frontend[Next.js Frontend<br/>Port 3000]
    Frontend -->|POST /chat| Backend[FastAPI Backend<br/>Port 8000]
    Backend -->|Invoke| Agent[LangGraph Agent]

    Agent -->|1. Route| Router[Router Node<br/>Keyword Classification]
    Router -->|Out of Scope| OutOfScope[Out of Scope Node]
    Router -->|In Scope| Retriever[Retriever Node<br/>RAG]

    Retriever -->|Query| VectorDB[(Chroma VectorDB<br/>13 chunks)]
    VectorDB -->|Top-k=3 Docs| Retriever

    Retriever -->|Needs Holidays?| HolidaysCheck{Holidays<br/>Check}
    HolidaysCheck -->|Yes| Holidays[Holidays Node]
    HolidaysCheck -->|No| LLM[LLM Answer Node]

    Holidays -->|API Call| FederalAPI[Federal Holidays API<br/>Nager.Date]
    FederalAPI -->|Holiday Data| Holidays
    Holidays --> LLM

    LLM -->|Generate with<br/>RAG Context| OpenAI[OpenAI GPT-4o-mini]
    OpenAI -->|Response| LLM

    LLM -->|Answer + Citations| Backend
    OutOfScope -->|Helpful Message| Backend
    Backend -->|JSON Response| Frontend
    Frontend -->|Display| User

    style Agent fill:#e1f5ff
    style VectorDB fill:#fff4e1
    style OpenAI fill:#f0e1ff
    style FederalAPI fill:#e1ffe1
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend (Next.js)"
        UI[Chat UI<br/>shadcn/ui]
        State[React State]
    end

    subgraph "Backend (FastAPI)"
        API[API Endpoints<br/>/chat, /health]
        Main[Main App]
    end

    subgraph "LangGraph Agent"
        Graph[StateGraph]
        Nodes[Agent Nodes]
        Edges[Conditional Edges]
    end

    subgraph "RAG Pipeline"
        Ingestion[PDF Ingestion<br/>PyPDF]
        Chunking[Text Splitter<br/>1000 chars]
        Embeddings[OpenAI Embeddings<br/>text-embedding-3-small]
        VDB[(Chroma VectorDB)]
        Retrieval[Similarity Search<br/>k=3]
    end

    subgraph "External Services"
        LLM[OpenAI API<br/>GPT-4o-mini]
        HolidaysAPI[Federal Holidays API]
    end

    UI --> API
    API --> Graph
    Graph --> Nodes
    Nodes --> Retrieval
    Retrieval --> VDB
    Embeddings --> VDB
    Ingestion --> Chunking --> Embeddings
    Nodes --> LLM
    Nodes --> HolidaysAPI

    style RAG Pipeline fill:#fff4e1
    style External Services fill:#e1ffe1
```

## Agent Flow (LangGraph)

```mermaid
stateDiagram-v2
    [*] --> Router

    Router --> OutOfScope: is_out_of_scope = true
    Router --> Retriever: is_out_of_scope = false

    OutOfScope --> [*]: Return helpful<br/>support message

    Retriever --> HolidaysDecision: Check needs_holidays

    HolidaysDecision --> Holidays: needs_holidays = true
    HolidaysDecision --> LLMAnswer: needs_holidays = false

    Holidays --> LLMAnswer: Add holiday context

    LLMAnswer --> [*]: Return answer<br/>+ citations

    note right of Router
        Keyword-based classification:
        - login_security_keywords
        - holiday_keywords
        - Benefit of doubt
    end note

    note right of Retriever
        RAG Process:
        1. Query vectorstore
        2. Get top-k=3 docs
        3. Extract citations
        4. Format for LLM
    end note

    note right of LLMAnswer
        Generate response with:
        - RAG context
        - Holiday info (if any)
        - System prompt
        - Return citations
    end note
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant R as Router Node
    participant RT as Retriever Node
    participant V as Chroma VectorDB
    participant L as LLM Answer Node
    participant O as OpenAI API

    U->>F: Ask question
    F->>B: POST /chat
    B->>R: Initialize state
    R->>R: Classify intent

    alt Out of Scope
        R-->>B: Return support message
    else In Scope
        R->>RT: Route to retriever
        RT->>V: Similarity search (k=3)
        V-->>RT: Return docs + metadata
        RT->>RT: Extract citations
        RT->>L: Pass docs + state
        L->>O: Generate with RAG context
        O-->>L: Response
        L-->>B: Answer + citations
    end

    B-->>F: JSON response
    F-->>U: Display answer + sources
```

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **UI Library**: shadcn/ui + TailwindCSS
- **State**: React hooks
- **Deployment**: Docker (standalone output)

### Backend
- **API**: FastAPI (Python 3.11)
- **Agent**: LangGraph 0.2.60
- **Validation**: Pydantic

### AI/ML
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Chroma 0.5.23
- **Framework**: LangChain 0.3.14

### Data Processing
- **PDF Loader**: PyPDF 5.1.0
- **Text Splitter**: RecursiveCharacterTextSplitter
  - Chunk size: 1000 characters
  - Chunk overlap: 200 characters

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Persistence**: Volume mounts (`./backend/data`)

## Key Design Decisions

### 1. Keyword-based Router
- **Choice**: Keyword matching over LLM classification
- **Rationale**: Faster, more reliable, no extra LLM calls
- **Trade-off**: Less flexible, requires keyword maintenance

### 2. Chroma Vector Database
- **Choice**: Chroma over FAISS/Pinecone
- **Rationale**:
  - Persistent storage
  - Easy Docker integration
  - Metadata support
  - Good performance for small-medium datasets

### 3. Small Chunk Size (1000 chars)
- **Choice**: 1000 chars with 200 overlap
- **Rationale**:
  - Better semantic granularity
  - More precise citations
  - Fits within LLM context window efficiently

### 4. Top-k=3 Retrieval
- **Choice**: Retrieve 3 most relevant chunks
- **Rationale**:
  - Balance between context and noise
  - Keeps LLM prompt concise
  - Meets latency SLA

### 5. Benefit of Doubt Routing
- **Choice**: Assume in-scope if no keywords match
- **Rationale**:
  - Better UX (attempt to answer)
  - Scope is broad (login/security)
  - Can still defer to support if needed

## Performance Characteristics

- **p95 Latency**: ~5 seconds (meets SLA)
- **p50 Latency**: ~4-5 seconds
- **Vector DB Size**: 13 chunks (from 5 PDF pages)
- **Embedding Dimensions**: 1536 (text-embedding-3-small)
- **Memory Usage**: ~500MB (including vectorstore)
- **Container Size**: ~2GB (backend), ~500MB (frontend)

## Security Considerations

- **API Key Management**: Environment variables, .gitignore
- **Data Isolation**: No user data stored, stateless design
- **Scope Limitation**: Only answers login/security questions
- **Safe Fallback**: Directs to support for out-of-scope

## Observability

- **Logging**: Print statements to stdout (Docker logs)
- **Metrics**: Response timing in API response
- **Citations**: Source tracking per response
- **Tool Calls**: Logged in response metadata

## Future Enhancements

1. **Streaming**: SSE endpoint for progressive responses
2. **State Persistence**: Redis/SQLite for conversation history
3. **Structured Logging**: JSON logs with correlation IDs
4. **Rate Limiting**: Per-user request throttling
5. **A/B Testing**: Multiple retrieval strategies
6. **Fine-tuning**: Custom embeddings model
7. **Monitoring**: Prometheus/Grafana dashboards
