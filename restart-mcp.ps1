#!/usr/bin/env powershell
# MCP SQLite Memory Bank Restart Script

Write-Host "🔄 Restarting MCP SQLite Memory Bank Server..." -ForegroundColor Yellow

# Force refresh the uvx cache for latest version
Write-Host "📦 Refreshing package cache..." -ForegroundColor Cyan
uvx --refresh mcp-sqlite-memory-bank --help | Out-Null

# Test if the server starts correctly
Write-Host "🧪 Testing server startup..." -ForegroundColor Cyan
$test = Start-Process -FilePath "uvx" -ArgumentList "mcp-sqlite-memory-bank" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2
if (!$test.HasExited) {
    $test.Kill()
    Write-Host "✅ Server test successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Server test failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 MCP SQLite Memory Bank is ready!" -ForegroundColor Green
Write-Host "📝 To restart in VS Code: Ctrl+Shift+P → 'MCP: Restart Server'" -ForegroundColor Blue
