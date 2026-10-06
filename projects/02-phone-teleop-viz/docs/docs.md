# 설정 메모 (WSL)

> 마무리 문서 작업 전까지 쓰는 임시 메모. 자세한 설명은 README 에 옮길 때 쓴다.

## 1. 패키지 설치

```bash
uv sync --extra placo-dep --extra phone
```

- `placo-dep`: placo (IK, 시각화) / `phone`: hebi-py, teleop
- 그냥 `uv sync` 만 하면 위 extra 가 **다시 지워진다**. 항상 같이 붙일 것

## 2. VS Code 에서 placo 자동완성 안 될 때

증상: `(function) KinematicsSolver: Any`
원인: `placo.pyi` 가 `cmeel.prefix/...` 안에 있고, 이 경로는 `.pth` 의 코드 실행으로만 추가돼서 Pylance 가 못 찾음

`.vscode/settings.json`

```json
{
  "python.analysis.extraPaths": [
    ".venv/lib/python3.12/site-packages/cmeel.prefix/lib/python3.12/site-packages"
  ]
}
```

- 반영 안 되면 "Python: Restart Language Server"
- `.vscode/` 는 `.gitignore` 에 없음 → `echo ".vscode/" >> .git/info/exclude`

## 3. 실행 (hebi 에러 우회)

증상: `RuntimeError: HEBI Core library not found`
진짜 에러: `cannot enable executable stack as shared object requires: Invalid argument`
원인: glibc 2.41+ 가 실행 가능 스택을 요구하는 `libhebi.so` 로드를 막음 (이 WSL 은 glibc 2.43). Android 를 써도 lerobot 이 import 시점에 hebi 를 부름

```bash
GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone-teleop-viz.py

# 또는 터미널에 한 번 설정해 두고 실행
export GLIBC_TUNABLES=glibc.rtld.execstack=2
```

- 스크립트 안의 `os.environ` 으로 넣으면 **효과 없음** (프로세스 시작 시점에 읽힘)
- `matplotlib not found - hebi.util.plot_logs ...` 경고는 무시해도 됨

## 4. URDF + 메시

- lerobot 의 IK 만 쓸 때는 URDF 하나로 되지만, placo 로 로드·시각화하려면 URDF 가 참조하는 메시(`assets/*.stl`)가 같이 있어야 한다
  - 예: `Mesh assets/base_motor_holder_so101_v1.stl`
- 출처: TheRobotStudio/SO-ARM100 의 `Simulation/SO101/` (URDF + `assets/` 폴더째)
- 이 프로젝트에는 `so101-description/` 에 통째로 복사해 둠. 쓰는 파일은 `so101-description/so101_new_calib.urdf`

## 5. 핸드폰 연결 (WSL 네트워크)

### 5-1. WSL 미러 모드 켜기

핸드폰이 WSL 서버에 접속하려면 WSL 이 Windows 와 같은 IP(`192.168.0.x`)를 써야 한다. 기본값(NAT)은 WSL 이 `172.x` 내부 IP 를 써서 외부 기기가 못 들어온다.

`C:\Users\<윈도우-사용자명>\.wslconfig`

```ini
[wsl2]
networkingMode=Mirrored
```

- 또는 "WSL Settings" 앱 → 네트워킹 → 네트워킹 모드 "Mirrored"
- 적용: PowerShell 에서 `wsl --shutdown` 후 WSL 다시 열기
- 확인: WSL 에서 `ip -4 addr` → `192.168.0.x` 가 보이면 됨

### 5-2. Hyper-V 방화벽에서 4443 포트 열기

증상: 서버는 `Server started at 0.0.0.0:4443` 로 떴는데, 핸드폰에서 `https://192.168.0.x:4443` 접속 시 `ERR_CONNECTION_TIMED_OUT`
원인: 미러 모드에서는 WSL 전용 Hyper-V 방화벽이 들어오는 연결을 기본 차단(`DefaultInboundAction : Block`)

**관리자 권한 PowerShell** 에서

```powershell
New-NetFirewallHyperVRule -Name "WSL-teleop-4443" -DisplayName "WSL phone teleop (4443)" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 4443
```

- 포트는 **4443 고정**: lerobot 의 `AndroidPhone.connect()` 가 `Teleop()` 을 인자 없이 부르고 `PhoneConfig` 에 포트 필드가 없음 (teleop 기본값 4443)
- `{40E0AC32-...}` 는 WSL 고정 ID (모든 PC 동일)
- 상태 확인: `Get-NetFirewallHyperVVMSetting -PolicyStore ActiveStore -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}'`
- 규칙 삭제: `Remove-NetFirewallHyperVRule -Name "WSL-teleop-4443"`
- WSL 설정의 "호스트 주소 Loopback"(`hostAddressLoopback`) 은 **같은 PC 안의** Windows ↔ WSL 연결용이라 이 문제와 무관


### 5-3. 접속

- 핸드폰은 PC 와 **같은 Wi-Fi** (모바일 데이터 X)
- 인증서 경고는 정상 (teleop 자체 서명 인증서, WebXR 이 https 필수) → "고급 → 계속 진행"

## 6. rerun 포트 충돌

증상: `--log rerun` 으로 실행하면

```
RuntimeError: Failed to create server: Address already in use (os error 98): (0.0.0.0:9090)
```

원인: 9090 포트를 다른 프로그램이 이미 쓰고 있음. 우분투 서버는 기본으로 깔린 서버 관리 웹 화면 **Cockpit**(`cockpit.socket`)이 9090 을 쓴다. 방화벽 문제가 아니므로 포트를 열어도 해결되지 않음

`phone_teleop_viz.py` 에서 `DebugLogger` 의 `web_port` 인자를 빈 포트로 바꾼다

```python
logger = DebugLogger(web_port=<빈 포트>)
# 예
logger = DebugLogger(web_port=9091)
```

- 누가 쓰는지 확인: `ss -ltnp | grep 9090` (이름이 안 나오면 `systemctl list-sockets | grep 9090`)
- 원격(VS Code Remote-SSH)이면 포트 탭에서 바꾼 포트를 포워딩. 브라우저 주소도 `http://localhost:<빈 포트>/?url=...` 로 바뀐다 (실행 시 터미널에 출력됨)
- (원격만 해당) rerun 화면은 뜨는데 **그래프가 비어 있으면** 9876 포워딩 확인. rerun 은 화면(`web_port`)과 데이터(9876)를 다른 포트로 보내고, 브라우저가 노트북의 `127.0.0.1:9876` 으로 데이터를 받으러 간다. 같은 PC 에서 돌리면 해당 없음
