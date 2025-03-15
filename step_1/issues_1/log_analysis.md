# 사고 분석 보고서

## 1. 사고 개요
화성 기지 폭발 사고의 원인을 분석한다.

## 2. 로그 분석
| Timestamp | Event | Message |
|-----------|-------|---------|
| 2023-08-27 11:40:00 | INFO | Oxygen tank explosion. |

## 3. 폭발 전후 로그
| Timestamp | Event | Message |
|-----------|-------|---------|
| 2023-08-27 11:35:00 | INFO | Oxygen tank unstable. |
| 2023-08-27 11:40:00 | INFO | Oxygen tank explosion. |
| 2023-08-27 12:00:00 | INFO | Center and mission control systems powered down. |

## 4. 사고 원인 정리
로그 분석 결과, **산소 탱크의 불안정한 상태(Oxygen tank unstable)** 이후 **산소 탱크 폭발(Oxygen tank explosion)** 이 발생한 것으로 확인됨.

