from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
import redis.asyncio as redis
import os
import json
from datetime import datetime
import uvicorn
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Worker Service", description="Mining Coordinator for CryptoSim")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Service URLs
RNG_SERVICE_URL = os.getenv("RNG_SERVICE_URL", "http://localhost:8000")
HASHER_SERVICE_URL = os.getenv("HASHER_SERVICE_URL", "http://localhost:8001")

# Initialize Redis client
redis_client: Optional[redis.Redis] = None

# Mining state
is_mining = False
mining_task = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_redis_client() -> redis.Redis:
    """Initialize Redis client if not already initialized."""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
    return redis_client

async def mine_block():
    """
    Core mining logic - coordinates between RNG and hasher services,
    storing results in Redis.
    """
    global is_mining
    
    try:
        redis_client = await get_redis_client()
        async with aiohttp.ClientSession() as session:
            while is_mining:
                start_time = datetime.now()
                
                # Step 1: Get random number
                async with session.get(f"{RNG_SERVICE_URL}/random") as rng_response:
                    if rng_response.status != 200:
                        logger.error("Failed to get random number")
                        continue
                    random_data = await rng_response.json()
                    number = random_data["number"]
                
                # Step 2: Compute hash
                hash_payload = {
                    "number": number,
                    "complexity": 2  # Adjustable mining difficulty
                }
                async with session.post(
                    f"{HASHER_SERVICE_URL}/hash",
                    json=hash_payload
                ) as hash_response:
                    if hash_response.status != 200:
                        logger.error("Failed to compute hash")
                        continue
                    hash_result = await hash_response.json()
                
                # Step 3: Store mining result
                mining_result = {
                    "timestamp": datetime.now().isoformat(),
                    "input_number": number,
                    "hash": hash_result["hash_result"],
                    "computation_time": hash_result["computation_time"]
                }
                
                # Store in Redis with TTL of 1 hour
                await redis_client.setex(
                    f"mining_result:{start_time.timestamp()}",
                    3600,  # 1 hour TTL
                    json.dumps(mining_result)
                )
                
                # Update mining stats
                await update_mining_stats(mining_result["computation_time"])
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Mining error: {str(e)}")
        is_mining = False
    finally:
        is_mining = False

async def update_mining_stats(computation_time: float):
    """Update mining statistics in Redis."""
    try:
        redis_client = await get_redis_client()
        
        # Increment total blocks mined
        await redis_client.incr("stats:total_blocks")
        
        # Update average computation time
        await redis_client.lpush("stats:computation_times", computation_time)
        await redis_client.ltrim("stats:computation_times", 0, 99)  # Keep last 100 times
        
        # Calculate and store mining rate (blocks per second)
        times = await redis_client.lrange("stats:computation_times", 0, -1)
        if times:
            avg_time = sum(float(t) for t in times) / len(times)
            mining_rate = 1 / avg_time if avg_time > 0 else 0
            await redis_client.set("stats:mining_rate", mining_rate)
            
    except Exception as e:
        logger.error(f"Error updating stats: {str(e)}")

@app.get("/")
async def read_root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "worker",
        "is_mining": is_mining
    }

@app.post("/start")
async def start_mining(background_tasks: BackgroundTasks):
    """Start the mining process."""
    global is_mining, mining_task
    
    if is_mining:
        return {"status": "already_running"}
    
    is_mining = True
    background_tasks.add_task(mine_block)
    return {"status": "started"}

@app.post("/stop")
async def stop_mining():
    """Stop the mining process."""
    global is_mining
    
    if not is_mining:
        return {"status": "not_running"}
    
    is_mining = False
    return {"status": "stopped"}

@app.get("/stats")
async def get_stats():
    """Get current mining statistics."""
    try:
        redis_client = await get_redis_client()
        
        # Retrieve stats from Redis
        total_blocks = await redis_client.get("stats:total_blocks")
        mining_rate = await redis_client.get("stats:mining_rate")
        
        return {
            "total_blocks": int(total_blocks or 0),
            "mining_rate": float(mining_rate or 0),
            "is_mining": is_mining
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)