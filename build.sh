#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
pip install playwright
python -m playwright install chromium
python -m playwright install-deps chromium

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py generate_thumbnails
