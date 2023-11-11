FROM python:3.10.13-slim

RUN useradd -m qpdoc
WORKDIR /home/qpdoc
COPY .env pyproject.toml README.md LICENSE .
COPY . $WORKDIR
RUN chown -R qpdoc:qpdoc /home/qpdoc
RUN chmod 0400 key.pem
USER qpdoc

ENV PATH="$PATH:/home/qpdoc/.local/bin"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt


ENTRYPOINT ["python", "main.py"]
#ENTRYPOINT uvicorn main:app --host 0.0.0.0 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

CMD alembic upgrade head

