$LogPath = "D:\Documentos\Desarrollo\Django\start_django_wsl.log"
"--- Ejecutando script: $(Get-Date) ---" | Out-File -FilePath $LogPath -Append

# Este script inicia Docker Compose en tu proyecto de WSL
# Esperar hasta que WSL responda
$maxTries = 30
$tries = 0
$ready = $false

while (-not $ready -and $tries -lt $maxTries) {
    try {
        wsl.exe -d Ubuntu -- echo "ok" | Out-Null
        $ready = $true
    }
    catch {
        Start-Sleep -Seconds 2
        $tries++
    }
}

# Define la ruta de tu proyecto en el entorno de Windows
$projectPath = "D:\Documentos\Desarrollo\Django"

# Mapea la ruta de Windows a la ruta de WSL
$wslPath = "/mnt/d/Documentos/Desarrollo/Django"

# Ejecuta el comando docker-compose dentro de WSL
# El '-e' le dice a WSL que ejecute el comando en el directorio del script
wsl.exe -d Ubuntu -e /usr/bin/bash -c "cd "/mnt/d/Documentos/Desarrollo/Django" && docker compose up -d