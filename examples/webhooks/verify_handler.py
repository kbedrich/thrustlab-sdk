"""Example FastAPI webhook handler verifying incoming events."""
import os
from fastapi import FastAPI, Request, HTTPException
from thrustlab import Webhook
from thrustlab.exceptions import SignatureVerificationError

app = FastAPI()
WEBHOOK_SECRET = os.environ["THRUSTLAB_WEBHOOK_SECRET"]


@app.post("/webhooks/thrustlab")
async def thrustlab_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Thrustlab-Signature", "")
    try:
        event = Webhook.verify(payload, sig, WEBHOOK_SECRET)
    except SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if event.type == "simulation.succeeded":
        sim_id = event.data["id"]
        # ... do work ...

    return {"received": True}
