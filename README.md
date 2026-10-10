# RAG Document Assistant

PDF փաստաթղթերի վրա հիմնված հարցուպատասխանի REST API՝ կառուցված FastAPI-ով։ Համակարգը փաստաթղթերից ստանում է տեքստը, ստեղծում է semantic embeddings, համապատասխան հատվածները պահում և որոնում է ChromaDB-ում, ապա Anthropic LLM-ի միջոցով ձևավորում է պատասխան՝ վերադարձնելով նաև օգտագործված աղբյուրները։

## Հիմնական հնարավորությունները

- PDF փաստաթղթերի բեռնում և տեքստի extraction
- Overlap ունեցող character-based chunking
- `all-MiniLM-L6-v2` model-ով local embeddings
- ChromaDB persistent vector store
- Cosine similarity-ով semantic search
- Anthropic Claude-ի միջոցով context-grounded պատասխաններ
- Պատասխանի հետ source metadata՝ filename և chunk index
- Բեռնված փաստաթղթերի library
- Փաստաթղթի և դրա բոլոր chunk-երի ջնջում
- Pydantic request/response validation
- Pytest automated tests
- Docker containerization

## Ինչպես է աշխատում

```text
PDF upload
    ↓
PyPDF text extraction
    ↓
Character-based chunking (500 chars, 100 overlap)
    ↓
Sentence Transformers embeddings
    ↓
ChromaDB persistent collection
    ↓
Question embedding + cosine similarity search
    ↓
Top-K relevant chunks
    ↓
Anthropic LLM prompt
    ↓
Answer + source citations
```

RAG-ը (Retrieval-Augmented Generation) թույլ է տալիս ամբողջ PDF-ը յուրաքանչյուր հարցման ժամանակ LLM-ին չուղարկել։ Փոխարենը համակարգը նախ գտնում է հարցին իմաստային առումով ամենամոտ chunk-երը և model-ին փոխանցում միայն այդ context-ը։ Սա նվազեցնում է prompt-ի ծավալը և օգնում է պատասխանը կապել բեռնված փաստաթղթերի բովանդակությանը։

## Tech stack

- **Python 3.12**
- **FastAPI** — REST API
- **Pydantic** — request/response schemas
- **PyPDF** — PDF text extraction
- **Sentence Transformers** — embeddings
- **`all-MiniLM-L6-v2`** — embedding model
- **ChromaDB** — persistent vector database
- **Anthropic SDK** — Claude LLM integration
- **Uvicorn** — ASGI server
- **Pytest** — automated tests
- **Docker** — containerized runtime

## Նախագծի կառուցվածքը

```text
rag-assistant/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── document.py
│   │   ├── llm.py
│   │   ├── retrieval.py
│   │   └── vector_db.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   ├── test_document.py
│   └── test_vector_db.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Տեղադրում և local run

### 1. Clone արեք repository-ն

```bash
git clone <repository-url>
cd rag-assistant
```

### 2. Ստեղծեք virtual environment

```bash
python -m venv .venv
```

Windows PowerShell-ում ակտիվացրեք այն՝

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS-ում՝

```bash
source .venv/bin/activate
```

### 3. Տեղադրեք dependencies-ը

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ստեղծեք `.env` ֆայլը

Project root-ում ստեղծեք `.env`՝ հետևյալ պարունակությամբ․

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
```

> Մի commit արեք `.env` ֆայլը և երբեք source code-ում կամ README-ում մի պահեք իրական API key։

### 5. Գործարկեք API-ն

```bash
python -m uvicorn app.main:app --reload
```

Հասանելի հասցեներ՝

- Swagger UI՝ <http://localhost:8000/docs>
- ReDoc՝ <http://localhost:8000/redoc>
- Health check՝ <http://localhost:8000/health>

Առաջին գործարկման ժամանակ Sentence Transformers-ը կարող է ներբեռնել `all-MiniLM-L6-v2` model-ը։

## API endpoints

### Health check

```http
GET /health
```

Response՝

```json
{
  "status": "ok"
}
```

### PDF փաստաթղթի բեռնում

```http
POST /documents
Content-Type: multipart/form-data
```

Request-ի multipart field-ը կոչվում է `file`։ Endpoint-ը ընդունում է միայն `application/pdf` content type ունեցող ֆայլեր։

```bash
curl -X POST "http://localhost:8000/documents" \
  -H "accept: application/json" \
  -F "file=@document.pdf;type=application/pdf"
```

Response-ի օրինակ՝

```json
{
  "document_id": "30f71b1a-c087-4c71-ae31-d93d6c98165d",
  "filename": "document.pdf",
  "characters": 18420,
  "chunks": 47
}
```

Յուրաքանչյուր document ստանում է UUID։ Դրա chunk-երը embedding-ի և metadata-ի հետ պահպանվում են ChromaDB-ում։

### Հարց փաստաթղթերի վերաբերյալ

```http
POST /ask
Content-Type: application/json
```

Request-ի օրինակ՝

```json
{
  "question": "What is the refund policy?",
  "top_k": 3
}
```

`top_k`-ի default արժեքը `5` է։ Որոնումն իրականացվում է library-ում առկա բոլոր փաստաթղթերի chunk-երի միջով։ `0.85`-ից մեծ cosine distance ունեցող արդյունքները չեն փոխանցվում LLM-ին։

Response-ի օրինակ՝

```json
{
  "question": "What is the refund policy?",
  "top_k": 3,
  "context": [
    {
      "text": "Customers can return products within 30 days of purchase.",
      "distance": 0.18,
      "metadata": {
        "document_id": "30f71b1a-c087-4c71-ae31-d93d6c98165d",
        "filename": "refund_policy.pdf",
        "chunk_index": 2
      }
    }
  ],
  "sources": [
    {
      "filename": "refund_policy.pdf",
      "chunk_index": 2
    }
  ],
  "answer": "Customers can return products within 30 days of purchase."
}
```

Եթե համապատասխան context չի գտնվել, endpoint-ը վերադարձնում է դատարկ `context` և `sources` arrays ու հետևյալ պատասխանը․

```text
I don't know based on the provided documents.
```

### Փաստաթղթերի library

```http
GET /library
```

Response-ի օրինակ՝

```json
{
  "documents": [
    {
      "document_id": "30f71b1a-c087-4c71-ae31-d93d6c98165d",
      "filename": "refund_policy.pdf"
    }
  ]
}
```

### Փաստաթղթի ջնջում

```http
DELETE /library/{document_id}
```

```bash
curl -X DELETE \
  "http://localhost:8000/library/30f71b1a-c087-4c71-ae31-d93d6c98165d"
```

Հաջող response՝

```json
{
  "status": "deleted",
  "document_id": "30f71b1a-c087-4c71-ae31-d93d6c98165d"
}
```

Չգտնված `document_id`-ի դեպքում API-ն վերադարձնում է `404 Not Found`։ Ջնջումը ChromaDB-ից հեռացնում է տվյալ document-ին պատկանող բոլոր chunk-երը։

## Docker

### Build

Project root-ից՝

```bash
docker build -t rag-assistant .
```

### Run

```bash
docker run --name rag-assistant-container \
  -p 8000:8000 \
  --env-file .env \
  rag-assistant
```

Windows PowerShell-ում նույն command-ը մեկ տողով՝

```powershell
docker run --name rag-assistant-container -p 8000:8000 --env-file .env rag-assistant
```

`.dockerignore`-ը image-ի մեջ չի պատճենում local `.env`-ը, virtual environment-ը, Git history-ն և `chroma_db/` տվյալները։ Այդ պատճառով նոր container-ը սկսում է դատարկ vector database-ով։

### ChromaDB persistence Docker-ում

Container-ը ջնջելուց հետո vector data-ն պահպանելու համար օգտագործեք named volume՝

```bash
docker run --name rag-assistant-container \
  -p 8000:8000 \
  --env-file .env \
  -v rag-assistant-chroma:/app/chroma_db \
  rag-assistant
```

Արդեն ստեղծված container-ը կրկին գործարկելու համար՝

```bash
docker start -a rag-assistant-container
```

## Tests

Գործարկեք ամբողջ test suite-ը՝

```bash
pytest -v
```

Ներկա tests-ը ստուգում են՝

- health endpoint-ը,
- document upload-ի հաջող և սխալ դեպքերը,
- context-ով և առանց համապատասխան context-ի `/ask` behavior-ը,
- chunking-ը և դրա validation rules-ը,
- ChromaDB document lookup/delete/library helper-ները։

API tests-ում retrieval և LLM calls-ը mock են արված, ուստի test suite-ը չի ուղարկում իրական request Anthropic API-ին։

## Persistence և տվյալների պահպանում

Local run-ի ժամանակ ChromaDB-ն տվյալները պահում է project root-ի `chroma_db/` directory-ում։ Server restart-ը չի ջնջում դրանք։ Յուրաքանչյուր chunk-ի metadata-ն ներառում է՝

- `document_id`
- `filename`
- `chunk_index`

Uploaded PDF-ի original binary file-ը չի պահպանվում․ պահպանվում են միայն extracted chunks-ը, embeddings-ը և metadata-ն։

## Ներկա սահմանափակումները

- Աջակցվում են միայն text-based PDF-ները․ scanned PDF-ների համար OCR չկա։
- Chunking-ը character-based է և չի հաշվի առնում sentence կամ token boundaries-ը։
- `/ask` որոնում է բոլոր բեռնված փաստաթղթերի միջով և դեռ չունի կոնկրետ `document_id`-ով filter։
- Source citations-ը filename և chunk index metadata են, ոչ թե PDF page number։
- Uploaded original PDF files-ը չեն պահպանվում։
- Authentication, authorization և rate limiting դեռ իրականացված չեն։
- Anthropic API-ի հասանելիությունն ու օգտագործման արժեքը կախված են արտաքին service-ից։
- Docker container-ի տվյալները container removal-ից հետո կկորչեն, եթե volume չօգտագործվի։
- Retrieval և answer quality-ի համար evaluation dataset ու metrics դեռ չկան։

## Հաջորդ հնարավոր բարելավումները

- Token-aware կամ semantic chunking
- PDF page number-ով ավելի ճշգրիտ citations
- `document_id`-ով scoped search
- OCR scanned documents-ի համար
- Configurable embedding և LLM models
- Authentication և per-user document isolation
- Structured logging, monitoring և rate limiting
- Retrieval/answer evaluation pipeline
- Production database և object storage

## Նախագծի կարգավիճակը

Նախագիծը աշխատող portfolio MVP է․ իրականացված են PDF ingestion-ը, persistent vector storage-ը, semantic retrieval-ը, Anthropic LLM generation-ը, source metadata-ն, document library management-ը, automated tests-ը և Docker setup-ը։ Այն նախատեսված է ուսումնական և demo օգտագործման համար և production deployment-ից առաջ պահանջում է security, observability ու scalability լրացումներ։
