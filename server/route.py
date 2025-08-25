from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from langgraph.graph import StateGraph
# from typing import Optional
import os

from server.agents.agent import process_query 

# Local imports
# from server.agents.tools import generate_sql
# from server.state import GraphState

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
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
    try:
        print("\n" + "="*50)
        print("=== New Request ===")
        print(f"Received request with data: {data}")
        
        # Validate input
        if not data or 'prompt' not in data:
            error_msg = "Missing 'prompt' in request body"
            print(f"Validation error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process the query using the lang_test module
        response = await process_query(data['prompt'])
        
        print(f"\nSending response: {response}")
        return response
        
    except HTTPException as he:
        print(f"\nHTTP Exception: {he.detail}")
        raise
        
    except Exception as e:
        error_msg = f"Unexpected error in generate_query: {str(e)}"
        print(f"\nUnexpected error: {error_msg}")
        import traceback
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        print("\n=== End Request ===\n" + "="*50 + "\n")

from fastapi import HTTPException

@app.post("/execute")
async def execute(data: dict = Body(...)):
    """
    Execute SQL query (placeholder for actual execution)
    """
    return {
        "message": "success",
        "executed_result": "Query execution would happen here",
        "query": data.get('query', '')
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
