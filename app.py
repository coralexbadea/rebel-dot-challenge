import typing as t
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette import status
from database.databaseUtils import get_vector_store
from langchain.vectorstores import VectorStore
from chains.chainsUtils import get_full_chain
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

class Question(BaseModel):
    user_question: str
class UnauthorizedMessage(BaseModel):
    detail: str = "Bearer token missing or unknown"

app = FastAPI(title="ML Models as API on Google Colab", description="with FastAPI and ColabCode", version="1.0")

# Placeholder for a database containing valid token values
known_tokens = set(["api_token_abc123"])
# We will handle a missing token ourselves
get_bearer_token = HTTPBearer(auto_error=False)

async def get_token(
    auth: t.Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    # Simulate a database query to find a known token
    if auth is None or (token := auth.credentials) not in known_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UnauthorizedMessage().detail,
        )
    return token

@app.on_event("startup")
def load_model():
    global retriever
    global full_chain

    db: VectorStore = get_vector_store()
    retriever = db.as_retriever(search_type="similarity_score_threshold", 
                    search_kwargs={"score_threshold": .8, 
                    "k": 1})
    full_chain = get_full_chain()


@app.post("/ask-question",
          responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},)
async def answer(request: Question, token: str = Depends(get_token)):
    query = request.user_question
    chat_response = {
        "source": "",
        "matched_question": "",
        "answer": ""
    }
    try:
        docs = retriever.get_relevant_documents(query)
        if len(docs):
            document = docs[0]
            chat_response['source'] = 'local'
            chat_response['matched_question'] = document.page_content
            chat_response['answer'] = document.metadata['answer']
        else:
            answer = full_chain.invoke({"question": query})
            chat_response['source'] = 'openai'
            chat_response['matched_question'] = 'N/A'
            chat_response['answer'] = answer
    except Exception as e:
            chat_response['source'] = 'error'
            chat_response['matched_question'] = 'N/A'
            chat_response['answer'] = e.__str__()

    return chat_response