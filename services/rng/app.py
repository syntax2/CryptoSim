from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
import uvicorn
import os

app = FastAPI(title="RNG Service", description="Random Number Generator for Crypto Mining Simulator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"status": "healthy", "service": "rng"}

@app.get("/random")
async def get_random():
    try:
        # Generate a random number between 0 and 100000
        number = random.randint(0, 100000)
        return {"number": number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)