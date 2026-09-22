[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $PSScriptRoot "napcat"),
    [string]$Version = "latest",
    [string]$DownloadUrl = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[NapCat] $Message" -ForegroundColor Cyan
}

function Get-ReleaseAsset {
    param([string]$ReleaseVersion)

    $releaseUri = if ($ReleaseVersion -eq "latest") {
        "https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest"
    } else {
        "https://api.github.com/repos/NapNeko/NapCatQQ/releases/tags/$ReleaseVersion"
    }

    Write-Step "正在查询 NapCatQQ 发布版本：$ReleaseVersion"
    $release = Invoke-RestMethod -Uri $releaseUri -Headers @{ Accept = "application/vnd.github+json" }
    $asset = @($release.assets | Where-Object { $_.name -match '\.zip$' } | Select-Object -First 1)

    if (-not $asset) {
        throw "发布版本 $($release.tag_name) 没有找到 .zip 安装包。请使用 -DownloadUrl 指定下载地址。"
    }

    return $asset
}

try {
    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "joha-napcat"
    $archivePath = Join-Path $tempDir "napcat.zip"

    if (Test-Path $InstallDir) {
        if (-not $Force) {
            $existingItems = @(Get-ChildItem -LiteralPath $InstallDir -Force)
            if ($existingItems.Count -gt 0) {
                throw "安装目录不为空：$InstallDir。若要覆盖，请添加 -Force。"
            }
        } else {
            Write-Step "清理现有安装目录：$InstallDir"
            Remove-Item -LiteralPath $InstallDir -Recurse -Force
        }
    }

    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

    if ([string]::IsNullOrWhiteSpace($DownloadUrl)) {
        $asset = Get-ReleaseAsset -ReleaseVersion $Version
        $DownloadUrl = $asset.browser_download_url
        Write-Step "找到安装包：$($asset.name)"
    }

    Write-Step "正在下载：$DownloadUrl"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $archivePath

    if ((Get-Item -LiteralPath $archivePath).Length -eq 0) {
        throw "下载的安装包为空。"
    }

    Write-Step "正在解压到：$InstallDir"
    Expand-Archive -LiteralPath $archivePath -DestinationPath $InstallDir -Force

    Write-Step "NapCatQQ 安装完成。"
    Write-Host "安装目录：$InstallDir" -ForegroundColor Green
    Write-Host "请在 NapCatQQ 中开启 OneBot WebSocket，并将 Joha 的 ws_url 配置为对应地址。"
} catch {
    Write-Error "NapCatQQ 安装失败：$($_.Exception.Message)"
    exit 1
} finally {
    if (Test-Path $tempDir) {
        Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
