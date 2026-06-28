from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
from collections import deque
from datetime import datetime

app = FastAPI()

# CORS taaki grader browser se check kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Prometheus Counter (Exact wahi naam jo grader ko chahiye)
http_requests_total = Counter("http_requests_total", "Total HTTP requests")

# 2. Uptime ke liye server start time save karna
START_TIME = time.time()

# 3. Logs save karne ke liye list (Memory mein last 1000 logs rakhega)
log_storage = deque(maxlen=1000)

# YAHAN APNA LOGIN EMAIL DALEIN
MY_EMAIL = "24f1001016@ds.study.iitm.ac.in"

# Yeh function HAR request par automatically chalega
@app.middleware("http")
async def track_and_log_requests(request: Request, call_next):
    # Counter badhao
    http_requests_total.inc()
    
    # Log ka data banao
    request_id = str(uuid.uuid4())
    ts = datetime.utcnow().isoformat() + "Z"
    path = request.url.path
    
    log_entry = {
        "level": "INFO",
        "ts": ts,
        "path": path,
        "request_id": request_id
    }
    log_storage.append(log_entry)
    
    # Request ko aage process hone do
    response = await call_next(request)
    return response

# Endpoints
@app.get("/work")
async def do_work(n: int = 0):
    return {"email": MY_EMAIL, "done": n}

@app.get("/metrics")
async def metrics():
    # Prometheus format mein data return karna
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
async def healthz():
    uptime_s = time.time() - START_TIME
    return {"status": "ok", "uptime_s": uptime_s}

@app.get("/logs/tail")
async def logs_tail(limit: int = 10):
    # Aakhri 'limit' logs return karna
    logs_list = list(log_storage)
    return logs_list[-limit:]
