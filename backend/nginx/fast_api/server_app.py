
from fastapi import FastAPI
import uvicorn
import socket
import os

app = FastAPI()

PORT = os.getenv("PORT", "8000")


@app.get("/")
def read_root():
    hostname = socket.gethostname()
    return {
        "message": "Hello from FastAPI",
        "server": hostname,
        "port": PORT
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
