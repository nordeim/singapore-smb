```bash
set -a && source ../.env.docker && set +a && uv run python -c "import config.celery; print('celery import OK')"
set -a && source ../.env.docker && set +a && uv run python manage.py check
```
