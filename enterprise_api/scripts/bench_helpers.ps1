function Import-BenchEnv {
  param([string]$Path = (Join-Path $PSScriptRoot '.env.bench'))
  if (Test-Path $Path) {
    Get-Content $Path | ForEach-Object {
      if ($_ -match '^[A-Za-z_][A-Za-z0-9_]*=') {
        $name,$val = $_ -split '=',2
        [Environment]::SetEnvironmentVariable($name, $val, 'Process')
      }
    }
  }
}

function Ensure-Dir {
  param([string]$Path)
  if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }
}

function Start-CpuLog {
  param(
    [string]$Name,
    [string]$OutDir = (Join-Path $PSScriptRoot 'bench_logs')
  )
  Ensure-Dir -Path $OutDir
  $ts = Get-Date -Format 'yyyyMMdd_HHmmss'
  $file = Join-Path $OutDir ("{0}_{1}.csv" -f $Name,$ts)
  $counter = '\Processor(_Total)\% Processor Time'
  $proc = Start-Process -WindowStyle Hidden -FilePath 'typeperf.exe' -ArgumentList @($counter,'-si','1','-f','CSV','-o',$file,'-y') -PassThru
  return @{ Pid = $proc.Id; File = $file }
}

function Stop-CpuLog {
  param([Alias('Pid')][int]$ProcessId)
  if ($ProcessId) {
    try { Stop-Process -Id $ProcessId -Force } catch {}
  }
}

function Get-AvgCpuFromCsv {
  param([string]$CsvPath)
  if (-not (Test-Path $CsvPath)) { return 0 }
  $rows = Get-Content $CsvPath
  if ($rows.Count -lt 3) { return 0 }
  $data = $rows | Select-Object -Skip 2 | ConvertFrom-Csv
  if (-not $data) { return 0 }
  $col = ($data | Get-Member -MemberType NoteProperty | Select-Object -Last 1 -ExpandProperty Name)
  $vals = @()
  foreach ($row in $data) {
    $s = $row.$col
    if ($s -is [string]) { $s = $s.Replace(',', '.') }
    try { $v = [double]::Parse($s, [System.Globalization.CultureInfo]::InvariantCulture); $vals += $v } catch {}
  }
  if ($vals.Count -eq 0) { return 0 }
  return [math]::Round(($vals | Measure-Object -Average).Average, 2)
}
