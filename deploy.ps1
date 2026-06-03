$repo = $PSScriptRoot
$claudeDir = "$env:USERPROFILE\.claude"

# Probe whether symlinks are available by attempting one in a temp location
function Test-SymlinkSupport {
    $tmp = Join-Path $env:TEMP "symlink-probe-$(New-Guid)"
    try {
        New-Item -ItemType SymbolicLink -Path $tmp -Target $env:TEMP -ErrorAction Stop | Out-Null
        Remove-Item $tmp -Force
        return $true
    } catch {
        return $false
    }
}

$useSymlinks = Test-SymlinkSupport

if (-not $useSymlinks) {
    Write-Host ""
    Write-Host "Symlinks are not available (requires Developer Mode or admin)."
    Write-Host "  Enable: Settings -> System -> For developers -> Developer Mode"
    Write-Host ""
    $choice = Read-Host "Enable symlinks first, then re-run — or proceed with junctions/hardlinks? [s=stop, j=junctions]"
    if ($choice -ne 'j') {
        Write-Host "Aborted. Re-run after enabling Developer Mode."
        exit 1
    }
    Write-Host "Proceeding with junctions/hardlinks..."
    Write-Host ""
}

function Link-File($path, $target) {
    if (Test-Path $path) {
        Write-Host "Skipping $(Split-Path $path -Leaf) — already exists (remove to redeploy)"
        return
    }
    if ($useSymlinks) {
        New-Item -ItemType SymbolicLink -Path $path -Target $target | Out-Null
        Write-Host "Symlinked $(Split-Path $path -Leaf)"
    } else {
        New-Item -ItemType HardLink -Path $path -Target $target | Out-Null
        Write-Host "Hardlinked $(Split-Path $path -Leaf)"
    }
}

function Link-Dir($path, $target) {
    if (Test-Path $path) {
        Write-Host "Skipping $(Split-Path $path -Leaf)/ — already exists (remove to redeploy)"
        return
    }
    if ($useSymlinks) {
        New-Item -ItemType SymbolicLink -Path $path -Target $target | Out-Null
        Write-Host "Symlinked $(Split-Path $path -Leaf)/"
    } else {
        New-Item -ItemType Junction -Path $path -Target $target | Out-Null
        Write-Host "Junction $(Split-Path $path -Leaf)/"
    }
}

Link-File "$claudeDir\CLAUDE.md" "$repo\global\CLAUDE.md"
Link-Dir  "$claudeDir\rules"     "$repo\global\rules"

Write-Host ""
Write-Host "For Copilot in repos: run this script from the repo root with a .claude\ target"
