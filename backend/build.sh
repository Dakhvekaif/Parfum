#!/usr/bin/env bash
# Render build script — runs on every deploy
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser from env vars (skips if already exists)
python manage.py create_superuser_env

# Seed sample data (only creates if data doesn't exist)
python manage.py seed_data
