# Запуск из каталога rsk_local: .\scripts\run-all-docker-tests.ps1
$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { Get-Location }
Set-Location $Root

$compose = Join-Path $Root "docker-compose.tests.yml"
if (-not (Test-Path $compose)) {
    Write-Error "Не найден $compose"
    exit 1
}

Write-Host "=== docker compose build (тестовые образы) ===" -ForegroundColor Cyan
docker compose -f $compose build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$services = @("auth_tests", "teams_tests", "user_profile_tests", "frontend_tests")
foreach ($s in $services) {
    Write-Host "`n=== $s ===" -ForegroundColor Cyan
    docker compose -f $compose run --rm $s
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Падение: $s (код $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
}

Write-Host "`nВсе тесты в Docker прошли успешно." -ForegroundColor Green
