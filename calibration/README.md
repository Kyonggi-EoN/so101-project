# calibration/

동아리 SO-101 팔의 캘리브레이션 값. **커밋해서 공유한다.**

## 왜 리포에 두나

`homing_offset` 은 "엔코더 원시값 ↔ 각도" 변환 기준이다. 녹화한 데이터셋의
관절 각도도, 학습된 정책이 출력하는 각도도 전부 이 기준으로 기록돼 있다.
새로 캘리브레이션하면 기준이 달라져서 **같은 체크포인트가 다른 자세로 움직인다.**
편의가 아니라 재현성 문제다.

## 폴더 모양을 바꾸지 말 것

lerobot 이 `HF_LEROBOT_CALIBRATION / <robots|teleoperators> / <name> / <id>.json`
으로 찾는다. 이 모양이라야 환경변수 하나로 모든 명령이 여기를 보게 된다.

```
calibration/
├─ robots/so_follower/follower.json        <id> = --robot.id
└─ teleoperators/so_leader/leader.json     <id> = --teleop.id
```

## 다시 캘리브레이션해야 하는 경우

**모터를 교체했을 때.** 서보 EEPROM 에도 같은 값이 들어 있어서, 새 모터는
기존 파일과 맞지 않는다. lerobot 이 알아서 감지하고 알려준다:

> Mismatch between calibration values in the motor and the calibration file

이때는 `lerobot-calibrate` 를 돌린 뒤 **바뀐 JSON 을 반드시 커밋**할 것.
안 하면 다음 사람이 또 캘리브레이션하게 된다.

## 이력

| 날짜 | 내용 |
|---|---|
| 2026-08-31 | 3번(elbow_flex) · 4번(wrist_flex) 모터 교체 후 재캘리브레이션 |
