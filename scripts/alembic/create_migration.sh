#!/bin/bash

read -p "Enter name of migration: " message
docker compose exec app alembic revision --autogenerate -m "$message"
