from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
# from numpy import histogram
import aiohttp
import asyncio
import redis.asyncio as redis
import os
import json
from datetime import datetime
from prometheus_client import Counter, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import time
import uvicorn
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Prometheus metrics
BLOCKS_MINED = Counter('cryptosim_blocks_mined_total', 'Total number of blocks mined')
MINING_RATE = Gauge('cryptosim_mining_rate', 'Current mining rate in blocks per second')
MINING_ACTIVE = Gauge('cryptosim_mining_active', 'Mining status (1 = active, 0 = inactive)')

# MINING_DURATION = histogram('cryptosim_mining_duration_seconds', 'Time spent mining each block', buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
HASH_REQUEST_ERRORS = Counter('cryptosim_hash_request_errors_total', 'Total number of failed hash requests')
RNG_REQUEST_ERRORS = Counter('cryptosim_rng_request_errors_total', 'Total number of failed RNG requests')

app = FastAPI(title="Worker Service")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
RNG_SERVICE_URL = os.getenv("RNG_SERVICE_URL", "http://localhost:8000")
HASHER_SERVICE_URL = os.getenv("HASHER_SERVICE_URL", "http://localhost:8001")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Global variables
redis_client: Optional[redis.Redis] = None
is_mining = False

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
    return redis_client

async def clear_redis_keys():
    """Clear existing Redis keys to prevent type conflicts."""
    redis = await get_redis()
    keys = ["mining_active", "total_blocks", "mining_rate", "recent_mines"]
    for key in keys:
        await redis.delete(key)

async def mine_block():
    global is_mining
    redis = await get_redis()
    
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            blocks_mined = 0
            
            while is_mining:
                try:
                    async with session.get(f"{RNG_SERVICE_URL}/random") as rng_response:
                        if rng_response.status != 200:
                            RNG_REQUEST_ERRORS.inc()
                            continue
                        number = (await rng_response.json())["number"]
                except Exception as e:
                    RNG_REQUEST_ERRORS.inc()
                    logger.error(f"RNG request error: {str(e)}")
                    continue

                try:
                    async with session.post(
                        f"{HASHER_SERVICE_URL}/hash",
                        json={"number": number, "complexity": 1}
                    ) as hash_response:
                        if hash_response.status != 200:
                            HASH_REQUEST_ERRORS.inc()
                            continue
                        hash_result = await hash_response.json()
                except Exception as e:
                    HASH_REQUEST_ERRORS.inc()
                    logger.error(f"Hash request error: {str(e)}")
                    continue
                # Get random number
                # async with session.get(f"{RNG_SERVICE_URL}/random") as rng_response:
                #     if rng_response.status != 200:
                #         continue
                #     number = (await rng_response.json())["number"]
                
                # # Hash the number
                # async with session.post(
                #     f"{HASHER_SERVICE_URL}/hash",
                #     json={"number": number, "complexity": 1}
                # ) as hash_response:
                #     if hash_response.status != 200:
                #         continue
                
                # Update stats
                blocks_mined += 1
                await redis.incr("total_blocks")
                BLOCKS_MINED.inc()  # Update Prometheus metric
                
                # Calculate and update mining rate every second
                elapsed = time.time() - start_time
                if elapsed >= 1.0:
                    mining_rate = blocks_mined / elapsed
                    await redis.set("mining_rate", str(mining_rate))
                    MINING_RATE.set(mining_rate)  # Update Prometheus metric
                    blocks_mined = 0
                    start_time = time.time()
                
                await asyncio.sleep(0.1)  # Prevent overwhelming the system
                
    except Exception as e:
        logger.error(f"Mining error: {str(e)}")
    finally:
        is_mining = False
        await redis.set("mining_active", "0")
        await redis.set("mining_rate", "0")

@app.on_event("startup")
async def startup_event():
    await clear_redis_keys()

@app.get("/")
async def read_root():
    return {"status": "healthy"}

@app.post("/start")
async def start_mining(background_tasks: BackgroundTasks):
    global is_mining
    
    if is_mining:
        return {"status": "already_running"}
    
    redis = await get_redis()
    is_mining = True
    await redis.set("mining_active", "1")
    background_tasks.add_task(mine_block)
    
    return {"status": "started"}

@app.post("/stop")
async def stop_mining():
    global is_mining
    
    if not is_mining:
        return {"status": "not_running"}
    
    redis = await get_redis()
    is_mining = False
    await redis.set("mining_active", "0")
    await redis.set("mining_rate", "0")
    
    return {"status": "stopped"}

@app.get("/stats")
async def get_stats():
    redis = await get_redis()
    
    total_blocks = await redis.get("total_blocks")
    mining_rate = await redis.get("mining_rate")
    mining_active = await redis.get("mining_active")
    
    return {
        "total_blocks": int(total_blocks or 0),
        "mining_rate": float(mining_rate or 0),
        "is_mining": mining_active == "1"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)