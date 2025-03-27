from fastapi import FastAPI
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from server.controller import receive_prompt
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC_DIR = "static"
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Mount the static directory for other assets (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount the index.html file from the static directory
@app.get("/")
async def serve_index():
    """
    Serve the index.html file
    """
    try:
        index_path = os.path.join(static_dir, "index.html")
        return FileResponse(index_path)
    except Exception as e:
        return {"message": "Welcome to DeeBee API"}

# @app.get("/")
# async def root():
#     """
#     Return a message to indicate the API is running
#     """
#     return "DeeBee running"


@app.post("/chat")
async def generate_query(data: dict = Body(...)):
    """
    Generate SQL query based on natural language prompt
    """
    result = receive_prompt(data['prompt'])
    return {
        "message": "success",
        "response": result
    }
