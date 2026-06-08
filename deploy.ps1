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
Link-Dir  "$claudeDir\skills"    "$repo\skills"

# Link plugins into the skills directory so Claude Code auto-loads them as <name>@skills-dir.
# ~/.claude/skills is already symlinked to $repo\skills, so a junction here is enough.
Link-Dir "$repo\skills\feature-dev" "$repo\plugins\feature-dev"
Link-Dir "$repo\skills\test-forge"  "$repo\plugins\test-forge"

# Also register in installed_plugins.json so VS Code Copilot can resolve agents from the plugin.
function Register-LocalPlugin($name, $pluginPath) {
    $jsonPath = "$claudeDir\plugins\installed_plugins.json"
    $key = "$name@local"
    $installed = Get-Content $jsonPath -Raw | ConvertFrom-Json -AsHashtable
    if (-not $installed.ContainsKey('plugins')) { $installed['plugins'] = @{} }
    if ($installed['plugins'].ContainsKey($key)) {
        Write-Host "Plugin $key already registered"
        return
    }
    $installed['plugins'][$key] = @(
        @{
            scope       = 'user'
            installPath = $pluginPath
            version     = 'unknown'
            installedAt = (Get-Date -Format 'o' -AsUTC)
            lastUpdated = (Get-Date -Format 'o' -AsUTC)
        }
    )
    $installed | ConvertTo-Json -Depth 10 | Set-Content $jsonPath -Encoding UTF8
    Write-Host "Registered $key in installed_plugins.json -> $pluginPath"
}

Register-LocalPlugin "feature-dev" "$repo\plugins\feature-dev"
Register-LocalPlugin "test-forge"  "$repo\plugins\test-forge"

# Register local plugins in VS Code Copilot settings
function Register-VSCodePlugin($pluginPath) {
    $vscodePaths = @(
        "$env:APPDATA\Code\User\settings.json",
        "$env:APPDATA\Code - Insiders\User\settings.json"
    )
    foreach ($settingsPath in $vscodePaths) {
        if (-not (Test-Path $settingsPath)) { continue }

        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
        if (-not $settings.ContainsKey('chat.pluginLocations')) {
            $settings['chat.pluginLocations'] = @{}
        }
        if (-not $settings['chat.pluginLocations'].ContainsKey($pluginPath)) {
            $settings['chat.pluginLocations'][$pluginPath] = $true
            $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
            Write-Host "Registered VS Code plugin -> $pluginPath ($(Split-Path $settingsPath -Leaf))"
        } else {
            Write-Host "VS Code plugin already registered -> $pluginPath"
        }
    }
}

Register-VSCodePlugin "$repo\plugins\feature-dev"
Register-VSCodePlugin "$repo\plugins\test-forge"

Write-Host ""
Write-Host "For Copilot in repos: run this script from the repo root with a .claude\ target"
