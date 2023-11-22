# QPDoc - Query Processed Documents

## Steps to run the application without containerization

1. Clone the repository and navigate to its root directory:  
`git clone git@github.com:oleverse/qpdoc.git`  
`cd qpdoc`  
2. Create virtual environment and activate it:  
with `poetry`:  
`poetry shell`  
with `venv`:  
`python -m venv .venv`  
`source .venv/bin/activate`
3. Install packages:  
`poetry update`  
or  
`pip install -r requirements.txt`
4. Copy file `env_sample` to `.env` and change values to fit your needs  
5. You should have PosgreSQL database engine running. 
As a good example we recommend to run `postgres` in `docker` container.
For that purpose the repository has its `docker-compose.yaml` file.
Just run a command:  
`docker compose up -d`  
6. Check that database is created and mentioned in `.env` file and run migrations:  
`alembic upgrade head`
7. Start the app by typing:  
`uvicorn main:app --reload`  
or run main module directly  
`python main.py`
8. Browse the app on `http://0.0.0.0:<port_from_env>`


## Dockerized version

We have an official Docker image at DockerHub.  
  
To run the app using Docker Compose:  
1. Download files `env_sample` and `docker-compose.yaml` from this repository  
2. Rename `env_sample` to `.env` and change values to fit your needs
3. Check if `.env` file values were correctly inserted using `docker compose config` command
4. Run `docker compose up -d`  
5. Check the app status with `docker ps` command and/or `docker logs <container-name>`  
6. Browse the app  
