[CmdletBinding()]
param(
  [string]$Python = "..\..\.venv\Scripts\python.exe",
  [string]$Script = "fetch_binance_klines.py",
  [string]$Symbol = "ETHUSDT",
  [string]$Interval = "1m",
  [ValidateSet("full","incremental","daemon")][string]$Mode = "full",
  [Parameter(Mandatory = $true)][DateTime]$Start,
  [Parameter(Mandatory = $true)][DateTime]$End,
  [int]$SegmentDays = 30,
  [string[]]$ExtraArgs = @()
)

function Invoke-FetchWithProgress {
  [CmdletBinding()]
  param(
    [string]$Python = "..\..\.venv\Scripts\python.exe",
    [string]$Script = "fetch_binance_klines.py",
    [string]$Symbol = "ETHUSDT",
    [string]$Interval = "1m",
    [ValidateSet("full","incremental","daemon")][string]$Mode = "full",
    [Parameter(Mandatory = $true)][DateTime]$Start,
    [Parameter(Mandatory = $true)][DateTime]$End,
    [int]$SegmentDays = 30,
    [string[]]$ExtraArgs = @()
  )

  # Ensure running in script directory for relative paths
  try {
    $scriptDir = Split-Path -Parent $PSCommandPath
    if ($scriptDir -and (Test-Path $scriptDir)) {
      Push-Location $scriptDir
    }

    # Fallback to system python if venv python not found
    if (-not (Test-Path $Python)) {
      Write-Verbose "Specified Python not found at '$Python', falling back to 'python' from PATH."
      $Python = "python"
    }

    $total = [Math]::Ceiling((($End - $Start).TotalDays) / $SegmentDays)
    if ($total -lt 1) { $total = 1 }
    $seg = 0

    $args = @(
      $Script, "--symbol", $Symbol, "--interval", $Interval, "--mode", $Mode,
      "--start", ($Start.ToString("yyyy-MM-dd")), "--end", ($End.ToString("yyyy-MM-dd")),
      "--segment-days", $SegmentDays
    ) + $ExtraArgs

    & $Python -X utf8 @args 2>&1 | ForEach-Object {
      $line = $_
      if ($line -match '处理分段:') {
        $seg++
        $pct = [int](($seg / $total) * 100)
        if ($pct -gt 100) { $pct = 100 }
        Write-Progress -Activity "Fetching $Symbol $Interval ($Mode)" -Status ("{0}/{1} {2}" -f $seg, $total, $line) -PercentComplete $pct
      }
      elseif ($line -match '合并完成') {
        Write-Progress -Activity "Fetching $Symbol $Interval ($Mode)" -Status "合并完成" -PercentComplete 100
      }
      elseif ($line -match '限流|WARNING|ERROR') {
        Write-Host $line
      }
      $line
    }
  }
  finally {
    # Clear progress and restore location
    try { Write-Progress -Activity "Fetching $Symbol $Interval ($Mode)" -Status "完成" -PercentComplete 100 } catch {}
    try { Pop-Location } catch {}
  }
}

# If the script is executed directly (not dot-sourced), call the function with provided parameters
if ($MyInvocation.InvocationName -ne '.') {
  Invoke-FetchWithProgress -Python $Python -Script $Script -Symbol $Symbol -Interval $Interval -Mode $Mode -Start $Start -End $End -SegmentDays $SegmentDays -ExtraArgs $ExtraArgs
}