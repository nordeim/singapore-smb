# run
```bash
docker compose --env-file .env.docker up -d postgres redis
```
and then execute migrations. 

```bash
# migrate:
set -a && source ../.env.docker && set +a && uv run python manage.py migrate
# seed:
set -a && source ../.env.docker && set +a && uv run python manage.py seed
# pytest:
set -a && source ../.env.docker && set +a && uv run python -m pytest -q
# 
# set -a && source ../.env.docker && set +a && uv run python -m pytest -q apps/accounts/tests/test_models.py::TestCompanyModel::test_company_settings_json apps/accounts/tests/test_models.py::TestCompanyModel::test_soft_delete apps/accounts/tests/test_services.py::TestUserService::test_update_user
# set -a && source ../.env.docker && set +a && uv run python -m pytest -q
```
