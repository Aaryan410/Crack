import os
import pickle
import base64

import redis

_REDIS_URL = os.getenv("KV_URL") or os.getenv("REDIS_URL")

_client = None
if _REDIS_URL:
    _client = redis.from_url(_REDIS_URL)

SESSION_TTL_SECONDS = 60 * 60 * 2

def _require_client():
    if _client is None:
        raise RuntimeError (
            "No KV_URL / REDIS_URL configured. Attach a Vercel KV store "
            "to this project (or set REDIS_URL locally) before running."
        )
    return _client

def save_interview(interview_id, engine, session):
    client = _require_client()

    payload = pickle.dumps({"engine": engine, "session": session})
    encoded = base64.b64encode(payload)

    client.set(f"interview:{interview_id}", encoded, ex=SESSION_TTL_SECONDS)

def load_interview(interview_id):
    if interview_id is None:
        return None, None

    client = _require_client()

    raw = client.get(f"interview:{interview_id}")
    if raw is None:
        return None, None
    
    payload = pickle.loads(base64.b64decode(raw))
    return payload["engine"], payload["session"]

def delete_interview(interview_id):
    if interview_id is None:
        return 

    client = _require_client()
    client.delete(f"interview:{interview_id}")
