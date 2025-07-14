from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from pydantic import BaseModel
from collections import deque
import logging
import wrapper
import os

app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
origins = [origin.strip() for origin in origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogStore:
    def __init__(self):
        self.logs = deque(maxlen=20)

    def add_log(self, log: str):
        self.logs.append(log)

    def clear_logs(self):
        self.logs.clear()
    
    def get_last_n_logs(self, n: int):
        return list(self.logs)[-n:] if n <= len(self.logs) else list(self.logs)

    def get_logs(self):
        return list(self.logs)
    
log_store = LogStore()
log_path = "./fastapi.logs"

class LogStoreHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_store.add_log(log_entry)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

store_handler = LogStoreHandler()
store_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)

logger = logging.getLogger("fastapi_logger")
logger.setLevel(logging.INFO)
logger.addHandler(store_handler)
logger.addHandler(file_handler)

@app.get("/")
def home():
    return {"message": "Hello, World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

class UserQuery(BaseModel):
    user_name: str
    user_age: int
    user_input: str
    user_jwt: str = None
    last_response_id: str = None
    use_structuring: bool = False

@app.post("/agent_response")
async def get_agent_response(user_query: UserQuery):
    logger.info(f"Query on Get Agent Response")
    if not user_query.user_input or user_query.user_input.strip() == "":
        logger.error(f"Invalid user query: {user_query}")
        return JSONResponse(content={"message": "Invalid user query"}, status_code=400)
    if not user_query.last_response_id or user_query.last_response_id.strip() == "":
        user_query.last_response_id = None
    try:
        response = await wrapper.get_agent_response(
            user_name=user_query.user_name,
            user_age=user_query.user_age,
            user_input=user_query.user_input,
            last_response_id=user_query.last_response_id,
            use_structuring=user_query.use_structuring,
            user_jwt=user_query.user_jwt
        )
        response['message'] = "Success"
        logger.info(f"Successfully fetched agent response")
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        logger.error(f"Error fetching agent response: {e}")
        return JSONResponse(content={"message": "Could Not Fetch response try again later"}, status_code=404)
    
@app.get("/logs")
def get_all_logs(join: bool = False):
    if join: return {"logs": "\n".join(log_store.get_logs())}
    return {"logs": log_store.get_logs()}

@app.get("/logs/download")
def download_log():
    if not os.path.exists(log_path):
        return JSONResponse(status_code=404, content={"error": "Log file not found."})
    return FileResponse(log_path, media_type='text/plain', filename="fastapi.log")

@app.get("/logs/{n}")
def get_last_n_logs(n: int, join: bool = False):
    if join: return {"logs": "\n".join(log_store.get_last_n_logs(n))}
    return {"logs": log_store.get_last_n_logs(n)}

@app.delete("/logs/delete")
def clear_logs():
    log_store.clear_logs()
    return {"status": "cleared"}

@app.get("/cors")
def get_cors():
    return {"allowed": origins}