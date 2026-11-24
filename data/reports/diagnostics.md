# STINT THEORY per-race diagnostics

Built from data/raw. For checking the OpenF1 reconstruction by eye; not a results file.

## Races to look at

Nonzero unpaired or unmatched safety-car / VSC / red messages.

_none_

## Grid check: 2023 R01 Bahrain Grand Prix (source: position_first_record)

Compare with the official grid.

| GridPosition | Driver | DriverNumber |
|---|---|---|
| 1 | VER | 1 |
| 2 | PER | 11 |
| 3 | LEC | 16 |
| 4 | SAI | 55 |
| 5 | ALO | 14 |
| 6 | RUS | 63 |
| 7 | HAM | 44 |
| 8 | STR | 18 |
| 9 | OCO | 31 |
| 10 | HUL | 27 |
| 11 | NOR | 4 |
| 12 | BOT | 77 |
| 13 | ZHO | 24 |
| 14 | TSU | 22 |
| 15 | ALB | 23 |
| 16 | SAR | 2 |
| 17 | MAG | 20 |
| 18 | PIA | 81 |
| 19 | DEV | 21 |
| 20 | GAS | 10 |

## 2023 R01 Bahrain Grand Prix (session 7953)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1058, 'stints': 70, 'drivers': 20, 'pit': 0, 'position': 666, 'race_control': 75, 'weather': 161, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 11; lap counts (top 5): {57: 11, 56: 5, 55: 1, 42: 1, 40: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 14:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 15:03:38 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:10:19 | 41 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 16:11:55 | 42 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 16:12:08 | 42 | Flag | CLEAR | Track | TRACK CLEAR |
| 16:37:31 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 4219.0 | 4315.0 | 1.6 |

Laps (any driver) flagged: SC 0, VSC 31, red 0, yellow 76

## 2023 R02 Saudi Arabian Grand Prix (session 7779)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 945, 'stints': 44, 'drivers': 20, 'pit': 0, 'position': 343, 'race_control': 58, 'weather': 148, 'starting_grid': 0, 'session_result': 20}
- max lap 51; drivers reaching it: 1; lap counts (top 5): {51: 1, 50: 16, 49: 1, 28: 1, 17: 1}

**Laps beyond scheduled_laps (50)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| PER | 51 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:50 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:31:10 | 18 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:36:10 | 20 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:38:27 | 20 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:25:07 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1870.0 | 2170.0 | 5.0 |

Laps (any driver) flagged: SC 60, VSC 0, red 0, yellow 55

## 2023 R03 Australian Grand Prix (session 7787)
- scheduled_laps: 58 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1006, 'stints': 85, 'drivers': 20, 'pit': 0, 'position': 479, 'race_control': 111, 'weather': 222, 'starting_grid': 0, 'session_result': 20}
- max lap 59; drivers reaching it: 3; lap counts (top 5): {59: 3, 58: 9, 57: 4, 53: 1, 18: 1}

**Laps beyond scheduled_laps (58)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 59 |  | False |  |
| ALO | 59 |  | False |  |
| HAM | 59 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 04:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 05:03:18 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 05:04:27 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 05:07:27 | 3 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 05:09:12 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:14:24 | 7 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 05:17:02 | 8 | Flag | RED | Track | RED FLAG |
| 05:22:27 | 9 | Other |  |  | RACE WILL RESUME AT 15:33 |
| 05:32:01 | 9 | Other |  |  | RACE WILL RESUME AT 15:33 - STANDING START PROCEDURE |
| 05:32:43 | 9 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:34:05 | 9 | Other |  |  | STANDING START PROCEDURE |
| 05:48:36 | 18 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 05:50:38 | 19 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 05:50:52 | 19 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:38:32 | 54 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 06:41:07 | 55 | Flag | RED | Track | RED FLAG |
| 06:45:37 | 56 | Other |  |  | RACE WILL RESUME AT 16:56 |
| 06:51:10 | 56 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:55:05 | 56 | Other |  |  | RACE WILL RESUME AT 16:56 - STANDING START PROCEDURE |
| 06:57:13 | 56 | Other |  |  | STANDING START PROCEDURE |
| 07:00:26 | 57 | Flag | RED | Track | RED FLAG |
| 07:22:32 | 58 | Other |  |  | RACE WILL RESUME AT 17:33 |
| 07:23:16 | 58 | Flag | CLEAR | Track | TRACK CLEAR |
| 07:32:01 | 58 | Other |  |  | RACE WILL RESUME AT 17:33 - ROLLING START PROCEDURE |
| 07:34:06 | 58 | Other |  |  | SAFETY CAR WILL ENTER PITS: ROLLING START PROCEDURE |
| 07:35:58 | 58 | Flag | CHEQUERED | Track | CHEQUERED FLAG |
| 07:37:06 | 58 | Flag | RED | Track | RED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 267.0 | 447.0 | 3.0 |
| sc | 864.0 | 1022.0 | 2.6 |
| red | 1022.0 | 1963.0 | 15.7 |
| vsc | 2916.0 | 3038.0 | 2.0 |
| sc | 5912.0 | 6067.0 | 2.6 |
| red | 6067.0 | 6670.0 | 10.0 |
| red | 7226.0 | 8596.0 | 22.8 |
| sc | 9121.0 | 9246.0 | 2.1 |

Laps (any driver) flagged: SC 142, VSC 34, red 54, yellow 119

## 2023 R04 Azerbaijan Grand Prix (session 9070)
- scheduled_laps: 51 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 963, 'stints': 43, 'drivers': 20, 'pit': 0, 'position': 325, 'race_control': 54, 'weather': 160, 'starting_grid': 0, 'session_result': 20}
- max lap 51; drivers reaching it: 16; lap counts (top 5): {51: 16, 50: 2, 37: 1, 10: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 10:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 10:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 11:04:04 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 11:22:24 | 11 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 11:28:42 | 13 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 11:29:44 | 13 | Flag | CLEAR | Track | TRACK CLEAR |
| 12:36:44 | 51 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1344.0 | 1722.0 | 6.3 |

Laps (any driver) flagged: SC 69, VSC 0, red 0, yellow 172

## 2023 R05 Miami Grand Prix (session 9078)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1139, 'stints': 40, 'drivers': 20, 'pit': 0, 'position': 430, 'race_control': 40, 'weather': 155, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 1; lap counts (top 5): {58: 1, 57: 17, 56: 2}

**Laps beyond scheduled_laps (57)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 58 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 18:40:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:50:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 19:33:47 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 21:01:28 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2023 R06 Monaco Grand Prix (session 9094)
- scheduled_laps: 78 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1516, 'stints': 57, 'drivers': 20, 'pit': 0, 'position': 300, 'race_control': 244, 'weather': 176, 'starting_grid': 0, 'session_result': 20}
- max lap 79; drivers reaching it: 1; lap counts (top 5): {79: 1, 78: 7, 77: 6, 76: 4, 71: 1}

**Laps beyond scheduled_laps (78)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 79 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:04 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:51:58 | 78 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 213

## 2023 R07 Spanish Grand Prix (session 9102)
- scheduled_laps: 66 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1312, 'stints': 63, 'drivers': 20, 'pit': 43, 'position': 705, 'race_control': 49, 'weather': 154, 'starting_grid': 0, 'session_result': 20}
- max lap 66; drivers reaching it: 12; lap counts (top 5): {66: 12, 65: 8}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:16 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:31:14 | 66 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2023 R08 Canadian Grand Prix (session 9110)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1318, 'stints': 53, 'drivers': 20, 'pit': 33, 'position': 346, 'race_control': 77, 'weather': 162, 'starting_grid': 0, 'session_result': 20}
- max lap 71; drivers reaching it: 1; lap counts (top 5): {71: 1, 70: 13, 69: 4, 54: 1, 7: 1}

**Laps beyond scheduled_laps (70)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 71 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 17:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 18:03:05 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:12:28 | 8 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 18:13:02 | 8 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 18:13:14 | 8 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:18:44 | 12 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 18:25:48 | 16 | Other |  |  | PIT EXIT INCIDENT INVOLVING CARS 31 (OCO), 77 (BOT) AND 20 (MAG) NOTED - OVERTAKING UNDER SAFETY CAR |
| 18:26:11 | 16 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 18:27:16 | 16 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:33:55 | 21 | Other |  |  | FIA STEWARDS: PIT EXIT INCIDENT INVOLVING CARS 31 (OCO), 77 (BOT) AND 20 (MAG) REVIEWED NO FURTHER INVESTIGATION - POSITIONS GIVEN BACK  |
| 19:37:04 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 748.0 | 782.0 | 0.6 |
| sc | 1124.0 | 1571.0 | 7.4 |

Laps (any driver) flagged: SC 95, VSC 30, red 0, yellow 168

## 2023 R09 Austrian Grand Prix (session 9118)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1355, 'stints': 83, 'drivers': 20, 'pit': 63, 'position': 532, 'race_control': 212, 'weather': 153, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 1; lap counts (top 5): {72: 1, 71: 10, 70: 8, 13: 1}

**Laps beyond scheduled_laps (71)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 72 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:02:48 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:03:56 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 13:05:02 | 2 | SafetyCar |  |  | SAFETY CAR THROUGH THE PIT LANE |
| 13:06:44 | 3 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 13:07:46 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 13:20:53 | 14 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:23:00 | 16 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:23:12 | 16 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:28:23 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 236.0 | 404.0 | 2.8 |
| vsc | 1253.0 | 1380.0 | 2.1 |

Laps (any driver) flagged: SC 58, VSC 44, red 0, yellow 79

## 2023 R10 British Grand Prix (session 9126)
- scheduled_laps: 52 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 974, 'stints': 44, 'drivers': 20, 'pit': 24, 'position': 305, 'race_control': 46, 'weather': 151, 'starting_grid': 0, 'session_result': 20}
- max lap 53; drivers reaching it: 1; lap counts (top 5): {53: 1, 52: 16, 47: 1, 32: 1, 10: 1}

**Laps beyond scheduled_laps (52)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 53 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 13:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 14:03:10 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:52:54 | 33 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 14:54:18 | 33 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 15:05:22 | 38 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 15:06:52 | 38 | Flag | CLEAR | Track | TRACK CLEAR |
| 15:28:27 | 52 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 3174.0 | 3258.0 | 1.4 |
| sc | 3258.0 | 3922.0 | 11.1 |

Laps (any driver) flagged: SC 108, VSC 34, red 0, yellow 66

## 2023 R11 Hungarian Grand Prix (session 9133)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1255, 'stints': 56, 'drivers': 20, 'pit': 36, 'position': 464, 'race_control': 87, 'weather': 164, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 9; lap counts (top 5): {70: 9, 69: 8, 68: 1, 3: 1, 2: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:06 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:41:14 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 39

## 2023 R12 Belgian Grand Prix (session 9141)
- scheduled_laps: 44 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 817, 'stints': 57, 'drivers': 20, 'pit': 37, 'position': 620, 'race_control': 56, 'weather': 150, 'starting_grid': 0, 'session_result': 20}
- max lap 44; drivers reaching it: 18; lap counts (top 5): {44: 18, 24: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:46 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:26:16 | 44 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 55

## 2023 R13 Dutch Grand Prix (session 9149)
- scheduled_laps: 72 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1344, 'stints': 121, 'drivers': 20, 'pit': 101, 'position': 1012, 'race_control': 78, 'weather': 209, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 17; lap counts (top 5): {72: 17, 63: 1, 42: 1, 15: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:05 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:26:04 | 16 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 13:34:57 | 21 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 13:36:19 | 21 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:30:29 | 64 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 14:31:16 | 64 | Flag | RED | Track | RED FLAG |
| 15:03:31 | 65 | Other |  |  | RACE WILL RESUME AT 17:14 |
| 15:07:08 | 65 | Other |  |  | RACE WILL RESUME AT 17:14 - ROLLING START PROCEDURE |
| 15:09:49 | 65 | Other |  |  | THE SAFETY CAR WILL STAY OUT FOR 2 LAPS  |
| 15:10:39 | 65 | Flag | CLEAR | Track | TRACK CLEAR |
| 15:17:24 | 66 | Other |  |  | SAFETY CAR WILL ENTER PITS: ROLLING START PROCEDURE |
| 15:27:08 | 72 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1564.0 | 2097.0 | 8.9 |
| vsc | 5429.0 | 5476.0 | 0.8 |
| red | 5476.0 | 7628.0 | 35.9 |
| sc | 7628.0 | 8244.0 | 10.3 |

Laps (any driver) flagged: SC 160, VSC 22, red 33, yellow 109

## 2023 R14 Italian Grand Prix (session 9157)
- scheduled_laps: 51 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 968, 'stints': 45, 'drivers': 20, 'pit': 25, 'position': 472, 'race_control': 45, 'weather': 156, 'starting_grid': 0, 'session_result': 20}
- max lap 52; drivers reaching it: 16; lap counts (top 5): {52: 16, 51: 2, 40: 1, 1: 1}

**Laps beyond scheduled_laps (51)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 52 |  | False |  |
| GAS | 52 |  | False |  |
| PER | 52 |  | False |  |
| ALO | 52 |  | False |  |
| LEC | 52 |  | False |  |
| STR | 52 |  | False |  |
| SAR | 52 |  | False |  |
| ALB | 52 |  | False |  |
| ZHO | 52 |  | False |  |
| NOR | 52 |  | False |  |
| LAW | 52 |  | False |  |
| HAM | 52 |  | False |  |
| SAI | 52 |  | False |  |
| RUS | 52 |  | False |  |
| BOT | 52 |  | False |  |
| PIA | 52 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:23:23 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2023 R15 Singapore Grand Prix (session 9165)
- scheduled_laps: 62 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1091, 'stints': 44, 'drivers': 19, 'pit': 25, 'position': 405, 'race_control': 76, 'weather': 176, 'starting_grid': 0, 'session_result': 19}
- max lap 63; drivers reaching it: 3; lap counts (top 5): {63: 3, 62: 13, 52: 1, 43: 1, 1: 1}

**Laps beyond scheduled_laps (62)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| NOR | 63 |  | False |  |
| HAM | 63 |  | False |  |
| SAI | 63 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 11:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 11:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 12:03:45 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:36:41 | 20 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 12:41:01 | 22 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 12:42:50 | 22 | Flag | CLEAR | Track | TRACK CLEAR |
| 13:18:06 | 44 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:21:29 | 45 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:21:44 | 45 | Flag | CLEAR | Track | TRACK CLEAR |
| 13:29:59 | 50 | Other |  |  | PIT EXIT INCIDENT INVOLVING CARS 11 (PER) AND 23 (ALB) NOTED - VSC INFRINGEMENT |
| 13:31:48 | 51 | Other |  |  | FIA STEWARDS: PIT EXIT INCIDENT INVOLVING CARS 11 (PER) AND 23 (ALB) WILL BE INVESTIGATED AFTER THE RACE - VSC INFRINGEMENT |
| 13:50:26 | 62 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 2201.0 | 2461.0 | 4.3 |
| vsc | 4686.0 | 4889.0 | 3.4 |

Laps (any driver) flagged: SC 53, VSC 44, red 0, yellow 182

## 2023 R16 Japanese Grand Prix (session 9173)
- scheduled_laps: 53 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 886, 'stints': 63, 'drivers': 20, 'pit': 43, 'position': 523, 'race_control': 73, 'weather': 158, 'starting_grid': 0, 'session_result': 20}
- max lap 54; drivers reaching it: 1; lap counts (top 5): {54: 1, 53: 9, 52: 5, 27: 1, 23: 1}

**Laps beyond scheduled_laps (53)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 54 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 04:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:20:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 05:04:05 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 05:05:18 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 05:11:45 | 4 | Other |  |  | INCIDENT INVOLVING CAR 11 (PER) NOTED - SAFETY CAR INFRINGEMENT |
| 05:12:41 | 4 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 05:13:56 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:20:27 | 8 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 11 (PER) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 05:22:37 | 9 | Other |  |  | FIA STEWARDS: 5 SECOND TIME PENALTY FOR CAR 11 (PER) - SAFETY CAR INFRINGEMENT |
| 05:29:34 | 14 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 05:30:36 | 14 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 05:30:51 | 14 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:35:04 | 53 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 318.0 | 761.0 | 7.4 |
| vsc | 1774.0 | 1836.0 | 1.0 |

Laps (any driver) flagged: SC 79, VSC 28, red 0, yellow 104

## 2023 R17 Qatar Grand Prix (session 9221)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1009, 'stints': 73, 'drivers': 20, 'pit': 54, 'position': 1058, 'race_control': 137, 'weather': 159, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 1; lap counts (top 5): {58: 1, 57: 13, 56: 3, 41: 1, 1: 1}

**Laps beyond scheduled_laps (57)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 58 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:10:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:34 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:04:43 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:11:00 | 4 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:12:23 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:31:15 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 283.0 | 660.0 | 6.3 |

Laps (any driver) flagged: SC 71, VSC 0, red 0, yellow 90

## 2023 R18 United States Grand Prix (session 9213)
- scheduled_laps: 56 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1017, 'stints': 56, 'drivers': 20, 'pit': 36, 'position': 537, 'race_control': 81, 'weather': 168, 'starting_grid': 0, 'session_result': 20}
- max lap 56; drivers reaching it: 14; lap counts (top 5): {56: 14, 55: 3, 50: 1, 11: 1, 7: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 18:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 19:03:42 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 20:39:02 | 56 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 7

## 2023 R19 Mexico City Grand Prix (session 9181)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1286, 'stints': 58, 'drivers': 20, 'pit': 38, 'position': 564, 'race_control': 100, 'weather': 190, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 1; lap counts (top 5): {72: 1, 71: 15, 67: 1, 48: 1, 32: 1}

**Laps beyond scheduled_laps (71)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 72 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 19:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 20:03:18 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 20:09:05 | 5 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 20:10:21 | 5 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 20:10:34 | 5 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:49:24 | 33 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 20:51:53 | 34 | Flag | RED | Track | RED FLAG |
| 21:01:47 | 35 | Other |  |  | RACE WILL RESUME AT 15:13 |
| 21:07:43 | 35 | Flag | CLEAR | Track | TRACK CLEAR |
| 21:11:01 | 35 | Other |  |  | RACE WILL RESUME AT 15:13 - STANDING START PROCEDURE |
| 21:11:47 | 35 | Other |  |  | ALL CARS MAY OVERTAKE THE SAFETY CAR |
| 21:12:46 | 35 | Other |  |  | ALL CARS MAY OVERTAKE THE SAFETY CAR |
| 21:13:38 | 35 | Other |  |  | STANDING START PROCEDURE |
| 22:05:49 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 545.0 | 621.0 | 1.3 |
| sc | 2964.0 | 3113.0 | 2.5 |
| red | 3113.0 | 4063.0 | 15.8 |

Laps (any driver) flagged: SC 42, VSC 30, red 36, yellow 125

## 2023 R20 São Paulo Grand Prix (session 9205)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1112, 'stints': 87, 'drivers': 20, 'pit': 67, 'position': 444, 'race_control': 55, 'weather': 183, 'starting_grid': 0, 'session_result': 20}
- max lap 71; drivers reaching it: 9; lap counts (top 5): {71: 9, 70: 4, 69: 1, 58: 1, 40: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:10:02 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:23 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:03:50 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:04:04 | 1 | SafetyCar |  |  | SAFETY CAR THROUGH THE PIT LANE |
| 17:06:35 | 2 | Flag | RED | Track | RED FLAG |
| 17:20:25 | 3 | Other |  |  | RACE WILL RESUME AT 14:31 |
| 17:27:51 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:29:01 | 3 | Other |  |  | RACE WILL RESUME AT 14:31 - STANDING START PROCEDURE |
| 17:30:46 | 3 | Other |  |  | ALL CARS MAY OVERTAKE THE SAFETY CAR |
| 19:00:12 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 230.0 | 395.0 | 2.8 |
| red | 395.0 | 1671.0 | 21.3 |

Laps (any driver) flagged: SC 32, VSC 0, red 32, yellow 32

## 2023 R21 Las Vegas Grand Prix (session 9189)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 949, 'stints': 51, 'drivers': 20, 'pit': 31, 'position': 628, 'race_control': 75, 'weather': 108, 'starting_grid': 0, 'session_result': 20}
- max lap 51; drivers reaching it: 3; lap counts (top 5): {51: 3, 50: 14, 47: 1, 46: 1, 3: 1}

**Laps beyond scheduled_laps (50)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 51 |  | False |  |
| PER | 51 |  | False |  |
| LEC | 51 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 06:04:05 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 06:05:49 | 1 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 06:07:46 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 06:07:58 | 2 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:09:27 | 3 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 06:16:28 | 6 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 06:17:57 | 6 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:51:24 | 26 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 06:56:17 | 28 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 06:57:17 | 28 | Flag | CLEAR | Track | TRACK CLEAR |
| 07:33:16 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 349.0 | 466.0 | 2.0 |
| sc | 567.0 | 988.0 | 7.0 |
| sc | 3084.0 | 3377.0 | 4.9 |

Laps (any driver) flagged: SC 133, VSC 40, red 0, yellow 217

## 2023 R22 Abu Dhabi Grand Prix (session 9197)
- scheduled_laps: 58 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1159, 'stints': 57, 'drivers': 20, 'pit': 37, 'position': 692, 'race_control': 67, 'weather': 156, 'starting_grid': 0, 'session_result': 20}
- max lap 59; drivers reaching it: 1; lap counts (top 5): {59: 1, 58: 17, 57: 2}

**Laps beyond scheduled_laps (58)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| VER | 59 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:10:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:20:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:26 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:30:29 | 58 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2024 R01 Bahrain Grand Prix (session 9472)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1129, 'stints': 63, 'drivers': 20, 'pit': 43, 'position': 698, 'race_control': 71, 'weather': 157, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 10; lap counts (top 5): {57: 10, 56: 9, 55: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 14:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 15:03:42 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:35:26 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 42

## 2024 R02 Saudi Arabian Grand Prix (session 9480)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 902, 'stints': 39, 'drivers': 20, 'pit': 19, 'position': 229, 'race_control': 68, 'weather': 146, 'starting_grid': 0, 'session_result': 20}
- max lap 50; drivers reaching it: 12; lap counts (top 5): {50: 12, 49: 6, 6: 1, 2: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:59 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:14:05 | 7 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:20:12 | 9 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:20:51 | 9 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:24:41 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 845.0 | 1212.0 | 6.1 |

Laps (any driver) flagged: SC 54, VSC 0, red 0, yellow 60

## 2024 R03 Australian Grand Prix (session 9488)
- scheduled_laps: 58 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 998, 'stints': 55, 'drivers': 19, 'pit': 36, 'position': 442, 'race_control': 84, 'weather': 144, 'starting_grid': 0, 'session_result': 19}
- max lap 58; drivers reaching it: 9; lap counts (top 5): {58: 9, 57: 8, 16: 1, 4: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 03:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 03:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 04:03:12 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:26:24 | 17 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 04:27:29 | 18 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 04:27:43 | 18 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:05:39 | 45 | Other |  |  | INCIDENT INVOLVING CAR 10 (GAS) NOTED - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – CROSSING THE LINE AT PIT EXIT |
| 05:08:08 | 47 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 10 (GAS) UNDER INVESTIGATION - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – CROSSING THE LINE AT PIT EXIT |
| 05:09:10 | 48 | Other |  |  | FIA STEWARDS: 5 SECOND TIME PENALTY FOR CAR 10 (GAS) - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – CROSSING THE LINE AT PIT EXIT |
| 05:22:02 | 58 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 05:23:37 | 58 | Flag | CHEQUERED | Track | CHEQUERED FLAG |
| 05:30:43 | 58 | Flag | CLEAR | Track | TRACK CLEAR |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 1584.0 | 1649.0 | 1.1 |
| vsc | 4922.0 | 5017.0 | 1.6 |

Laps (any driver) flagged: SC 0, VSC 50, red 0, yellow 56

## 2024 R04 Japanese Grand Prix (session 9496)
- scheduled_laps: 53 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 908, 'stints': 74, 'drivers': 20, 'pit': 54, 'position': 443, 'race_control': 70, 'weather': 181, 'starting_grid': 0, 'session_result': 20}
- max lap 53; drivers reaching it: 9; lap counts (top 5): {53: 9, 52: 8, 13: 1, 1: 2}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 04:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 05:03:42 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 05:04:24 | 1 | Flag | RED | Track | RED FLAG |
| 05:20:23 | 2 | Other |  |  | RACE WILL RESUME AT 14:32 |
| 05:22:31 | 2 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:30:00 | 2 | Other |  |  | RACE WILL RESUME AT 14:32 - STANDING START PROCEDURE |
| 05:31:45 | 2 | Other |  |  | ALL CARS MAY OVERTAKE THE SAFETY CAR |
| 05:32:48 | 2 | Other |  |  | STANDING START PROCEDURE |
| 06:58:05 | 53 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| red | 264.0 | 1351.0 | 18.1 |

Laps (any driver) flagged: SC 0, VSC 0, red 18, yellow 22

## 2024 R05 Chinese Grand Prix (session 9673)
- scheduled_laps: 56 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1033, 'stints': 60, 'drivers': 20, 'pit': 40, 'position': 617, 'race_control': 58, 'weather': 165, 'starting_grid': 0, 'session_result': 20}
- max lap 56; drivers reaching it: 17; lap counts (top 5): {56: 17, 34: 1, 27: 1, 20: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 06:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 06:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 07:03:37 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 07:39:16 | 22 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 07:43:21 | 23 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 07:47:18 | 25 | Other |  |  | INCIDENT INVOLVING CARS 2 (SAR) AND 27 (HUL) NOTED - SAFETY CAR INFRINGEMENT |
| 07:49:36 | 26 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 07:51:05 | 26 | Flag | CLEAR | Track | TRACK CLEAR |
| 07:53:02 | 27 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 08:00:59 | 31 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 08:02:48 | 31 | Flag | CLEAR | Track | TRACK CLEAR |
| 08:03:58 | 32 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CARS 2 (SAR) AND 27 (HUL) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 08:05:50 | 33 | Other |  |  | FIA STEWARDS: 10 SECOND TIME PENALTY FOR CAR 2 (SAR) - SAFETY CAR INFRINGEMENT |
| 08:19:36 | 41 | Other |  |  | INCIDENT INVOLVING CARS 27 (HUL) AND 3 (RIC) NOTED - SAFETY CAR INFRINGEMENT |
| 08:19:42 | 42 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CARS 27 (HUL) AND 3 (RIC) WILL BE INVESTIGATED AFTER THE RACE - SAFETY CAR INFRINGEMENT |
| 08:44:29 | 56 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 2356.0 | 2601.0 | 4.1 |
| sc | 2601.0 | 2976.0 | 6.2 |
| sc | 3182.0 | 3659.0 | 8.0 |

Laps (any driver) flagged: SC 163, VSC 56, red 0, yellow 146

## 2024 R06 Miami Grand Prix (session 9507)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1112, 'stints': 48, 'drivers': 20, 'pit': 28, 'position': 403, 'race_control': 77, 'weather': 150, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 1; lap counts (top 5): {58: 1, 57: 18, 28: 1}

**Laps beyond scheduled_laps (57)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| NOR | 58 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 19:20:00 | 1.0 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:30:00 | 1.0 | Other |  |  | PIT EXIT CLOSED |
| 20:03:24 | 1.0 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 20:37:57 | 23.0 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 20:38:38 | 23.0 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 20:38:49 | 23.0 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:47:06 | 28.0 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 20:54:50 | 32.0 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 20:56:01 | 32.0 | Flag | CLEAR | Track | TRACK CLEAR |
| 21:15:30 | 45.0 | Other |  |  | INCIDENT INVOLVING CAR 20 (MAG) NOTED - ENTERING PIT LANE UNDER SAFETY CAR CONDITIONS |
| 21:15:36 | 45.0 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 20 (MAG) WILL BE INVESTIGATED AFTER THE RACE - ENTERING PIT LANE UNDER SAFETY CAR CONDITIONS |
| 21:34:15 | 57.0 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 2277.0 | 2318.0 | 0.7 |
| sc | 2826.0 | 3290.0 | 7.7 |

Laps (any driver) flagged: SC 95, VSC 33, red 0, yellow 74

## 2024 R07 Emilia Romagna Grand Prix (session 9515)
- scheduled_laps: 63 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1239, 'stints': 47, 'drivers': 20, 'pit': 27, 'position': 308, 'race_control': 100, 'weather': 143, 'starting_grid': 0, 'session_result': 20}
- max lap 63; drivers reaching it: 9; lap counts (top 5): {63: 9, 62: 10, 52: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:17 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:28:42 | 63 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2024 R08 Monaco Grand Prix (session 9523)
- scheduled_laps: 78 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1237, 'stints': 43, 'drivers': 20, 'pit': 23, 'position': 127, 'race_control': 122, 'weather': 200, 'starting_grid': 0, 'session_result': 20}
- max lap 78; drivers reaching it: 7; lap counts (top 5): {78: 7, 77: 3, 76: 6, 1: 4}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:11 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:04:08 | 1 | Flag | RED | Track | RED FLAG |
| 13:29:32 | 1 | Other |  |  | RACE WILL RESUME AT 15:44 |
| 13:35:44 | 1 | Flag | CLEAR | Track | TRACK CLEAR |
| 13:42:01 | 1 | Other |  |  | RACE WILL RESUME AT 15:44 - STANDING START PROCEDURE |
| 13:43:45 | 1 | Other |  |  | ALL CARS MAY OVERTAKE THE SAFETY CAR |
| 13:44:53 | 2 | Other |  |  | STANDING START |
| 15:26:26 | 78 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| red | 248.0 | 2144.0 | 31.6 |

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 18

## 2024 R09 Canadian Grand Prix (session 9531)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1272, 'stints': 62, 'drivers': 20, 'pit': 42, 'position': 406, 'race_control': 130, 'weather': 113, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 14; lap counts (top 5): {70: 14, 69: 1, 53: 2, 52: 1, 41: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 18:03:12 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:40:26 | 25 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 18:47:34 | 29 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 18:49:05 | 29 | Flag | CLEAR | Track | TRACK CLEAR |
| 19:23:59 | 54 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 19:29:42 | 57 | Other |  |  | LAPPED CAR MAY NOW OVERTAKE THE SAFETY CAR: 24 |
| 19:31:31 | 58 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 19:33:06 | 58 | Flag | CLEAR | Track | TRACK CLEAR |
| 19:49:00 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 2426.0 | 2854.0 | 7.1 |
| sc | 5039.0 | 5491.0 | 7.5 |

Laps (any driver) flagged: SC 159, VSC 0, red 0, yellow 263

## 2024 R10 Spanish Grand Prix (session 9539)
- scheduled_laps: 66 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1310, 'stints': 62, 'drivers': 20, 'pit': 42, 'position': 744, 'race_control': 107, 'weather': 154, 'starting_grid': 0, 'session_result': 20}
- max lap 66; drivers reaching it: 11; lap counts (top 5): {66: 11, 65: 8, 64: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:14 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:31:35 | 66 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2024 R11 Austrian Grand Prix (session 9550)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1407, 'stints': 65, 'drivers': 20, 'pit': 45, 'position': 591, 'race_control': 125, 'weather': 143, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 1; lap counts (top 5): {72: 1, 71: 11, 70: 6, 69: 1, 65: 1}

**Laps beyond scheduled_laps (71)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| RUS | 72 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:02 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:20:23 | 66 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 14:21:09 | 66 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 14:21:21 | 66 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:27:25 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 4823.0 | 4869.0 | 0.8 |

Laps (any driver) flagged: SC 0, VSC 23, red 0, yellow 21

## 2024 R12 British Grand Prix (session 9558)
- scheduled_laps: 52 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 962, 'stints': 65, 'drivers': 20, 'pit': 45, 'position': 252, 'race_control': 110, 'weather': 147, 'starting_grid': 0, 'session_result': 20}
- max lap 52; drivers reaching it: 12; lap counts (top 5): {52: 12, 51: 3, 50: 3, 34: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 13:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 14:03:13 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 15:25:39 | 52 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2024 R13 Hungarian Grand Prix (session 9566)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1356, 'stints': 60, 'drivers': 20, 'pit': 40, 'position': 552, 'race_control': 75, 'weather': 155, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 11; lap counts (top 5): {70: 11, 69: 8, 34: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:02:59 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:41:00 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 21

## 2024 R14 Belgian Grand Prix (session 9574)
- scheduled_laps: 44 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 842, 'stints': 58, 'drivers': 20, 'pit': 34, 'position': 539, 'race_control': 23, 'weather': 137, 'starting_grid': 0, 'session_result': 20}
- max lap 44; drivers reaching it: 19; lap counts (top 5): {44: 19, 6: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:53 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:23:48 | 44 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 19

## 2024 R15 Dutch Grand Prix (session 9582)
- scheduled_laps: 72 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1426, 'stints': 46, 'drivers': 20, 'pit': 26, 'position': 540, 'race_control': 84, 'weather': 153, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 8; lap counts (top 5): {72: 8, 71: 10, 70: 2}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:12 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:33:58 | 72 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2024 R16 Italian Grand Prix (session 9590)
- scheduled_laps: 53 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1009, 'stints': 50, 'drivers': 20, 'pit': 30, 'position': 482, 'race_control': 61, 'weather': 133, 'starting_grid': 0, 'session_result': 20}
- max lap 53; drivers reaching it: 13; lap counts (top 5): {53: 13, 52: 6, 8: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:34 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:18:15 | 53 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2024 R17 Azerbaijan Grand Prix (session 9598)
- scheduled_laps: 51 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 975, 'stints': 42, 'drivers': 20, 'pit': 22, 'position': 359, 'race_control': 115, 'weather': 152, 'starting_grid': 0, 'session_result': 20}
- max lap 51; drivers reaching it: 14; lap counts (top 5): {51: 14, 50: 4, 46: 1, 15: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 10:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 10:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 11:04:11 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:34:38 | 51 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 12:37:07 | 51 | Flag | CHEQUERED | Track | CHEQUERED FLAG |
| 12:46:47 | 51 | Other |  |  | INCIDENT INVOLVING CAR 27 (HUL) NOTED - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:46:58 | 51 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 27 (HUL) WILL BE INVESTIGATED AFTER THE RACE - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:47:11 | 51 | Flag | CLEAR | Track | TRACK CLEAR |
| 12:47:38 | 51 | Other |  |  | INCIDENT INVOLVING CAR 1 (VER) NOTED - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:47:49 | 51 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 1 (VER) WILL BE INVESTIGATED AFTER THE RACE - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:57:51 | 51 | Other |  |  | INCIDENT INVOLVING CAR 31 (OCO) NOTED - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:57:58 | 51 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 31 (OCO) WILL BE INVESTIGATED AFTER THE RACE - VIRTUAL SAFETY CAR INFRINGEMENT |
| 12:59:57 | 51 | Other |  |  | INCIDENT INVOLVING CAR 10 (GAS) NOTED - VIRTUAL SAFETY CAR INFRINGEMENT |
| 13:00:03 | 51 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 10 (GAS) WILL BE INVESTIGATED AFTER THE RACE - VIRTUAL SAFETY CAR INFRINGEMENT |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 5678.0 | 5827.0 | 2.5 |

Laps (any driver) flagged: SC 0, VSC 31, red 0, yellow 61

## 2024 R18 Singapore Grand Prix (session 9606)
- scheduled_laps: 62 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1179, 'stints': 43, 'drivers': 20, 'pit': 23, 'position': 416, 'race_control': 63, 'weather': 160, 'starting_grid': 0, 'session_result': 20}
- max lap 62; drivers reaching it: 7; lap counts (top 5): {62: 7, 61: 11, 58: 1, 16: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 11:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 11:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 12:03:57 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:44:49 | 62 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2024 R19 United States Grand Prix (session 9617)
- scheduled_laps: 56 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1059, 'stints': 43, 'drivers': 20, 'pit': 23, 'position': 403, 'race_control': 120, 'weather': 155, 'starting_grid': 0, 'session_result': 20}
- max lap 56; drivers reaching it: 12; lap counts (top 5): {56: 12, 55: 7, 2: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 18:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 19:03:49 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:08:06 | 3 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 19:13:07 | 5 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 19:14:18 | 5 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:38:58 | 56 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 486.0 | 787.0 | 5.0 |

Laps (any driver) flagged: SC 57, VSC 0, red 0, yellow 129

## 2024 R20 Mexico City Grand Prix (session 9625)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1216, 'stints': 41, 'drivers': 20, 'pit': 21, 'position': 422, 'race_control': 120, 'weather': 159, 'starting_grid': 0, 'session_result': 20}
- max lap 71; drivers reaching it: 8; lap counts (top 5): {71: 8, 70: 9, 16: 1, 1: 2}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 19:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 20:03:35 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 20:04:31 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 20:14:47 | 6 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 20:16:02 | 6 | Flag | CLEAR | Track | TRACK CLEAR |
| 21:44:30 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 271.0 | 887.0 | 10.3 |

Laps (any driver) flagged: SC 106, VSC 0, red 0, yellow 53

## 2024 R21 São Paulo Grand Prix (session 9636)
- scheduled_laps: 69 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1137, 'stints': 54, 'drivers': 20, 'pit': 35, 'position': 360, 'race_control': 111, 'weather': 201, 'starting_grid': 0, 'session_result': 20}
- max lap 69; drivers reaching it: 15; lap counts (top 5): {69: 15, 39: 1, 31: 2, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 14:50:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 15:00:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 15:49:58 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:28:21 | 28 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 16:29:50 | 28 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 16:30:04 | 29 | Flag | CLEAR | Track | TRACK CLEAR |
| 16:32:53 | 30 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 16:37:22 | 32 | Flag | RED | Track | RED FLAG |
| 16:51:37 | 33 | Other |  |  | RACE WILL RESUME AT 14:02 |
| 17:00:01 | 33 | Other |  |  | RACE WILL RESUME AT 14:06 - ROLLING START PROCEDURE |
| 17:00:20 | 33 | Other |  |  | RACE WILL RESUME AT 14:02 - ROLLING START PROCEDURE |
| 17:01:15 | 33 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:02:36 | 33 | Other |  |  | ROLLING START |
| 17:13:14 | 39 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:18:04 | 42 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:19:29 | 42 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:56:52 | 69 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 3501.0 | 3590.0 | 1.5 |
| sc | 3773.0 | 4042.0 | 4.5 |
| red | 4042.0 | 5401.0 | 22.6 |
| sc | 5401.0 | 5556.0 | 2.6 |
| sc | 6194.0 | 6484.0 | 4.8 |

Laps (any driver) flagged: SC 130, VSC 33, red 33, yellow 289

## 2024 R22 Las Vegas Grand Prix (session 9644)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 940, 'stints': 59, 'drivers': 20, 'pit': 39, 'position': 691, 'race_control': 37, 'weather': 143, 'starting_grid': 0, 'session_result': 20}
- max lap 50; drivers reaching it: 16; lap counts (top 5): {50: 16, 49: 2, 26: 1, 16: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 05:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 05:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 06:03:40 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 07:25:46 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2024 R23 Qatar Grand Prix (session 9655)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 944, 'stints': 82, 'drivers': 20, 'pit': 60, 'position': 510, 'race_control': 112, 'weather': 151, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 14; lap counts (top 5): {57: 14, 56: 1, 40: 1, 39: 1, 9: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 15:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 15:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 16:03:33 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:04:33 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 16:10:56 | 4 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 16:12:10 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 16:56:32 | 35 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 16:59:01 | 36 | SafetyCar |  |  | SAFETY CAR THROUGH THE PIT LANE |
| 17:03:25 | 38 | Other |  |  | LAPPED CARS MAY NOW OVERTAKE THE SAFETY CAR: 44, 77 |
| 17:03:37 | 38 | Other |  |  | SAFETY CAR WILL USE START/FINISH STRAIGHT |
| 17:05:22 | 39 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:07:08 | 39 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:08:24 | 40 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 17:08:44 | 40 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:12:10 | 42 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:13:28 | 42 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:32:10 | 56 | Other |  |  | INCIDENT INVOLVING CAR 63 (RUS) NOTED - SAFETY CAR INFRINGEMENT |
| 17:34:38 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |
| 17:36:07 | 57 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 63 (RUS) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 17:37:04 | 57 | Other |  |  | FIA STEWARDS: 5 SECOND TIME PENALTY FOR CAR 63 (RUS) - SAFETY CAR INFRINGEMENT |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 273.0 | 656.0 | 6.4 |
| sc | 3392.0 | 3922.0 | 8.8 |
| vsc | 4104.0 | 4124.0 | 0.3 |
| sc | 4124.0 | 4330.0 | 3.4 |

Laps (any driver) flagged: SC 201, VSC 15, red 0, yellow 156

## 2024 R24 Abu Dhabi Grand Prix (session 9662)
- scheduled_laps: 58 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1037, 'stints': 48, 'drivers': 20, 'pit': 28, 'position': 508, 'race_control': 131, 'weather': 148, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 10; lap counts (top 5): {58: 10, 57: 6, 56: 1, 31: 1, 27: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:35 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:05:54 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:07:40 | 3 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:07:51 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:30:07 | 58 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 354.0 | 460.0 | 1.8 |

Laps (any driver) flagged: SC 0, VSC 38, red 0, yellow 99

## 2025 R01 Australian Grand Prix (session 9693)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 928, 'stints': 106, 'drivers': 20, 'pit': 82, 'position': 335, 'race_control': 115, 'weather': 178, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 1; lap counts (top 5): {58: 1, 57: 13, 47: 1, 46: 1, 33: 1}

**Laps beyond scheduled_laps (57)**

| driver | lap | lap_time_s | pit_in | status |
|---|---|---|---|---|
| NOR | 58 |  | False |  |

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 03:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 03:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 04:18:23 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:19:31 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 04:21:22 | 2 | SafetyCar |  |  | SAFETY CAR THROUGH THE PIT LANE |
| 04:30:00 | 5 | Other |  |  | SAFETY CAR WILL USE START/FINISH STRAIGHT |
| 04:33:54 | 7 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 04:35:12 | 7 | Flag | CLEAR | Track | TRACK CLEAR |
| 04:36:21 | 8 | Other |  |  | INCIDENT INVOLVING CAR 14 (ALO) NOTED - SAFETY CAR INFRINGEMENT |
| 04:37:35 | 9 | Other |  |  | INCIDENT INVOLVING CAR 22 (TSU) NOTED - SAFETY CAR INFRINGEMENT |
| 04:37:41 | 9 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 14 (ALO) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 04:38:41 | 10 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 22 (TSU) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 04:51:45 | 18 | Other |  |  | INCIDENT INVOLVING CAR 23 (ALB) NOTED - SAFETY CAR INFRINGEMENT |
| 04:51:51 | 18 | Other |  |  | INCIDENT INVOLVING CAR 44 (HAM) NOTED - SAFETY CAR INFRINGEMENT |
| 04:52:52 | 19 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 23 (ALB) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 04:53:00 | 19 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 44 (HAM) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 04:54:00 | 20 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 14 (ALO) NO FURTHER ACTION - SAFETY CAR INFRINGEMENT |
| 04:54:12 | 20 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 22 (TSU) NO FURTHER ACTION - SAFETY CAR INFRINGEMENT |
| 04:54:21 | 20 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 23 (ALB) NO FURTHER ACTION - SAFETY CAR INFRINGEMENT |
| 04:54:31 | 20 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 44 (HAM) NO FURTHER ACTION - SAFETY CAR INFRINGEMENT |
| 05:15:09 | 34 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 05:28:35 | 40 | Other |  |  | LAPPED CARS MAY NOW OVERTAKE THE SAFETY CAR: 5, 31, 87, 30 |
| 05:30:50 | 41 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 05:32:25 | 41 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:41:06 | 47 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 05:47:04 | 50 | Other |  |  | LAPPED CAR MAY NOW OVERTAKE THE SAFETY CAR: 87 |
| 05:49:42 | 51 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 05:51:17 | 51 | Flag | CLEAR | Track | TRACK CLEAR |
| 06:00:29 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1171.0 | 2034.0 | 14.4 |
| sc | 4509.0 | 5450.0 | 15.7 |
| sc | 6066.0 | 6582.0 | 8.6 |

Laps (any driver) flagged: SC 328, VSC 0, red 0, yellow 213

## 2025 R02 Chinese Grand Prix (session 9998)
- scheduled_laps: 56 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1066, 'stints': 45, 'drivers': 20, 'pit': 25, 'position': 461, 'race_control': 58, 'weather': 154, 'starting_grid': 0, 'session_result': 20}
- max lap 56; drivers reaching it: 16; lap counts (top 5): {56: 16, 55: 3, 5: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 06:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 06:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 07:03:39 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 08:34:33 | 56 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 72

## 2025 R03 Japanese Grand Prix (session 10006)
- scheduled_laps: 53 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1059, 'stints': 41, 'drivers': 20, 'pit': 21, 'position': 281, 'race_control': 25, 'weather': 140, 'starting_grid': 0, 'session_result': 20}
- max lap 53; drivers reaching it: 19; lap counts (top 5): {53: 19, 52: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 04:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 05:03:47 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 05:42:02 | 25 | Other |  |  | PIT EXIT INCIDENT INVOLVING CARS 1 (VER) AND 4 (NOR) NOTED |
| 05:43:05 | 26 | Other |  |  | FIA STEWARDS: PIT EXIT INCIDENT INVOLVING CARS 1 (VER) AND 4 (NOR) REVIEWED NO FURTHER INVESTIGATION |
| 06:25:53 | 53 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

## 2025 R04 Bahrain Grand Prix (session 10014)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1129, 'stints': 62, 'drivers': 20, 'pit': 42, 'position': 1179, 'race_control': 93, 'weather': 158, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 19; lap counts (top 5): {57: 19, 46: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 14:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 15:03:49 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 15:56:09 | 32 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 16:02:20 | 35 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 16:03:55 | 35 | Flag | CLEAR | Track | TRACK CLEAR |
| 16:12:46 | 41 | Other |  |  | TURN 4 INCIDENT INVOLVING CARS 30 (LAW) AND 18 (STR) NOTED - SAFETY CAR INFRINGEMENT |
| 16:14:09 | 42 | Other |  |  | FIA STEWARDS: TURN 4 INCIDENT INVOLVING CARS 30 (LAW) AND 18 (STR) REVIEWED NO FURTHER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 16:39:29 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 3369.0 | 3740.0 | 6.2 |

Laps (any driver) flagged: SC 77, VSC 0, red 0, yellow 0

## 2025 R05 Saudi Arabian Grand Prix (session 10022)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 899, 'stints': 39, 'drivers': 20, 'pit': 19, 'position': 322, 'race_control': 67, 'weather': 142, 'starting_grid': 0, 'session_result': 20}
- max lap 50; drivers reaching it: 14; lap counts (top 5): {50: 14, 49: 4, 2: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:55 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:05:02 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:09:28 | 3 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:11:06 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:08:14 | 40 | Other |  |  | INCIDENT INVOLVING CAR 4 (NOR) NOTED - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – CROSSING THE LINE AT PIT EXIT |
| 18:14:11 | 43 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 4 (NOR) REVIEWED NO FURTHER INVESTIGATION - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – CROSSING THE LINE AT PIT EXIT |
| 18:25:02 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 302.0 | 568.0 | 4.4 |

Laps (any driver) flagged: SC 55, VSC 0, red 0, yellow 55

## 2025 R06 Miami Grand Prix (session 10033)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 559, 'stints': 38, 'drivers': 20, 'pit': 18, 'position': 291, 'race_control': 78, 'weather': 149, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 13; lap counts (top 5): {57: 13, 56: 3, 37: 1, 31: 1, 28: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 19:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 20:03:42 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 20:06:03 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 20:08:55 | 3 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 20:09:08 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:48:05 | 29 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 20:50:12 | 30 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 20:50:25 | 30 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:55:09 | 33 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 20:56:31 | 34 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 20:56:44 | 34 | Flag | CLEAR | Track | TRACK CLEAR |
| 21:32:33 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 363.0 | 535.0 | 2.9 |
| vsc | 2885.0 | 3012.0 | 2.1 |
| vsc | 3309.0 | 3391.0 | 1.4 |

Laps (any driver) flagged: SC 0, VSC 62, red 0, yellow 0

## 2025 R07 Emilia Romagna Grand Prix (session 9987)
- scheduled_laps: 63 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1207, 'stints': 57, 'drivers': 20, 'pit': 37, 'position': 498, 'race_control': 46, 'weather': 150, 'starting_grid': 0, 'session_result': 20}
- max lap 63; drivers reaching it: 18; lap counts (top 5): {63: 18, 45: 1, 28: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:33 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:42:34 | 29 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:46:03 | 31 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:46:14 | 31 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:06:27 | 46 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:18:03 | 52 | Other |  |  | LAPPED CAR MAY NOW OVERTAKE THE SAFETY CAR: 87 |
| 14:20:09 | 53 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:21:42 | 53 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:23:24 | 55 | Other |  |  | INCIDENT INVOLVING CARS 4 (NOR) AND 23 (ALB) NOTED - SAFETY CAR INFRINGEMENT |
| 14:24:31 | 55 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CARS 4 (NOR) AND 23 (ALB) REVIEWED NO FURTHER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 14:35:06 | 63 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 2554.0 | 2763.0 | 3.5 |
| sc | 3987.0 | 4809.0 | 13.7 |

Laps (any driver) flagged: SC 149, VSC 45, red 0, yellow 157

## 2025 R08 Monaco Grand Prix (session 9979)
- scheduled_laps: 78 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1425, 'stints': 59, 'drivers': 20, 'pit': 40, 'position': 339, 'race_control': 198, 'weather': 160, 'starting_grid': 0, 'session_result': 20}
- max lap 78; drivers reaching it: 5; lap counts (top 5): {78: 5, 77: 3, 76: 9, 75: 1, 37: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:09 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:04:43 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:09:15 | 4 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:09:28 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:43:43 | 78 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 283.0 | 555.0 | 4.5 |

Laps (any driver) flagged: SC 0, VSC 68, red 0, yellow 172

## 2025 R09 Spanish Grand Prix (session 9971)
- scheduled_laps: 66 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1204, 'stints': 73, 'drivers': 19, 'pit': 54, 'position': 590, 'race_control': 102, 'weather': 155, 'starting_grid': 0, 'session_result': 19}
- max lap 66; drivers reaching it: 17; lap counts (top 5): {66: 17, 54: 1, 28: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:18 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:17:01 | 55 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:23:46 | 58 | Other |  |  | LAPPED CARS MAY NOW OVERTAKE THE SAFETY CAR: 30, 31, 5, 14, 87, 22, 55, 43 |
| 14:27:16 | 60 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:28:21 | 60 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:36:15 | 66 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 4621.0 | 5236.0 | 10.2 |

Laps (any driver) flagged: SC 113, VSC 0, red 0, yellow 55

## 2025 R10 Canadian Grand Prix (session 9963)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1349, 'stints': 102, 'drivers': 20, 'pit': 82, 'position': 550, 'race_control': 98, 'weather': 167, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 8; lap counts (top 5): {70: 8, 69: 9, 67: 1, 54: 1, 47: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 17:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 18:03:05 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:27:32 | 67 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 19:27:49 | 67 | Other |  |  | ALL CARS TO FOLLOW THE SAFETY CAR THROUGH THE PIT LANE |
| 19:34:56 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |
| 19:39:45 | 70 | Flag | CLEAR | Track | TRACK CLEAR |
| 19:48:27 | 70 | Other |  |  | INCIDENT INVOLVING CARS 12 (ANT), 81 (PIA), 31 (OCO), 16 (LEC), 55 (SAI), 10 (GAS) AND 18 (STR) NOTED - SAFETY CAR INFRINGEMENT |
| 19:58:16 | 70 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CARS 12 (ANT), 81 (PIA), 31 (OCO), 16 (LEC), 55 (SAI), 10 (GAS) AND 18 (STR) WILL BE INVESTIGATED AFTER THE RACE - SAFETY CAR INFRINGEMENT |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 5252.0 | 5696.0 | 7.4 |

Laps (any driver) flagged: SC 71, VSC 0, red 0, yellow 89

## 2025 R11 Austrian Grand Prix (session 9955)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1128, 'stints': 52, 'drivers': 20, 'pit': 32, 'position': 519, 'race_control': 119, 'weather': 161, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 6; lap counts (top 5): {70: 6, 69: 9, 68: 1, 16: 1, 1: 3}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:18:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:18:56 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 13:22:13 | 3 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 13:23:02 | 3 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:41:47 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1136.0 | 1333.0 | 3.3 |

Laps (any driver) flagged: SC 51, VSC 0, red 0, yellow 67

## 2025 R12 British Grand Prix (session 9947)
- scheduled_laps: 52 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 827, 'stints': 55, 'drivers': 20, 'pit': 35, 'position': 538, 'race_control': 158, 'weather': 155, 'starting_grid': 0, 'session_result': 20}
- max lap 52; drivers reaching it: 14; lap counts (top 5): {52: 14, 51: 1, 24: 1, 18: 1, 4: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 13:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:55:00 | 1 | Other |  |  | FORMATION LAP WILL BE STARTED BEHIND THE SAFETY CAR |
| 14:00:55 | 1 | Other |  |  | STANDING START |
| 14:03:50 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:05:48 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 14:10:18 | 4 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 14:10:31 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:13:39 | 5 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 14:17:04 | 7 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 14:17:17 | 7 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:29:14 | 14 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:38:36 | 17 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:39:12 | 17 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:41:15 | 18 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:49:02 | 21 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:49:28 | 21 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:49:47 | 22 | Other |  |  | INCIDENT INVOLVING CAR 81 (PIA) NOTED - SAFETY CAR INFRINGEMENT |
| 14:51:57 | 23 | Other |  |  | FIA STEWARDS: INCIDENT INVOLVING CAR 81 (PIA) UNDER INVESTIGATION - SAFETY CAR INFRINGEMENT |
| 14:55:02 | 25 | Other |  |  | FIA STEWARDS: 10 SECOND TIME PENALTY FOR CAR 81 (PIA) - SAFETY CAR INFRINGEMENT |
| 15:33:41 | 48 | Other |  |  | FIA STEWARDS: PENALTY SERVED - 10 SECOND TIME PENALTY FOR CAR 81 (PIA) - SAFETY CAR INFRINGEMENT |
| 15:41:05 | 52 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 348.0 | 618.0 | 4.5 |
| vsc | 819.0 | 1024.0 | 3.4 |
| sc | 1754.0 | 2316.0 | 9.4 |
| sc | 2475.0 | 2942.0 | 7.8 |

Laps (any driver) flagged: SC 146, VSC 100, red 0, yellow 253

## 2025 R13 Belgian Grand Prix (session 9939)
- scheduled_laps: 44 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 879, 'stints': 60, 'drivers': 20, 'pit': 26, 'position': 275, 'race_control': 117, 'weather': 223, 'starting_grid': 0, 'session_result': 20}
- max lap 44; drivers reaching it: 19; lap counts (top 5): {44: 19, 43: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 12:55:01 | 1 | Other |  |  | FORMATION LAP WILL BE STARTED BEHIND THE SAFETY CAR |
| 13:01:44 | 1 | Other |  |  | STARTING PROCEDURE SUSPENDED |
| 13:01:58 | 1 | Flag | RED | Track | RED FLAG |
| 13:54:50 | 1 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:04:44 | 1 | Other |  |  | RACE WILL RESUME AT 16:20 |
| 14:15:01 | 1 | Other |  |  | RACE WILL START BEHIND THE SAFETY CAR |
| 14:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:29:35 | 4 | Other |  |  | ROLLING START |
| 15:45:22 | 44 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| red | 118.0 | 3290.0 | 52.9 |
| sc | 4501.0 | 5375.0 | 14.6 |

Laps (any driver) flagged: SC 80, VSC 0, red 0, yellow 0

## 2025 R14 Hungarian Grand Prix (session 9928)
- scheduled_laps: 70 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1369, 'stints': 49, 'drivers': 20, 'pit': 29, 'position': 482, 'race_control': 95, 'weather': 136, 'starting_grid': 0, 'session_result': 20}
- max lap 70; drivers reaching it: 9; lap counts (top 5): {70: 9, 69: 10, 49: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:06 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:38:27 | 70 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0

## 2025 R15 Dutch Grand Prix (session 9920)
- scheduled_laps: 72 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1365, 'stints': 60, 'drivers': 20, 'pit': 40, 'position': 483, 'race_control': 110, 'weather': 159, 'starting_grid': 0, 'session_result': 20}
- max lap 72; drivers reaching it: 17; lap counts (top 5): {72: 17, 65: 1, 53: 1, 23: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:21 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:32:02 | 23 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 13:37:09 | 26 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 13:38:27 | 26 | Flag | CLEAR | Track | TRACK CLEAR |
| 13:44:35 | 31 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 13:45:45 | 32 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 13:45:57 | 32 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:12:19 | 53 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:18:18 | 56 | Other |  |  | LAPPED CARS MAY NOW OVERTAKE THE SAFETY CAR: 30 AND 55 |
| 14:19:34 | 57 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:20:51 | 57 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:30:28 | 65 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 14:36:08 | 68 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 14:36:48 | 68 | Flag | CLEAR | Track | TRACK CLEAR |
| 14:41:50 | 72 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 1922.0 | 2229.0 | 5.1 |
| vsc | 2675.0 | 2745.0 | 1.2 |
| sc | 4339.0 | 4774.0 | 7.2 |
| sc | 5428.0 | 5768.0 | 5.7 |

Laps (any driver) flagged: SC 236, VSC 38, red 0, yellow 228

## 2025 R16 Italian Grand Prix (session 9912)
- scheduled_laps: 53 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 976, 'stints': 39, 'drivers': 20, 'pit': 19, 'position': 421, 'race_control': 73, 'weather': 144, 'starting_grid': 0, 'session_result': 20}
- max lap 53; drivers reaching it: 14; lap counts (top 5): {53: 14, 52: 4, 25: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:27:55 | 1 | Other |  |  | PIT EXIT INCIDENT INVOLVING CAR 14 (ALO) NOTED - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – PRACTICE START INFRINGEMENT |
| 12:28:15 | 1 | Other |  |  | PIT EXIT INCIDENT INVOLVING CAR 18 (STR) NOTED - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – PRACTICE START INFRINGEMENT |
| 12:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 12:31:59 | 1 | Other |  |  | FIA STEWARDS: PIT EXIT INCIDENT INVOLVING CAR 14 (ALO) WILL BE INVESTIGATED AFTER THE RACE - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – PRACTICE START INFRINGEMENT |
| 12:32:06 | 1 | Other |  |  | FIA STEWARDS: PIT EXIT INCIDENT INVOLVING CAR 18 (STR) WILL BE INVESTIGATED AFTER THE RACE - FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS – PRACTICE START INFRINGEMENT |
| 13:03:35 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:16:59 | 53 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 19

## 2025 R17 Azerbaijan Grand Prix (session 9904)
- scheduled_laps: 51 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 968, 'stints': 41, 'drivers': 20, 'pit': 21, 'position': 334, 'race_control': 73, 'weather': 156, 'starting_grid': 0, 'session_result': 20}
- max lap 51; drivers reaching it: 17; lap counts (top 5): {51: 17, 50: 2, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 10:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 10:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 11:03:54 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 11:05:16 | 1 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 11:12:23 | 4 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 11:13:56 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 12:37:19 | 51 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 316.0 | 743.0 | 7.1 |

Laps (any driver) flagged: SC 76, VSC 0, red 0, yellow 121

## 2025 R18 Singapore Grand Prix (session 9896)
- scheduled_laps: 62 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1229, 'stints': 43, 'drivers': 20, 'pit': 23, 'position': 454, 'race_control': 121, 'weather': 161, 'starting_grid': 0, 'session_result': 20}
- max lap 62; drivers reaching it: 9; lap counts (top 5): {62: 9, 61: 11}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 11:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 11:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 12:03:32 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 13:43:54 | 62 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 40

## 2025 R19 United States Grand Prix (session 9888)
- scheduled_laps: 56 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1067, 'stints': 41, 'drivers': 20, 'pit': 21, 'position': 387, 'race_control': 81, 'weather': 154, 'starting_grid': 0, 'session_result': 20}
- max lap 56; drivers reaching it: 16; lap counts (top 5): {56: 16, 55: 3, 6: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 18:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 18:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 19:03:40 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:14:35 | 7 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 19:17:55 | 8 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 19:18:08 | 9 | Flag | CLEAR | Track | TRACK CLEAR |
| 20:37:40 | 56 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 875.0 | 1075.0 | 3.3 |

Laps (any driver) flagged: SC 0, VSC 38, red 0, yellow 97

## 2025 R20 Mexico City Grand Prix (session 9877)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1266, 'stints': 47, 'drivers': 20, 'pit': 27, 'position': 593, 'race_control': 78, 'weather': 162, 'starting_grid': 0, 'session_result': 20}
- max lap 71; drivers reaching it: 11; lap counts (top 5): {71: 11, 70: 5, 68: 1, 35: 1, 26: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 19:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 19:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 20:03:16 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 21:39:16 | 70 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 21:40:44 | 71 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 21:40:56 | 71 | Flag | CLEAR | Track | TRACK CLEAR |
| 21:41:13 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 5956.0 | 6044.0 | 1.5 |

Laps (any driver) flagged: SC 0, VSC 31, red 0, yellow 120

## 2025 R21 São Paulo Grand Prix (session 9869)
- scheduled_laps: 71 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1252, 'stints': 57, 'drivers': 20, 'pit': 37, 'position': 759, 'race_control': 58, 'weather': 152, 'starting_grid': 0, 'session_result': 20}
- max lap 71; drivers reaching it: 17; lap counts (top 5): {71: 17, 38: 1, 6: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 16:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 17:03:14 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 17:04:58 | 2 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 17:11:15 | 5 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 17:11:42 | 5 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:13:31 | 7 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 17:16:26 | 8 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 17:16:38 | 8 | Flag | CLEAR | Track | TRACK CLEAR |
| 18:35:14 | 71 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 298.0 | 675.0 | 6.3 |
| vsc | 811.0 | 986.0 | 2.9 |

Laps (any driver) flagged: SC 76, VSC 37, red 0, yellow 130

## 2025 R22 Las Vegas Grand Prix (session 9858)
- scheduled_laps: 50 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 888, 'stints': 44, 'drivers': 20, 'pit': 23, 'position': 329, 'race_control': 63, 'weather': 141, 'starting_grid': 0, 'session_result': 20}
- max lap 50; drivers reaching it: 15; lap counts (top 5): {50: 15, 49: 2, 36: 1, 3: 1, 1: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 03:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 03:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 04:04:09 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 04:07:08 | 2 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 04:09:53 | 4 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 04:10:06 | 4 | Flag | CLEAR | Track | TRACK CLEAR |
| 04:29:40 | 16 | SafetyCar |  |  | VIRTUAL SAFETY CAR DEPLOYED |
| 04:30:43 | 16 | SafetyCar |  |  | VIRTUAL SAFETY CAR ENDING |
| 04:30:56 | 16 | Flag | CLEAR | Track | TRACK CLEAR |
| 05:25:17 | 50 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| vsc | 428.0 | 593.0 | 2.8 |
| vsc | 1780.0 | 1843.0 | 1.0 |

Laps (any driver) flagged: SC 0, VSC 63, red 0, yellow 76

## 2025 R23 Qatar Grand Prix (session 9850)
- scheduled_laps: 57 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1070, 'stints': 61, 'drivers': 20, 'pit': 41, 'position': 476, 'race_control': 81, 'weather': 149, 'starting_grid': 0, 'session_result': 20}
- max lap 57; drivers reaching it: 13; lap counts (top 5): {57: 13, 56: 5, 42: 1, 7: 1}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 15:20:01 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 15:30:01 | 1 | Other |  |  | PIT EXIT CLOSED |
| 16:03:27 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 16:13:01 | 7 | SafetyCar |  |  | SAFETY CAR DEPLOYED |
| 16:20:04 | 10 | SafetyCar |  |  | SAFETY CAR IN THIS LAP |
| 16:20:49 | 10 | Flag | CLEAR | Track | TRACK CLEAR |
| 17:28:05 | 57 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

| source | start_s | end_s | minutes |
|---|---|---|---|
| sc | 781.0 | 1204.0 | 7.0 |

Laps (any driver) flagged: SC 76, VSC 0, red 0, yellow 57

## 2025 R24 Abu Dhabi Grand Prix (session 9839)
- scheduled_laps: 58 (winner_laps_actual); grid: position_first_record
- endpoint rows: {'laps': 1156, 'stints': 47, 'drivers': 20, 'pit': 27, 'position': 668, 'race_control': 109, 'weather': 154, 'starting_grid': 0, 'session_result': 20}
- max lap 58; drivers reaching it: 16; lap counts (top 5): {58: 16, 57: 4}

**Race-control messages used for SC / VSC / red periods**

| date_utc | lap | category | flag | scope | message |
|---|---|---|---|---|---|
| 12:20:00 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 12:30:00 | 1 | Other |  |  | PIT EXIT CLOSED |
| 13:03:28 | 1 | Flag | GREEN | Track | GREEN LIGHT - PIT EXIT OPEN |
| 14:29:35 | 58 | Flag | CHEQUERED | Track | CHEQUERED FLAG |

**Rebuilt SC / VSC / red periods (session seconds)**

_none_

Laps (any driver) flagged: SC 0, VSC 0, red 0, yellow 0
