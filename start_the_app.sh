#!/bin/bash
# This file is used in Dockerfile to bootstrap the application when its container is up.

# wait for the db container to start resolving via Docker network
sleep 5
alembic upgrade head
python main.py