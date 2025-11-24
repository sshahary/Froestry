from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import uvicorn

# Add the backend directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

# 🔥 DEV: allow all origins so CORS is definitely not the issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # you can later restrict this to ["http://localhost:3001"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health():
    return {"status": "ok"}

from chatbot_location_search import ResponseStructure, search_tree_locations

@app.post("/get_tree_locations", response_model=ResponseStructure)
async def get_tree_locations_endpoint(request: QueryRequest):
    try:
        return await search_tree_locations(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
