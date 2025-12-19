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

# Note:
If you want an additional verification pass, the next practical step would be: create a fresh empty DB, apply database/schema.sql, and then run uv run python manage.py migrate to ensure migrations are either no-ops or compatible (that’s a slightly more invasive check because it involves DB state changes).
