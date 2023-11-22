FROM python:3.11-slim

RUN useradd -m qpdoc
WORKDIR /home/qpdoc
COPY README.md LICENSE ./
RUN mkdir app
COPY app app/
COPY main.py $WORKDIR
COPY requirements.txt $WORKDIR
COPY start_the_app.sh $WORKDIR
COPY alembic.ini $WORKDIR
RUN mkdir front
COPY front front/
RUN mkdir migrations
COPY migrations migrations/
COPY Dockerfile $WORKDIR
COPY start_the_app.sh .local/bin/
RUN chown -R qpdoc:qpdoc /home/qpdoc
RUN mkdir ssl
USER qpdoc

ENV PATH="$PATH:/home/qpdoc/.local/bin"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt


ENTRYPOINT ["./start_the_app.sh"]
