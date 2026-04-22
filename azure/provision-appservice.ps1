param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$Location,

    [Parameter(Mandatory = $true)]
    [string]$AppServicePlan,

    [Parameter(Mandatory = $true)]
    [string]$WebAppName,

    [Parameter(Mandatory = $true)]
    [string]$PostgresServerName,

    [Parameter(Mandatory = $true)]
    [string]$PostgresDatabaseName,

    [Parameter(Mandatory = $true)]
    [string]$PostgresAdminUser,

    [Parameter(Mandatory = $true)]
    [string]$PostgresAdminPassword,

    [string]$PythonRuntime = "PYTHON|3.11",
    [string]$AppServiceSku = "B1",
    [string]$SettingsFile = ".\\azure\\appsettings.production.sample.json"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating resource group $ResourceGroup in $Location..."
az group create `
  --name $ResourceGroup `
  --location $Location | Out-Null

Write-Host "Creating Linux App Service plan $AppServicePlan..."
az appservice plan create `
  --name $AppServicePlan `
  --resource-group $ResourceGroup `
  --location $Location `
  --sku $AppServiceSku `
  --is-linux | Out-Null

Write-Host "Creating App Service web app $WebAppName..."
az webapp create `
  --name $WebAppName `
  --resource-group $ResourceGroup `
  --plan $AppServicePlan `
  --runtime $PythonRuntime | Out-Null

Write-Host "Setting startup command..."
az webapp config set `
  --resource-group $ResourceGroup `
  --name $WebAppName `
  --startup-file "bash startup.sh" | Out-Null

Write-Host "Creating PostgreSQL Flexible Server $PostgresServerName..."
az postgres flexible-server create `
  --resource-group $ResourceGroup `
  --location $Location `
  --name $PostgresServerName `
  --database-name $PostgresDatabaseName `
  --admin-user $PostgresAdminUser `
  --admin-password $PostgresAdminPassword `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --version 16 `
  --yes | Out-Null

Write-Host "Reading app settings template from $SettingsFile..."
$settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json

$postgresConnection = "postgresql+psycopg://$PostgresAdminUser`:$PostgresAdminPassword@$PostgresServerName.postgres.database.azure.com:5432/$PostgresDatabaseName"

foreach ($setting in $settings) {
    if ($setting.name -eq "DATABASE_URL") {
        $setting.value = $postgresConnection
    }
}

$settingsArgs = @()
foreach ($setting in $settings) {
    $settingsArgs += "$($setting.name)=$($setting.value)"
}

Write-Host "Applying app settings..."
az webapp config appsettings set `
  --resource-group $ResourceGroup `
  --name $WebAppName `
  --settings $settingsArgs | Out-Null

Write-Host "Provisioning complete."
Write-Host "Web App: https://$WebAppName.azurewebsites.net"
Write-Host "Next steps:"
Write-Host "1. Configure Microsoft Entra authentication in App Service."
Write-Host "2. Replace placeholder bot settings and any secrets with real values."
Write-Host "3. Add GitHub secrets and run the deployment workflow."
