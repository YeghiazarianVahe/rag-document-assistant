# RAG Document Assistant

PDF փաստաթղթերի բովանդակության հիման վրա հարցերին պատասխանող պարզ RAG համակարգ՝ կառուցված Python-ի և FastAPI-ի միջոցով։

## Խնդրի նկարագրություն

Մեծ ծավալի փաստաթղթերում անհրաժեշտ տեղեկությունը ձեռքով գտնելը ժամանակատար է։ Միևնույն ժամանակ ամբողջ փաստաթուղթը յուրաքանչյուր հարցման ժամանակ Large Language Model-ին (`LLM`) փոխանցելը արդյունավետ չէ և կարող է սահմանափակվել model-ի context window-ով։

Այս նախագծի նպատակը PDF փաստաթուղթ բեռնելու և դրա բովանդակության վերաբերյալ բնական լեզվով հարցեր տալու հնարավորություն ստեղծելն է։ Համակարգը կիրառում է **RAG (Retrieval-Augmented Generation)** մոտեցումը՝ նախ գտնելով հարցին համապատասխան հատվածները, ապա դրանք օգտագործելով պատասխանի համար անհրաժեշտ context կառուցելու նպատակով։

RAG pipeline-ի հիմնական քայլերն են՝

1. PDF փաստաթղթից ստանալ տեքստը։
2. Տեքստը բաժանել փոքր հատվածների՝ `chunks`։
3. Յուրաքանչյուր chunk-ը վերածել embedding vector-ի։
4. Օգտատիրոջ հարցը նույնպես վերածել embedding vector-ի։
5. Cosine similarity-ի միջոցով գտնել հարցին իմաստային առումով ամենամոտ chunk-երը։
6. Ընտրված chunk-երից կառուցել LLM-ի համար անհրաժեշտ context-ը և prompt-ը։
7. LLM-ի միջոցով ստեղծել վերջնական պատասխան։

## Ինչու է պետք RAG

Առանց retrieval փուլի ամբողջ փաստաթուղթը յուրաքանչյուր հարցման հետ LLM-ին ուղարկելը մի քանի խնդիր է առաջացնում՝

- LLM-ի context window-ը սահմանափակ է,
- մեծ prompt-երը բարձրացնում են հարցման արժեքը,
- response-ի latency-ն մեծանում է,
- ավելորդ կամ ոչ համապատասխան context-ը կարող է վատացնել պատասխանի որակը,
- մեծ փաստաթղթերի մշակումը դառնում է դժվար մասշտաբավորվող։

RAG-ը նախ ընտրում է միայն հարցին համապատասխան հատվածները և LLM-ին փոխանցում է նպատակային context։ Սա նվազեցնում է փոխանցվող տվյալների ծավալը և օգնում է ստանալ փաստաթղթի բովանդակության վրա հիմնված պատասխան։

Պարզեցված ձևով՝

```text
Retrieval = գտնել համապատասխան տեղեկությունը
Generation = այդ տեղեկության հիման վրա կազմել պատասխանը
```

## Օրինակ

Ենթադրենք՝ փաստաթղթում գրված է՝

> Customers can return products within 30 days of purchase.

Օգտատերը հարցնում է՝

> Can I return my purchase after two weeks?

Համակարգը հարցը և փաստաթղթի chunk-երը վերածում է embedding vector-ների։ Similarity search-ի միջոցով ընտրվում է հարցին ամենամոտ chunk-ը, ապա կառուցվում է հետևյալ prompt-ը՝

```text
Context:
Customers can return products within 30 days of purchase.

Question:
Can I return my purchase after two weeks?

Answer:
```

LLM-ը կարող է վերադարձնել՝

```text
Yes. Two weeks is within the 30-day return period.
```

## Pipeline

```text
PDF upload
    ↓
PDF text extraction
    ↓
Text chunking
    ↓
Chunk embeddings
    ↓
User question
    ↓
Query embedding
    ↓
Cosine similarity
    ↓
Top-K relevant chunks
    ↓
Prompt construction
    ↓
LLM generation
    ↓
Final answer
```

## Օգտագործվող տեխնոլոգիաներ

- **Python** — նախագծի հիմնական լեզու
- **FastAPI** — REST API-ի ստեղծում
- **Pydantic** — request և response տվյալների validation
- **PyPDF** — PDF ֆայլերից տեքստի ստացում
- **Sentence Transformers** — տեքստային embeddings-ի ստեղծում
- **NumPy** — vector-ների հետ աշխատանք և similarity հաշվարկներ
- **Uvicorn** — ASGI server

Օգտագործվող embedding model-ը՝

```text
all-MiniLM-L6-v2
```

## API endpoints

### Health check

```http
GET /health
```

Օրինակ response՝

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

Endpoint-ը՝

- ընդունում է PDF ֆայլ,
- ստանում է փաստաթղթի տեքստը,
- տեքստը բաժանում է chunk-երի,
- ստեղծում և հիշողության մեջ պահում է chunk embedding-ները։

### Հարց փաստաթղթի վերաբերյալ

```http
POST /ask
Content-Type: application/json
```

Օրինակ request՝

```json
{
  "question": "What is the refund policy?",
  "top_k": 3
}
```

Օրինակ response-ի կառուցվածք՝

```json
{
  "question": "What is the refund policy?",
  "top_k": 3,
  "context": [
    {
      "text": "Customers can return products within 30 days of purchase.",
      "score": 0.72
    }
  ],
  "answer": "Generated answer or constructed prompt"
}
```

Եթե դեռ փաստաթուղթ չի բեռնվել, endpoint-ը վերադարձնում է `400 Bad Request`։

## Նախագծի կառուցվածքը

```text
app/
├── main.py
├── api/
│   └── routes.py
├── models/
│   └── schemas.py
└── services/
    ├── document.py
    ├── retrieval.py
    └── llm.py
```

### `app/main.py`

Ստեղծում է FastAPI application-ը և միացնում API router-ը։

### `app/api/routes.py`

Պարունակում է HTTP endpoint-ները և կապում է համակարգի հիմնական փուլերը՝ document processing, retrieval և generation։

### `app/models/schemas.py`

Պարունակում է Pydantic request և response model-ները։

### `app/services/document.py`

Պատասխանատու է՝

- PDF-ից տեքստ ստանալու,
- տեքստը chunk-երի բաժանելու համար։

### `app/services/retrieval.py`

Պատասխանատու է՝

- embeddings ստեղծելու,
- cosine similarity հաշվելու,
- Top-K համապատասխան chunk-երը գտնելու համար։

### `app/services/llm.py`

Պատասխանատու է retrieved context-ից prompt կառուցելու և հետագայում LLM provider-ի հետ աշխատելու համար։

## Ներկա սահմանափակումները

- Chunk-երը և embedding-ները պահվում են միայն RAM-ում և server restart-ից հետո կորչում են։
- Միաժամանակ տարբեր փաստաթղթերի առանձին կառավարում դեռ չկա։
- Vector database դեռ չի օգտագործվում։
- Generation փուլը ներկայում կառուցում և վերադարձնում է prompt-ը, բայց իրական LLM API call դեռ չի կատարում։
- PDF text extraction-ը նախատեսված է text-based PDF-ների համար և OCR չի կատարում։
- Authentication, authorization և rate limiting դեռ իրականացված չեն։
- Retrieval-ի որակը դեռ գնահատված չէ առանձին evaluation dataset-ով։

## Հաջորդ քայլերը

1. Միացնել իրական LLM provider և վերադարձնել վերջնական բնական լեզվով պատասխանը։
2. Ավելացնել vector database, օրինակ՝ PostgreSQL + pgvector։
3. Պահպանել փաստաթղթերը, chunk-երը և metadata-ն persistent storage-ում։
4. Ավելացնել document ID և մի քանի փաստաթղթի անկախ կառավարում։
5. Բարելավել chunking ռազմավարությունը՝ կիրառելով overlap և token-based սահմաններ։
6. Ավելացնել source citation-ներ՝ պատասխանի հետ վերադարձնելով օգտագործված chunk-երը։
7. Ավելացնել OCR աջակցություն scanned PDF-ների համար։
8. Ավելացնել automated tests՝ document processing, retrieval և API endpoint-ների համար։
9. Չափել retrieval-ի և վերջնական պատասխանների որակը evaluation dataset-ով։
10. Ավելացնել authentication, logging և error handling production օգտագործման համար։

## Նախագծի կարգավիճակը

Նախագիծը գտնվում է զարգացման փուլում։ PDF processing-ը, chunking-ը, embeddings-ի ստեղծումը, similarity search-ը և prompt construction-ը արդեն կազմում են աշխատող հիմնական pipeline։ Հաջորդ առանցքային փուլը իրական LLM integration-ն է։
