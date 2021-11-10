import pandas as pd
from functools import reduce

from src.objects import get_season

fee_dict = dict()

# 주택용전력 (저압) setting
household_low_pressure_fee = {
    "type": ["주택용 저압" for _ in range(0, 12)],
    "max kWh": reduce(lambda acc, cur: acc + [200, 400, float("inf")], range(0, 3), [])
    + [300, 450, float("inf")],
    "basic": reduce(lambda acc, cur: acc + [910, 1600, 7300], range(0, 4), []),
    "fee": reduce(lambda acc, cur: acc + [88.3, 182.9, 275.6], range(0, 4), []),
    "unit": ["kWh" for _ in range(0, 12)],
    "season": ["spring" for _ in range(0, 3)] + ["autumn" for _ in range(0, 3)] +
    ["winter" for _ in range(0, 3)] + ["summer" for _ in range(0, 3)]
}
household_low_pressure_fee_df = pd.DataFrame(household_low_pressure_fee,
                                             columns=['type', 'max kWh', 'basic', 'fee', 'unit', 'season'])
fee_dict['주택용전력 (저압)'] = household_low_pressure_fee_df

# 주택용 전력 (고압) setting
household_high_pressure_fee = {
    "type": ["주택용 고압" for _ in range(0, 12)],
    "max kWh": reduce(lambda acc, cur: acc + [200, 400, float("inf")], range(0, 3), [])
    + [300, 450, float("inf")],
    "basic": reduce(lambda acc, cur: acc + [730, 1260, 6060], range(0, 4), []),
    "fee": reduce(lambda acc, cur: acc + [73.3, 142.3, 210.6], range(0, 4), []),
    "unit": ["kWh" for _ in range(0, 12)],
    "season": ["spring" for _ in range(0, 3)] + ["autumn" for _ in range(0, 3)] +
    ["winter" for _ in range(0, 3)] + ["summer" for _ in range(0, 3)]
}
household_high_pressure_fee_df = pd.DataFrame(household_high_pressure_fee,
                                              columns=['type', 'max kWh', 'basic', 'fee', 'unit', 'season'])
fee_dict['주택용전력 (고압)'] = household_high_pressure_fee_df

# 일반용전력(갑) 1 setting
public_fee = {
    "type": ["일반용전력(갑) 1, 저압" for _ in range(0, 4)] +
    ["일반용전력(갑) 1, 고압A, 선택 1" for _ in range(0, 4)] +
    ["일반용전력(갑) 1, 고압A, 선택 2" for _ in range(0, 4)] +
    ["일반용전력(갑) 1, 고압B, 선택 1" for _ in range(0, 4)] +
    ["일반용전력(갑) 1, 고압B, 선택 2" for _ in range(0, 4)],
    "max kWh": [float("inf") for _ in range(0, 20)],
    "basic": reduce(lambda acc, cur: acc + [cur for _ in range(0, 4)],
                    [6160, 7170, 8230, 7170, 8230], []),
    "fee": [60.2, 100.7, 60.2, 87.3] +
    [66.9, 110.9, 66.9, 98.6] +
    [62.6, 106.9, 62.6, 93.3] +
    [65.8, 108.9, 65.8, 95.6] +
    [60.5, 103.5, 60.5, 90.3],
    "unit": ["kWh" for _ in range(0, 20)],
    "season": reduce(lambda acc, cur: acc + ["spring", "summer", "autumn", "winter"],
                     range(0, 5), [])
}
public_fee_df = pd.DataFrame(public_fee,
                             columns=['type', 'max kWh', 'basic', 'fee', 'unit', 'season'])
fee_dict['일반용전력(갑) 1'] = public_fee_df

# 전체통합
RATE_TABLE = pd.DataFrame(
    columns=['type', 'max kWh', 'basic', 'fee', 'unit', 'season'])
for _ in fee_dict.values():
    RATE_TABLE = pd.concat([RATE_TABLE, _], ignore_index=True)

# 종합계약 요금표


def COMPREHENSIVE_RATE_TABLE(now_month):
    return RATE_TABLE[
        ((RATE_TABLE['type'] == "주택용 저압") | (RATE_TABLE['type'] == "일반용전력(갑) 1, 고압A, 선택 2")) &
        (RATE_TABLE['season'] == get_season(now_month))
    ]


def COMPREHENSIVE_HOUSEHOLD_RATE_TABLE(now_month):
    return RATE_TABLE[
        (RATE_TABLE['type'] == "주택용 저압") &
        (RATE_TABLE['season'] == get_season(now_month))
    ]


def COMPREHENSIVE_PUBLIC_RATE_TABLE(now_month):
    return RATE_TABLE[
        (RATE_TABLE['type'] == "일반용전력(갑) 1, 고압A, 선택 2") &
        (RATE_TABLE['season'] == get_season(now_month))
    ]

# 단일계약 요금표


def SINGLE_RATE_TABLE(now_month):
    return RATE_TABLE[
        (RATE_TABLE['type'] == "주택용 고압") &
        (RATE_TABLE['season'] == get_season(now_month))
    ]
