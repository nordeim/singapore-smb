cd backend
cp .env.example .env
uv sync --all-extras
createdb singapore_smb
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
