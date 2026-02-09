
from fastapi import FastAPI
import uvicorn
import socket

app = FastAPI()


@app.get("/")
def read_root():
    hostname = socket.gethostname()
    return {
        "message": "Hello from FastAPI",
        "server": hostname,
        "port": "8000"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
