from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from app.conf.config import settings
# from app.routes import auth, search, profile, users
from front.routes import pages
from app.routes import auth, profile, upload_pdf, llm_endpoint
from sqlalchemy import text
from app.database.db import get_db
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="front/static"), name="static")
# app.mount("/sphinx", StaticFiles(directory="docs/_build/html"), name="sphinx")

app.include_router(auth.router, prefix='/api')
app.include_router(profile.router, prefix='/api')
app.include_router(upload_pdf.router, prefix='/api')
app.include_router(llm_endpoint.router, prefix='/llm')
app.include_router(pages.router, include_in_schema=False)


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to QPDoc API!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/api/", include_in_schema=False)
def root():
    return {"message": "Welcome to QPDoc API!"}


if __name__ == '__main__':
    # in order to run SSL version you need to generate certificate/private key pair
    # uvicorn.run("main:app", host='0.0.0.0', ssl_keyfile='key.pem', ssl_certfile='cert.pem')

    # development doesn't need SSL
    uvicorn.run("main:app", reload=True, port=settings.app_port, host='0.0.0.0', ssl_keyfile='key.pem', ssl_certfile='cert.pem')
