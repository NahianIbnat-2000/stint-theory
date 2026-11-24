# STINT THEORY data coverage report

Generated 2026-11-23T21:09:34+00:00 from the files in data/raw. All counts come from the data on disk.

## Sessions and laps by season

| season | races_listed | ingest_status | validated | passed_validation | races_in_sample | driver_laps | clean_green_laps | clean_green_share | strict_clean_share | stints |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | 22 | downloaded: 22 | 22 | 22 | 22 | 24479 | 19192 | 0.784 | 0.7529 | 1338 |
| 2024 | 24 | downloaded: 24 | 24 | 24 | 24 | 26629 | 20801 | 0.7811 | 0.7535 | 1287 |
| 2025 | 24 | downloaded: 24 | 24 | 23 | 23 | 25706 | 20290 | 0.7893 | 0.7623 | 1270 |

## Share of rows with a non-missing value

| season | lap_time_s | s1_s | s2_s | s3_s | tyre_life | compound_relative | position_end_of_lap | grid_position | track_temp_c | air_temp_c | scheduled_laps |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | 0.9952 | 0.9913 | 0.9962 | 0.9933 | 1 | 1 | 0.9959 | 1 | 0.9993 | 0.9993 | 1 |
| 2024 | 0.9968 | 0.9935 | 0.9982 | 0.9971 | 1 | 0.9999 | 0.9979 | 1 | 0.9995 | 0.9995 | 1 |
| 2025 | 0.998 | 0.9957 | 0.9976 | 0.9972 | 1 | 1 | 0.998 | 1 | 1 | 1 | 1 |

## Share of rows carrying each exclusion flag

Flags overlap, so shares do not add up.

| season | flag_pit_in | flag_pit_out | flag_first_lap | flag_missing_time | flag_sc | flag_vsc | flag_red | flag_yellow | flag_post_neutralisation | flag_deleted | flag_not_accurate | flag_fastf1_generated | flag_non_slick | flag_rain | flag_beyond_scheduled | flag_pace_outlier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | 0.0373 | 0.0373 | 0.0179 | 0.0048 | 0.045 | 0.0138 | 0.0063 | 0.0779 | 0.0181 | 0.015 | 0.0 | 0.0 | 0.0324 | 0.0277 | 0.0014 | 0.0349 |
| 2024 | 0.031 | 0.0317 | 0.018 | 0.0032 | 0.0362 | 0.0105 | 0.0019 | 0.0574 | 0.0115 | 0.0123 | 0.0 | 0.0 | 0.0827 | 0.0601 | 0.0001 | 0.0336 |
| 2025 | 0.0312 | 0.0312 | 0.0179 | 0.002 | 0.0597 | 0.0163 | 0.0 | 0.0786 | 0.0174 | 0.012 | 0.0 | 0.0 | 0.0512 | 0.014 | 0.0 | 0.0291 |

## Pace-outlier rate by tyre age

Among laps with no other exclusion flag, so this is the flag's own effect. Should be roughly flat. A rise with tyre age means it is removing high-wear laps.

| season | tyre_life_bin | laps | outlier_share |
|---|---|---|---|
| 2023 | (0, 5] | 2785 | 0.075 |
| 2023 | (10, 15] | 3913 | 0.0281 |
| 2023 | (15, 20] | 3055 | 0.036 |
| 2023 | (20, 30] | 3305 | 0.0324 |
| 2023 | (30, 80] | 1699 | 0.0453 |
| 2023 | (5, 10] | 4435 | 0.0336 |
| 2024 | (0, 5] | 3302 | 0.0591 |
| 2024 | (10, 15] | 4007 | 0.027 |
| 2024 | (15, 20] | 3247 | 0.032 |
| 2024 | (20, 30] | 3744 | 0.0329 |
| 2024 | (30, 80] | 2020 | 0.0436 |
| 2024 | (5, 10] | 4481 | 0.0261 |
| 2025 | (0, 5] | 2693 | 0.0839 |
| 2025 | (10, 15] | 4110 | 0.0251 |
| 2025 | (15, 20] | 3301 | 0.0227 |
| 2025 | (20, 30] | 4173 | 0.028 |
| 2025 | (30, 80] | 1814 | 0.0364 |
| 2025 | (5, 10] | 4199 | 0.0257 |

## Raw compound labels

| season | compound_raw | laps |
|---|---|---|
| 2023 | HARD | 11894 |
| 2023 | INTERMEDIATE | 743 |
| 2023 | MEDIUM | 8294 |
| 2023 | SOFT | 3498 |
| 2023 | WET | 50 |
| 2024 | HARD | 13801 |
| 2024 | INTERMEDIATE | 2166 |
| 2024 | MEDIUM | 8879 |
| 2024 | SOFT | 1746 |
| 2024 | UNKNOWN | 2 |
| 2024 | WET | 35 |
| 2025 | HARD | 10512 |
| 2025 | INTERMEDIATE | 1315 |
| 2025 | MEDIUM | 10564 |
| 2025 | SOFT | 3315 |

## How the relative compound was assigned

| season | compound_map_method | laps |
|---|---|---|
| 2023 | reported | 24479 |
| 2024 | missing | 2 |
| 2024 | reported | 26627 |
| 2025 | reported | 25706 |

## OpenF1 reconstruction checks (summed over races)

In-laps are inferred as the lap before an out-lap; `pit_rows_on_inferred_in_lap` should be close to `pit_table_rows`. Unpaired or unmatched safety-car messages need a manual look.

| season | lap_rows_without_driver_or_lap | duplicate_lap_rows_dropped | laps_without_stint | laps_stint_extended_by_one | in_laps_inferred | pit_table_rows | pit_rows_on_inferred_in_lap | pit_rows_on_out_lap | deleted_laps | laps_missing_start_time | rc_messages | sc_unpaired | vsc_unpaired | red_unpaired | yellow_capped | safetycar_msgs_unmatched | sc_restart_periods | vsc_upgraded_to_sc | closed_by_chequered | starting_grid_rows | session_result_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | 0 | 0 | 0 | 92 | 912 | 693 | 693 | 37 | 368 | 18 | 1896 | 0 | 0 | 0 | 25 | 0 | 2 | 1 | 0 | 0 | 439 |
| 2024 | 0 | 0 | 0 | 41 | 825 | 825 | 825 | 35 | 327 | 14 | 2174 | 0 | 0 | 0 | 34 | 0 | 1 | 2 | 2 | 0 | 479 |
| 2025 | 0 | 0 | 0 | 40 | 817 | 821 | 815 | 73 | 309 | 19 | 2216 | 0 | 0 | 0 | 39 | 0 | 1 | 0 | 1 | 0 | 479 |

## Races with incomplete lap data

Lap rows present / laps driven per the classification. Below 90% the race is excluded from the sample.

| season | round | event_name | lap_completeness | passed |
|---|---|---|---|---|
| 2025 | 6 | Miami Grand Prix | 0.5579 | False |

## Validation issues (warnings and errors)

| season | check | severity | sessions | rows |
|---|---|---|---|---|
| 2023 | lap_time_missing | warning | 22 | 118 |
| 2023 | laps_exceed_scheduled | warning | 14 | 35 |
| 2024 | compound_unknown_label | warning | 1 | 2 |
| 2024 | lap_time_missing | warning | 23 | 86 |
| 2024 | laps_exceed_scheduled | warning | 2 | 2 |
| 2024 | sector_sum_mismatch_gt_0.1s | warning | 1 | 17 |
| 2025 | lap_completeness | error | 1 | 558 |
| 2025 | lap_time_missing | warning | 20 | 54 |
| 2025 | laps_exceed_scheduled | warning | 1 | 1 |
