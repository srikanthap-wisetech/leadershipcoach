# LeadWise Deployment Checklist

## 1. Prepare the application

- Install production dependencies from `requirements.txt`
- Use `startup.sh` as the production startup command
- Set `APP_ENVIRONMENT=production`
- Set `APP_BASE_URL` to the production URL
- Set `WEB_CONCURRENCY` based on the App Service plan size

## 2. Provision Azure resources

- Create a resource group
- Create an Azure App Service plan (Linux)
- Create an Azure App Service web app
- Create Azure Database for PostgreSQL Flexible Server
- Create Application Insights / Log Analytics
- Create Azure Key Vault
- Optional: create Azure Communication Services Email or SendGrid

## 3. Configure authentication

- Enable App Service Authentication
- Configure Microsoft Entra as the identity provider
- Restrict access to users in your organization
- Decide the group-based mapping for:
  - Leaders
  - Administrators
  - People Leadership

## 4. Configure app settings

Set these application settings in App Service:

- `APP_ENVIRONMENT=production`
- `APP_BASE_URL=https://<your-domain>`
- `WEB_CONCURRENCY=2` or higher
- `DATABASE_URL=postgresql+psycopg://...`
- `BOOTSTRAP_JSON_TO_DATABASE=false` after the first migration cutover
- `LEADWISE_DATA_DIR=/home/data` only as a temporary bridge if JSON storage is still being used
- `MICROSOFT_APP_ID`
- `MICROSOFT_APP_PASSWORD`
- `MICROSOFT_APP_TYPE`
- `MICROSOFT_APP_TENANT_ID`

You can start from:

- `azure/appsettings.production.sample.json`

## 5. Configure startup

Set the App Service startup command to:

```bash
startup.sh
```

If App Service requires the explicit command instead, use:

```bash
gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT app.main:app
```

## 6. Database readiness

- Create the PostgreSQL server
- Set `DATABASE_URL` in App Service
- Use `BOOTSTRAP_JSON_TO_DATABASE=true` once if you want to seed PostgreSQL from the current JSON-backed store
- Verify the database-backed app starts cleanly
- Turn `BOOTSTRAP_JSON_TO_DATABASE=false` after the initial cutover
- Plan the next step from the current generic record store to a normalized production schema

## 7. Security and secrets

- Move secrets into Key Vault
- Reference secrets from App Service
- Disable public write access to anything not needed
- Use HTTPS only
- Keep TLS minimums enabled

## 8. Operational readiness

- Enable App Service logs
- Enable Application Insights
- Test health endpoint
- Create alerts for app failure, exceptions, and high error rate
- Add backup and restore validation

## 9. Release process

- Add GitHub repository secrets:
  - `AZURE_CREDENTIALS`
  - `AZURE_RESOURCE_GROUP`
  - `AZURE_WEBAPP_NAME`
- Create a staging slot
- Deploy first to staging
- Verify:
  - landing page
  - journal
  - community
  - my activity
  - actions page
  - admin pages
  - authentication
  - redirects and theme handling
- Swap staging to production

The repository now includes a starter workflow:

- `.github/workflows/deploy-azure-appservice.yml`

## 10. Recommended first production milestone

### Good first milestone

- deploy to App Service
- use Entra sign-in
- keep internal-only access
- use temporary env-configurable storage only for evaluation

### True production milestone

- PostgreSQL-backed persistence
- real role mapping
- real email delivery
- CI/CD pipeline
- monitoring and rollback readiness
