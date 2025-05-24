from fastapi import FastAPI
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from server.controller import main_controller, execute_controller
# from server.controller import execute_controller
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

origins = [
    "http://localhost:5656",
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
    result = main_controller(data['prompt'])
    return {
        "message": result['message'],
        "executed_result": result['executed_result'],
        "query": result['query'],
    }

from fastapi import HTTPException

@app.post("/execute")
async def execute(data: dict = Body(...)):
    """
    Generate SQL query based on natural language prompt
    """
    executed_result = execute_controller(data['query'])
    
    if 'error' in executed_result:
        
        raise HTTPException(status_code=500, detail=executed_result['error'])
    
    return {
        "message": "success",
        "executed_result": executed_result['executed_result'],
        "query": executed_result['query'],
    }
