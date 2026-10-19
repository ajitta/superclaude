<#
.SYNOPSIS
  Install/upgrade audit, Windows owner check (docs/features/install-upgrade-audit/04a-handoff.md).

.DESCRIPTION
  Runs the scenarios U1, U4, I2 and E6 of the audit's matrix against this checkout,
  each in a throwaway sandbox under -Work. The real profile is never the target:
  USERPROFILE, HOME and CLAUDE_CONFIG_DIR point into the sandbox, the script aborts
  if Python resolves Path.home() anywhere else, and it compares the real
  ~\.claude before and after. Writes results.md under -Work; paste it back.

  Needs: git, uv/uvx on PATH, a healthy .venv in the checkout (uv pip install -e ".[dev]"),
  network for uvx to build the old releases. No claude binary is used.

  PYTHONIOENCODING=utf-8 is set so piped output survives the CLI's emoji; PYTHONUTF8 is
  NOT set, so file reads keep the locale defaults the audit wants to catch.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\install-audit-windows.ps1
  pwsh -File scripts\install-audit-windows.ps1 -Only E6
#>
param(
  [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
  [string]$Work = (Join-Path $env:TEMP ("sc-install-audit-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))),
  [string[]]$Only = @('W6', 'U1', 'U4', 'I2', 'E6')
)

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$RealHome = [Environment]::GetFolderPath('UserProfile')
$Results = New-Object System.Collections.Generic.List[string]
$SavedEnv = @{}
foreach ($k in 'USERPROFILE', 'HOME', 'CLAUDE_CONFIG_DIR', 'PYTHONIOENCODING') { $SavedEnv[$k] = [Environment]::GetEnvironmentVariable($k) }

function Add-Result([string]$Id, [string]$Check, [bool]$Ok, [string]$Observed, [string]$Expect = '') {
  $mark = if ($Ok) { 'PASS' } else { 'FAIL' }
  $obs = ($Observed -replace '\|', '/' -replace "`r?`n", ' ')
  if ($obs.Length -gt 240) { $obs = $obs.Substring(0, 240) + '...' }
  $Results.Add("| $Id | $Check | $mark | $obs | $Expect |")
  Write-Host ("{0,-22} {1} {2}" -f $Id, $mark, $Check)
}

# --- real-profile guard ---------------------------------------------------
function Get-RealState {
  $c = Join-Path $RealHome '.claude'
  $state = @{}
  $s = Join-Path $c 'settings.json'
  $state.settings = if (Test-Path $s) { (Get-FileHash $s -Algorithm SHA256).Hash } else { 'absent' }
  $state.artifacts = @('CLAUDE.md', 'superclaude', 'commands\sc', 'agents', 'output-styles', 'agent-memory', '.superclaude_hooks') |
    Where-Object { Test-Path (Join-Path $c $_) }
  $j = Join-Path $RealHome '.claude.json'
  $state.mcp = 'absent'
  if (Test-Path $j) {
    try { $state.mcp = ((Get-Content $j -Raw | ConvertFrom-Json).mcpServers | ConvertTo-Json -Depth 8 -Compress) } catch { $state.mcp = 'unreadable' }
  }
  return $state
}
function Assert-RealUnchanged($Before) {
  $now = Get-RealState
  foreach ($k in 'settings', 'mcp') { if ($now[$k] -ne $Before[$k]) { throw "GUARD: real ~\.claude $k changed" } }
  if (($now.artifacts -join ',') -ne ($Before.artifacts -join ',')) { throw "GUARD: real ~\.claude artifacts changed: $($now.artifacts -join ',')" }
}

# --- sandbox ----------------------------------------------------------------
function New-Sandbox([string]$Name) {
  $sb = Join-Path $Work $Name
  if (Test-Path $sb) { Remove-Item -Recurse -Force $sb }
  $h = Join-Path $sb 'home'; $p = Join-Path $sb 'proj'
  New-Item -ItemType Directory -Force $h, $p | Out-Null
  git -C $p init -q -b main | Out-Null
  git -C $p config user.email sandbox@example.invalid
  git -C $p config user.name sandbox
  return [pscustomobject]@{ Root = $sb; Home = $h; Proj = $p }
}
function Enter-Sandbox($Sb) {
  $env:USERPROFILE = $Sb.Home; $env:HOME = $Sb.Home
  $env:CLAUDE_CONFIG_DIR = Join-Path $Sb.Home '.claude'
  $env:PYTHONIOENCODING = 'utf-8'
  Set-Location $Sb.Proj
  $seen = (& uv run --no-sync --project $Repo python -c "import pathlib; print(pathlib.Path.home())" 2>$null | Select-Object -Last 1)
  if ("$seen".Trim() -ne $Sb.Home) { throw "GUARD: Path.home() is '$seen', not the sandbox $($Sb.Home)" }
}
function Exit-Sandbox {
  foreach ($k in $SavedEnv.Keys) { [Environment]::SetEnvironmentVariable($k, $SavedEnv[$k]) }
  Set-Location $Repo
}
function Get-Base($Sb, [string]$Scope) { if ($Scope -eq 'user') { Join-Path $Sb.Home '.claude' } else { Join-Path $Sb.Proj '.claude' } }
function Get-Settings($Sb, [string]$Scope) { Join-Path (Get-Base $Sb $Scope) $(if ($Scope -eq 'local') { 'settings.local.json' } else { 'settings.json' }) }
function Get-ClaudeMd($Sb, [string]$Scope) { if ($Scope -eq 'local') { Join-Path $Sb.Proj 'CLAUDE.local.md' } else { Join-Path (Get-Base $Sb $Scope) 'CLAUDE.md' } }

function Invoke-Native([string[]]$Cmd) {
  $out = ($null | & $Cmd[0] $Cmd[1..($Cmd.Length - 1)] 2>&1 | ForEach-Object { "$_" }) -join "`n"
  return [pscustomobject]@{ Rc = $LASTEXITCODE; Out = $out }
}
function Invoke-Sc([string[]]$ScArgs) { Invoke-Native (@('uv', 'run', '--no-sync', '--project', $Repo, 'superclaude') + $ScArgs) }

$OldSrc = @{}
function Install-Old($Sb, [string]$Ref, [string]$Scope) {
  if (-not $OldSrc.ContainsKey($Ref)) {
    $sha = (git -C $Repo rev-parse --short=8 "$Ref^{commit}").Trim()
    $dir = Join-Path $Work "src-$sha"
    if (-not (Test-Path (Join-Path $dir 'pyproject.toml'))) {
      $zip = "$dir.zip"
      git -C $Repo archive --format=zip -o $zip $sha
      Expand-Archive -Force $zip $dir
    }
    $OldSrc[$Ref] = $dir
  }
  Invoke-Native @('uvx', '--from', $OldSrc[$Ref], 'superclaude', 'install', '--scope', $Scope)
}

# Customizations C (the Linux harness's seed-C.sh, trimmed).
function Set-Customizations($Sb, [string]$Scope) {
  $b = Get-Base $Sb $Scope
  foreach ($d in 'agents', 'output-styles', 'skills\my-skill') { New-Item -ItemType Directory -Force (Join-Path $b $d) | Out-Null }
  $utf8 = New-Object Text.UTF8Encoding($false)
  # Fully indented: an inlined nested object is re-serialised by design (C-21 residual), so I2's byte check would fail on the seed, not on superclaude.
  [IO.File]::WriteAllText((Get-Settings $Sb $Scope), "{`n  `"model`": `"opus`",`n  `"hooks`": {`n    `"PreToolUse`": [`n      {`n        `"matcher`": `"Bash`",`n        `"hooks`": [`n          {`n            `"type`": `"command`",`n            `"command`": `"echo user-pre-bash`"`n          }`n        ]`n      }`n    ]`n  }`n}`n", $utf8)
  [IO.File]::WriteAllText((Join-Path $b 'agents\my-agent.md'), "---`nname: my-agent`ndescription: user agent`n---`nMine.`n", $utf8)
  [IO.File]::WriteAllText((Join-Path $b 'output-styles\my-style.md'), "---`nname: My Style`ndescription: user style`n---`nTerse.`n", $utf8)
  [IO.File]::WriteAllText((Join-Path $b 'skills\my-skill\SKILL.md'), "---`nname: my-skill`ndescription: user skill`n---`nDo it.`n", $utf8)
  [IO.File]::WriteAllText((Get-ClaudeMd $Sb $Scope), "# My rules`n`nAlways answer in English.`n", $utf8)
}
function Get-Tree($Sb) {
  $map = @{}
  Get-ChildItem -Recurse -File -Force $Sb.Root | Where-Object { $_.FullName -notmatch '\\\.git\\(?!info\\exclude$)' } | ForEach-Object {
    $map[$_.FullName.Substring($Sb.Root.Length)] = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
  }
  return $map
}
function Compare-Tree($A, $B) {
  $d = @()
  foreach ($k in $A.Keys) { if (-not $B.ContainsKey($k)) { $d += "- $k" } elseif ($A[$k] -ne $B[$k]) { $d += "M $k" } }
  foreach ($k in $B.Keys) { if (-not $A.ContainsKey($k)) { $d += "+ $k" } }
  return $d
}
function Test-UserFiles($Sb, [string]$Scope) {
  $b = Get-Base $Sb $Scope
  $missing = @('agents\my-agent.md', 'output-styles\my-style.md', 'skills\my-skill\SKILL.md') | Where-Object { -not (Test-Path (Join-Path $b $_)) }
  $s = Get-Content -Raw (Get-Settings $Sb $Scope) -ErrorAction SilentlyContinue
  if ($s -notmatch 'echo user-pre-bash' -or $s -notmatch '"model"') { $missing += 'settings user keys/hook' }
  if ((Get-Content -Raw (Get-ClaudeMd $Sb $Scope) -ErrorAction SilentlyContinue) -notmatch 'Always answer in English') { $missing += 'CLAUDE text' }
  return $missing
}

# --- scenarios --------------------------------------------------------------
function Invoke-U1 {
  foreach ($scope in 'user', 'project', 'local') {
    $id = "U1-$scope"; $sb = New-Sandbox $id; Enter-Sandbox $sb
    try {
      Set-Customizations $sb $scope
      $o = Install-Old $sb 'v4.29.5' $scope
      Add-Result $id 'old v4.29.5 install' ($o.Rc -eq 0) "rc $($o.Rc)"
      $r = Invoke-Sc @('update', '--scope', $scope); Add-Result $id 'update exit 0' ($r.Rc -eq 0) "rc $($r.Rc)"
      $m = Test-UserFiles $sb $scope; Add-Result $id 'user files intact' (-not $m) ($m -join ', ')
      $r = Invoke-Sc @('verify-drift', '--scope', $scope); Add-Result $id 'verify-drift exit 0 (Q9a)' ($r.Rc -eq 0) (($r.Out -split "`n" | Select-String 'drift|EXTRA') -join '; ')
      $r = Invoke-Sc @('doctor', '--scope', $scope); Add-Result $id 'doctor healthy' ($r.Rc -eq 0) (($r.Out -split "`n" | Select-String 'healthy|failed|refus') -join '; ')
    } finally { Exit-Sandbox }
  }
}

function Invoke-U4 {
  $id = 'U4'; $sb = New-Sandbox $id; Enter-Sandbox $sb
  try {
    Set-Customizations $sb 'local'
    $o = Install-Old $sb '19575ac4^' 'local'; Add-Result $id 'old 19575ac4^ local install' ($o.Rc -eq 0) "rc $($o.Rc)"
    $mem = Join-Path $sb.Proj '.claude\agent-memory-local\my-agent'; New-Item -ItemType Directory -Force $mem | Out-Null
    Set-Content -Path (Join-Path $mem 'MEMORY.md') -Value 'remember this'
    $st = Join-Path $sb.Home '.claude\.superclaude_hooks'; New-Item -ItemType Directory -Force $st | Out-Null
    Set-Content -Path (Join-Path $st 'loop_guard_abc.json') -Value '{}'
    $r = Invoke-Sc @('install', '--scope', 'local'); Add-Result $id 'install exit 0, no traceback' ($r.Rc -eq 0 -and $r.Out -notmatch 'Traceback') "rc $($r.Rc)"
    $s = Get-Content -Raw (Get-Settings $sb 'local')
    Add-Result $id 'legacy python ...\scripts\x.py registrations rewritten' ($s -notmatch 'superclaude[\\/]+scripts') (([regex]::Matches($s, '"command":\s*"[^"]*scripts[^"]*"') | ForEach-Object { $_.Value }) -join '; ')
    $r = Invoke-Sc @('doctor', '--scope', 'local'); Add-Result $id 'doctor exit 0' ($r.Rc -eq 0) (($r.Out -split "`n" | Select-String 'healthy|failed') -join '; ')
    $r = Invoke-Sc @('update', '--scope', 'local'); Add-Result $id 'update exit 0' ($r.Rc -eq 0) "rc $($r.Rc)"
    $r = Invoke-Sc @('uninstall', '--scope', 'local', '-y')
    # superclaude\scripts\ may stay on purpose (hook-upgrade-live-session); anything else SC-made may not.
    $left = @()
    if (Test-Path (Join-Path $sb.Proj '.claude\commands\sc')) { $left += 'commands\sc' }
    $scDir = Join-Path $sb.Proj '.claude\superclaude'
    if (Test-Path $scDir) { $left += Get-ChildItem -Force $scDir | Where-Object { $_.Name -ne 'scripts' } | ForEach-Object { "superclaude\$($_.Name)" } }
    Add-Result $id 'uninstall exit 0, no SC content left but scripts\' ($r.Rc -eq 0 -and -not $left) ("rc $($r.Rc); " + ($left -join ', '))
    Add-Result $id 'non-empty agent-memory-local kept, lost exclude warned (Q11b)' ((Test-Path (Join-Path $mem 'MEMORY.md')) -and $r.Out -match 'agent-memory-local') "warned: $($r.Out -match 'agent-memory-local')"
    Add-Result $id '~\.claude\.superclaude_hooks reported (C-17, S3: FAIL expected)' ($r.Out -match '\.superclaude_hooks') "mentioned: $($r.Out -match '\.superclaude_hooks')"
  } finally { Exit-Sandbox }
}

function Invoke-I2 {
  foreach ($scope in 'user', 'project', 'local') {
    $id = "I2-$scope"; $sb = New-Sandbox $id; Enter-Sandbox $sb
    try {
      Set-Customizations $sb $scope
      $pre = Get-Tree $sb
      $r = Invoke-Sc @('install', '--scope', $scope); Add-Result $id 'install exit 0' ($r.Rc -eq 0) "rc $($r.Rc)"
      $r = Invoke-Sc @('uninstall', '--scope', $scope, '-y'); Add-Result $id 'uninstall exit 0' ($r.Rc -eq 0) "rc $($r.Rc)"
      $d = Compare-Tree $pre (Get-Tree $sb)
      $other = $d | Where-Object { $_ -notmatch 'settings(\.local)?\.json$|CLAUDE(\.local)?\.md$' }
      Add-Result $id 'tree after uninstall == before install, outside settings/CLAUDE files' (-not $other) ($other -join ', ')
      $m = Test-UserFiles $sb $scope; Add-Result $id 'user files and settings keys intact' (-not $m) ($m -join ', ')
      Add-Result $id 'settings/CLAUDE bytes identical (C-20/C-21 fixed: PASS expected)' (-not $d) ($d -join ', ')
    } finally { Exit-Sandbox }
  }
}

function Get-Head([string]$Path) {
  $b = [IO.File]::ReadAllBytes($Path)
  return ('{0:X2} {1:X2} {2:X2}' -f $b[0], $b[1], $b[2])
}
function ConvertTo-Encoding([string]$Path, [string]$Enc) {
  $text = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8)
  switch ($Enc) {
    'utf-16' { [IO.File]::WriteAllText($Path, $text, [Text.Encoding]::Unicode) }
    'utf-8-bom' { [IO.File]::WriteAllText($Path, $text, (New-Object Text.UTF8Encoding($true))) }
    'cp949' {
      # ASCII-only source: PowerShell 5.1 reads a BOM-less script in the ANSI code page.
      $note = "$([char]0xD55C)$([char]0xAE00) $([char]0xFC)"
      try { $e = [Text.Encoding]::GetEncoding(949) } catch { $e = [Text.Encoding]::GetEncoding(1252) }
      [IO.File]::WriteAllText($Path, ($text -replace '\}\s*$', ", `"note`": `"$note`"}"), $e)
    }
  }
  return (Get-Head $Path)
}

# W6 (second half): what does this PowerShell's Out-File and Set-Content write by default?
function Invoke-W6 {
  $p = Join-Path $Work 'w6-probe.json'
  '{"model": "opus"}' | Out-File -FilePath $p
  Add-Result 'W6' "Out-File default encoding (FF FE = UTF-16LE, EF BB BF = UTF-8 BOM)" $true (Get-Head $p)
  '{"model": "opus"}' | Set-Content -Path $p
  Add-Result 'W6' "Set-Content default encoding" $true (Get-Head $p)
}

function Invoke-E6 {
  foreach ($scope in 'user', 'project', 'local') {
    foreach ($enc in 'utf-16', 'utf-8-bom', 'cp949') {
      foreach ($cmd in 'install', 'update', 'uninstall', 'doctor') {
        $id = "E6-$scope-$enc-$cmd"; $sb = New-Sandbox $id; Enter-Sandbox $sb
        try {
          $null = Invoke-Sc @('install', '--scope', $scope)
          $head = ConvertTo-Encoding (Get-Settings $sb $scope) $enc
          $pre = Get-Tree $sb
          $a = @($cmd, '--scope', $scope); if ($cmd -eq 'uninstall') { $a += '-y' }
          $r = Invoke-Sc $a
          $d = Compare-Tree $pre (Get-Tree $sb)
          $why = ($r.Out -split "`n" | Select-String 'UTF|BOM|Nothing was changed' | Select-Object -First 2) -join '; '
          Add-Result $id "exit 1, nothing changed (Q16a); first bytes $head" ($r.Rc -eq 1 -and -not $d -and $r.Out -notmatch 'Traceback') "rc $($r.Rc); changed $($d.Count); $why"
        } finally { Exit-Sandbox }
      }
    }
  }
}

# --- main -------------------------------------------------------------------
New-Item -ItemType Directory -Force $Work | Out-Null
$before = Get-RealState
Write-Host "Sandbox root: $Work"
Write-Host "PowerShell $($PSVersionTable.PSVersion); $(git --version); $(uv --version)"
try {
  foreach ($s in $Only) { & "Invoke-$s"; Assert-RealUnchanged $before }
} finally {
  Exit-Sandbox
  Assert-RealUnchanged $before
  Write-Host 'GUARD: real profile unchanged'
}
$md = @("# Install/upgrade audit, Windows run", '',
  "PowerShell $($PSVersionTable.PSVersion); $(git --version); $(uv --version); repo $(git -C $Repo rev-parse --short HEAD)", '',
  '| ID | Check | Result | Observed | Expected |', '|---|---|---|---|---|') + $Results
$md | Set-Content -Encoding UTF8 (Join-Path $Work 'results.md')
Write-Host "Results: $(Join-Path $Work 'results.md')"
