import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to qpdoc API!"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000)
