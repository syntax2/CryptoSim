from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time
import uvicorn
import os
from typing import Optional
import asyncio
from datetime import datetime

app = FastAPI(title="Hasher Service", description="Hash Computing Service for Crypto Mining Simulator")

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NumberInput(BaseModel):
    number: int
    complexity: Optional[int] = 1  # Mining difficulty simulation

class HashResult(BaseModel):
    input_number: int
    hash_result: str
    computation_time: float
    timestamp: str

# In-memory storage for recent hashes (could be moved to Redis in production)
recent_hashes = []
MAX_STORED_HASHES = 100

def compute_hash(number: int, complexity: int) -> tuple[str, float]:
    """
    Compute a hash with artificial complexity to simulate mining difficulty.
    
    Args:
        number: The input number to hash
        complexity: Number of times to rehash (simulate difficulty)
        
    Returns:
        tuple: (Final hash value, Computation time in seconds)
    """
    start_time = time.time()
    current_hash = str(number).encode()
    
    # Simulate mining difficulty by performing multiple rounds of hashing
    for _ in range(complexity):
        current_hash = hashlib.sha256(current_hash).digest()
        # Add small delay to simulate real-world mining complexity
        time.sleep(0.001 * complexity)
    
    final_hash = current_hash.hex()
    computation_time = time.time() - start_time
    
    return final_hash, computation_time

@app.get("/")
async def read_root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hasher",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/hash", response_model=HashResult)
async def create_hash(input_data: NumberInput, background_tasks: BackgroundTasks):
    """
    Create a hash from the input number with specified complexity.
    
    Args:
        input_data: NumberInput model containing the number and optional complexity
        background_tasks: FastAPI background tasks handler
    
    Returns:
        HashResult: Contains the input number, hash result, computation time, and timestamp
    """
    try:
        # Ensure complexity is within reasonable bounds
        complexity = max(1, min(input_data.complexity, 10))
        
        # Compute hash with artificial complexity
        hash_value, comp_time = compute_hash(input_data.number, complexity)
        
        result = HashResult(
            input_number=input_data.number,
            hash_result=hash_value,
            computation_time=comp_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store hash result in background
        background_tasks.add_task(store_hash_result, dict(result))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent")
async def get_recent_hashes():
    """Get recent hash computations."""
    return recent_hashes

def store_hash_result(result: dict):
    """Store hash result and maintain maximum size of recent hashes."""
    global recent_hashes
    recent_hashes.append(result)
    if len(recent_hashes) > MAX_STORED_HASHES:
        recent_hashes = recent_hashes[-MAX_STORED_HASHES:]

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # Different port from RNG service
    uvicorn.run(app, host="0.0.0.0", port=port)