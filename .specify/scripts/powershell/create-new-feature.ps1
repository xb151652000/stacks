param(
    [Parameter(Mandatory=$true)]
    [string]$Json,
    [int]$Number = 1,
    [string]$ShortName = "",
    [switch]$jsonOutput = $false
)

$ErrorActionPreference = "Stop"

$featureDescription = $Json

if ($ShortName -eq "") {
    Write-Error "ShortName is required"
    exit 1
}

$branchName = "$Number-$ShortName"
$featureDir = "specs\$branchName"
$specFile = "$featureDir\spec.md"

Write-Host "Creating feature branch: $branchName"
Write-Host "Feature directory: $featureDir"
Write-Host "Spec file: $specFile"

try {
    if (-not (Test-Path $featureDir)) {
        New-Item -ItemType Directory -Force -Path $featureDir | Out-Null
        Write-Host "Created directory: $featureDir"
    }

    if (-not (Test-Path $specFile)) {
        New-Item -ItemType File -Force -Path $specFile | Out-Null
        Write-Host "Created spec file: $specFile"
    }

    $result = @{
        BRANCH_NAME = $branchName
        SPEC_FILE = $specFile
        FEATURE_DIR = $featureDir
        SUCCESS = $true
    }

    if ($jsonOutput) {
        $result | ConvertTo-Json -Depth 10
    } else {
        Write-Host "Feature setup complete!"
        Write-Host "Branch: $branchName"
        Write-Host "Spec file: $specFile"
    }
} catch {
    Write-Error "Failed to create feature: $_"
    exit 1
}
