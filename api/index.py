from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import json
import os
import numpy as np

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class CheckRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

@app.get("/")
def read_root():
    return {"message": "eShopCo Latency Analysis API", "status": "online"}

@app.post("/check")
def check(data: CheckRequest):
    regions = data.regions
    threshold_ms = data.threshold_ms

    file = "q-vercel-latency.json"
    path = os.path.join(os.path.dirname(__file__), file)
    
    with open(path, "r") as f:
        telemetry = json.load(f)

    result = {}

    for region in regions:
        latency_sum = 0
        uptime_sum = 0
        breaches = 0
        count = 0

        for entry in telemetry:
            if entry["region"] == region:
                latency_sum += entry["latency_ms"]
                uptime_sum += entry["uptime_pct"]
                count += 1
                if entry["latency_ms"] > threshold_ms:
                    breaches += 1

        avg_latency = round(latency_sum / count, 2) if count else 0
        avg_uptime = round(uptime_sum / count, 2) if count else 0

        region_latencies = [e["latency_ms"] for e in telemetry if e["region"] == region]
        p95 = np.percentile(region_latencies, 95) if region_latencies else 0

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95": round(p95, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches,
        }
    
    return {"regions": result}