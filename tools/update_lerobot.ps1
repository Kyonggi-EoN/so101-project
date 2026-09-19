<#
.SYNOPSIS
    third_party/lerobot 을 업스트림의 특정 커밋으로 교체한다.

.DESCRIPTION
    이 리포는 lerobot 파이썬 패키지를 복사해서 들고 있다(vendoring).
    버전을 올릴 때 손으로 하면 단계를 빠뜨리기 쉬워서 스크립트로 묶었다.

      1. 업스트림을 --depth 1 로 받는다 (312MB 히스토리를 받지 않는다)
      2. third_party/lerobot 을 통째로 교체한다 (덮어쓰기가 아니라 삭제 후 복사)
      3. 업스트림 pyproject.toml 의 의존성 diff 를 출력한다
      4. third_party/UPSTREAM.md 에 커밋 해시와 날짜를 기록한다

    pyproject.toml 은 자동으로 고치지 않는다. 3번 출력을 보고 사람이 판단한다.

.PARAMETER Rev
    업스트림 커밋 해시(40자 권장), 태그, 또는 브랜치 이름.

.EXAMPLE
    .\tools\update_lerobot.ps1 -Rev 5aa74557f84c54d4b458f8b9643c5aa2982acfed

    실행 후 이어서 해야 할 것:
      uv lock
      uv sync
      # 로봇 붙여서 teleoperate -> 짧은 녹화 -> rollout 검증
      git add -A; git commit -m "chore: bump lerobot"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Rev
)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/huggingface/lerobot.git"
$Root    = Split-Path -Parent $PSScriptRoot
$Dest    = Join-Path $Root "third_party\lerobot"
$Snap    = Join-Path $Root "third_party\upstream-pyproject.toml"
$Doc     = Join-Path $Root "third_party\UPSTREAM.md"
$Tmp     = Join-Path $env:TEMP ("lerobot-fetch-" + [guid]::NewGuid().ToString("N").Substring(0, 8))

function Get-DependencySection {
    # pyproject.toml 에서 [project] ~ [project.scripts] 구간만 뽑는다.
    # 이 구간에 dependencies 와 optional-dependencies 가 들어 있고,
    # 그 뒤 [tool.ruff] 같은 린터 설정은 우리와 무관하므로 비교 대상에서 뺀다.
    param([string]$Path)
    if (-not (Test-Path $Path)) { return @() }
    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    $start = ($lines | Select-String -SimpleMatch "[project]" | Select-Object -First 1).LineNumber
    $end   = ($lines | Select-String -SimpleMatch "[project.scripts]" | Select-Object -First 1).LineNumber
    if (-not $start) { return $lines }
    if (-not $end) { $end = $lines.Count }
    return $lines[($start - 1)..($end - 1)]
}

try {
    # ---- 1. 업스트림 받기 ----------------------------------------------------
    Write-Host "[1/4] 업스트림 $Rev 받는 중 (shallow)..." -ForegroundColor Cyan
    git init -q $Tmp
    git -C $Tmp remote add origin $RepoUrl
    git -C $Tmp fetch -q --depth 1 origin $Rev
    if ($LASTEXITCODE -ne 0) {
        throw "fetch 실패. -Rev 에 전체 40자 해시나 태그/브랜치 이름을 넣었는지 확인하세요."
    }
    git -C $Tmp checkout -q FETCH_HEAD

    $FullSha = (git -C $Tmp rev-parse HEAD).Trim()
    $CommitDate = (git -C $Tmp log -1 --format=%ad --date=short).Trim()
    $Src = Join-Path $Tmp "src\lerobot"
    if (-not (Test-Path $Src)) { throw "$Src 이 없습니다. 업스트림 구조가 바뀌었을 수 있습니다." }

    # ---- 2. 교체 -------------------------------------------------------------
    Write-Host "[2/4] third_party\lerobot 교체 중..." -ForegroundColor Cyan
    if (Test-Path $Dest) { Remove-Item -LiteralPath $Dest -Recurse -Force }
    Copy-Item -LiteralPath $Src -Destination $Dest -Recurse
    Get-ChildItem -LiteralPath $Dest -Recurse -Force -Directory |
        Where-Object { $_.Name -eq "__pycache__" } |
        Remove-Item -Recurse -Force
    $PyCount = (Get-ChildItem -LiteralPath $Dest -Recurse -Filter *.py).Count
    Write-Host "      .py 파일 $PyCount 개" -ForegroundColor DarkGray

    # ---- 3. 의존성 diff ------------------------------------------------------
    Write-Host "[3/4] 업스트림 의존성 변경 확인..." -ForegroundColor Cyan
    $NewPyproject = Join-Path $Tmp "pyproject.toml"
    $old = Get-DependencySection -Path $Snap
    $new = Get-DependencySection -Path $NewPyproject

    if ($old.Count -eq 0) {
        Write-Host "      이전 사본이 없어 비교를 건너뜁니다 (최초 실행)." -ForegroundColor DarkGray
    }
    else {
        $diff = Compare-Object -ReferenceObject $old -DifferenceObject $new
        if (-not $diff) {
            Write-Host "      변경 없음." -ForegroundColor Green
        }
        else {
            Write-Host ""
            Write-Host "  !! 업스트림이 의존성을 바꿨습니다 !!" -ForegroundColor Yellow
            foreach ($d in $diff) {
                $mark = "-"; $color = "Red"
                if ($d.SideIndicator -eq "=>") { $mark = "+"; $color = "Green" }
                Write-Host ("    {0} {1}" -f $mark, $d.InputObject) -ForegroundColor $color
            }
            Write-Host ""
            Write-Host "  -> pyproject.toml 에 반영할지 판단하세요." -ForegroundColor Yellow
            Write-Host "     우리가 바꾼 4곳은 pyproject.toml 상단 주석에 적혀 있습니다." -ForegroundColor Yellow
            Write-Host ""
        }
    }
    Copy-Item -LiteralPath $NewPyproject -Destination $Snap -Force

    # ---- 4. UPSTREAM.md 기록 -------------------------------------------------
    Write-Host "[4/4] UPSTREAM.md 갱신..." -ForegroundColor Cyan
    $today = Get-Date -Format "yyyy-MM-dd"
    $table = @(
        "| | |",
        "|---|---|",
        "| 원본 | https://github.com/huggingface/lerobot |",
        ("| 커밋 | ``{0}`` |" -f $FullSha),
        ("| 커밋 날짜 | {0} |" -f $CommitDate),
        ("| 가져온 날짜 | {0} |" -f $today),
        ("| 파일 수 | .py {0}개 |" -f $PyCount),
        "| 라이선스 | Apache-2.0 - ``third_party/LICENSE`` |"
    ) -join "`n"

    # 주의: PowerShell 변수는 대소문자를 구분하지 않는다.
    # 내용을 $doc 에 담으면 경로 변수 $Doc 을 덮어쓴다. 이름을 분리할 것.
    $docText = [System.IO.File]::ReadAllText($Doc)
    $pattern = "(?s)<!-- BEGIN:AUTO -->.*?<!-- END:AUTO -->"
    $replacement = "<!-- BEGIN:AUTO -->`n" + $table + "`n<!-- END:AUTO -->"
    if ($docText -notmatch $pattern) { throw "UPSTREAM.md 에 <!-- BEGIN:AUTO --> 마커가 없습니다." }
    $docText = [regex]::Replace($docText, $pattern, { $replacement })
    # Set-Content -Encoding UTF8 은 PS 5.1 에서 BOM 을 붙인다. .NET 으로 BOM 없이 쓴다.
    [System.IO.File]::WriteAllText($Doc, $docText, (New-Object System.Text.UTF8Encoding($false)))

    Write-Host ""
    Write-Host "완료. lerobot -> $FullSha ($CommitDate)" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Cyan
    Write-Host "  uv lock"
    Write-Host "  uv sync"
    Write-Host "  # 로봇 붙여서 teleoperate -> 짧은 녹화 -> rollout 검증"
    Write-Host "  git add -A; git commit -m `"chore: bump lerobot to $($FullSha.Substring(0,8))`""
}
finally {
    if (Test-Path $Tmp) { Remove-Item -LiteralPath $Tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
