# server.py
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI

# ---------- Конфигурация (настройте под себя) ----------
FAISS_INDEX_PATH = "faiss_roag_index"          # папка с индексом
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

LLM_BASE_URL = "http://localhost:1234/v1"     # или ваш удалённый LLM
LLM_MODEL = "local-model"                     # название модели
LLM_API_KEY = "not-needed"

# Системный промпт и тревожные триггеры (как раньше)
SYSTEM_PROMPT = """Ты — ИИ-ассистент для врачей акушеров-гинекологов, работающий строго на основе клинических рекомендаций РОАГ.
- Отвечай только на основании предоставленных фрагментов (контекста).
- Если в контексте нет ответа, честно скажи: "В предоставленных клинических рекомендациях ответ не найден".
- Не добавляй информацию из своих общих знаний.
- Отвечай на русском языке, максимально точно и структурированно.
- Указывай источники (названия файлов), которые упоминаются в метаданных.
"""

EMERGENCY_TRIGGERS = [
    "сильное кровотечение", "кровь идёт", "судороги", "потеря сознания",
    "резкая слабость", "острая боль в животе", "давление 160",
    "не чувствую ребёнка", "не шевелится", "отслойка плаценты",
    "преэклампсия", "эклампсия", "внезапная одышка",
    "кровь из влагалища", "слишком сильная боль", "высокая температура 40"
]

EMERGENCY_RESPONSE = (
    "❗ Описанные вами симптомы могут указывать на неотложное состояние. "
    "Пожалуйста, немедленно обратитесь в скорую помощь (тел. 112 или 103) "
    "или к вашему лечащему врачу. "
    "Данный ассистент не предназначен для диагностики и консультаций в экстренных ситуациях."
)

# ---------- Глобальные объекты (инициализируются при старте) ----------
vectorstore = None
embeddings = None

def load_resources():
    global vectorstore, embeddings
    if not Path(FAISS_INDEX_PATH).exists():
        raise FileNotFoundError(f"Индекс не найден: {FAISS_INDEX_PATH}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загрузка при старте
    load_resources()
    yield
    # Очистка при остановке (если нужно)

app = FastAPI(lifespan=lifespan)

# Модели запроса/ответа
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    emergency: bool

# ---------- Логика детектора ----------
def is_emergency(text: str) -> bool:
    text_lower = text.lower()
    for trigger in EMERGENCY_TRIGGERS:
        if trigger in text_lower:
            return True
    return False

# ---------- Основной эндпоинт ----------
@app.post("/ask", response_model=QueryResponse)
async def ask_endpoint(req: QueryRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Пустой запрос")

    # Проверяем тревожность
    if is_emergency(query):
        return QueryResponse(answer=EMERGENCY_RESPONSE, emergency=True)

    # Поиск в FAISS
    docs = vectorstore.similarity_search(query, k=4)
    context = "\n\n".join(
        [f"Источник: {doc.metadata['source']}\n{doc.page_content}" for doc in docs]
    )

    # Формируем запрос к LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {query}\n\nОтвет:"}
    ]

    try:
        client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=1500
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"❌ Ошибка при обращении к LLM: {str(e)}"

    return QueryResponse(answer=answer, emergency=False)

# ---------- Запуск ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)