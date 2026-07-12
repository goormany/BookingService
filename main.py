import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))


app = FastAPI()


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)