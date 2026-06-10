$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

$filePath = $data.tool_input.file_path
if (-not $filePath -or -not $filePath.EndsWith('.md')) { exit 0 }

if (-not (Get-Command markdownlint -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine("markdown-lint: markdownlint CLI not found for `"$filePath`".`nInstall it with: npm install -g markdownlint-cli")
    exit 2
}

$configArgs = @()
foreach ($name in @('.markdownlint.json', '.markdownlint.jsonc', '.markdownlint.yaml', '.markdownlint.yml')) {
    $p = Join-Path $env:CLAUDE_PROJECT_DIR $name
    if (Test-Path $p) { $configArgs = @('--config', $p); break }
}

$result = & markdownlint @configArgs $filePath 2>&1
if ($LASTEXITCODE -eq 0) { exit 0 }

[Console]::Error.WriteLine("markdownlint issues in ${filePath}:`n`n${result}`n`nSuggest specific fixes for each violation above.")
exit 2
