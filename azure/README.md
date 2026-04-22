# LeadWise Azure Deployment Notes

This folder contains deployment scaffolding for running LeadWise in Azure App Service.

## Files

- `appsettings.production.sample.json`
  Sample App Service application settings file for production.
- `provision-appservice.ps1`
  Starter Azure CLI-based provisioning script for the App Service and PostgreSQL resources.

## GitHub Actions workflow

The repository includes:

- `.github/workflows/deploy-azure-appservice.yml`

This workflow:

- installs Python dependencies
- smoke tests the FastAPI import
- creates a ZIP deployment package
- deploys the app to Azure App Service
- sets the startup command to `bash startup.sh`

## Required GitHub secrets

Add these repository secrets before using the workflow:

- `AZURE_CREDENTIALS`
- `AZURE_RESOURCE_GROUP`
- `AZURE_WEBAPP_NAME`

## Notes

- `AZURE_CREDENTIALS` should contain the JSON output for a service principal that has deployment rights to the target resource group or web app.
- App settings should be applied in App Service or through your infrastructure process before the first production deployment.
- For the first PostgreSQL cutover, you can temporarily set `BOOTSTRAP_JSON_TO_DATABASE=true` if you want the app to seed the database from the current JSON store on first startup.

## Provisioning script example

```powershell
.\\azure\\provision-appservice.ps1 `
  -ResourceGroup rg-leadwise-dev `
  -Location australiaeast `
  -AppServicePlan asp-leadwise-dev `
  -WebAppName leadwise-dev `
  -PostgresServerName leadwise-dev-pg `
  -PostgresDatabaseName leadwise `
  -PostgresAdminUser leadwiseadmin `
  -PostgresAdminPassword "<secure-password>"
```

Use this script as a starter, not as the final hardening step. After provisioning, you should still:

- enable Microsoft Entra authentication
- move secrets to Key Vault
- review database networking and firewall settings
- configure staging slots and monitoring
