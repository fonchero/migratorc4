param(
    [string]$carpetaProyecto
)

Write-Host "`nValidando compilación en: $carpetaProyecto" -ForegroundColor Cyan

if (-Not (Test-Path "$carpetaProyecto\pom.xml")) {
    Write-Host "`nNo se encontró el pom.xml en: $carpetaProyecto" -ForegroundColor Yellow
    exit 1
}

Push-Location $carpetaProyecto

# Ejecutar mvn clean package sin tests
$mvnOutput = mvn clean package -DskipTests -B -ntp 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nCompilación exitosa de: $carpetaProyecto" -ForegroundColor Green
} else {
    Write-Host "`nError en la compilación. Revisa los mensajes anteriores." -ForegroundColor Red
    $mvnOutput | Out-File -FilePath "$carpetaProyecto\compilacion_error.log" -Encoding utf8
}

Pop-Location
