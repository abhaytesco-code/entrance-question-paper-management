# Run script for LearnMatrix (PowerShell)
# Usage: Open PowerShell in project root and run: .\run.ps1

if (Test-Path .env) {
    Write-Host "Loading .env"
    Get-Content .env | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)\s*=\s*(.*)\s*$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            try {
                [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
            } catch {
                Write-Host ("Failed to set env var {0}: {1}" -f $name, $_) -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host ".env file not found. Copy .env.example to .env and update credentials." -ForegroundColor Yellow
}

Write-Host "Installing dependencies (if not already installed)..."
python -m pip install -r requirements.txt

Write-Host "Starting Flask app..."
python app.py
