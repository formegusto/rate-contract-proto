import datetime as dt
import pandas as pd
from src.rate_table import COMPREHENSIVE_HOUSEHOLD_RATE_TABLE, SINGLE_RATE_TABLE
from src.objects import *

# set kepco fee
KEPCO_FEE = {
    "환경비용차감": -5,
    "기후환경요금": 5.3,
    "연료비조정액": -3,
    "필수사용량 보장공제 (월 1,000 kWh 초과), 저압": 709.5,
    "필수사용량 보장공제 (월 1,000 kWh 초과), 고압": 574.6,
    "필수사용량 보장공제 (월 200 kWh 이하), 저압": 4000,
    "필수사용량 보장공제 (월 200 kWh 이하), 고압": 2500,
}

# Set Peak
peak_month = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
peak_arr = [95, 95, 94, 90, 91, 72, 66, 87, 91, 85, 100, 95]

peak_year = 2020
peak_date = list()
PEAK_DF = pd.DataFrame(columns=["peak (kW)"])

for idx, _ in enumerate(peak_month):
    peak_date.append(
        dt.datetime(
            peak_year,
            _,
            1
        )
    )
    PEAK_DF = PEAK_DF.append({
        "peak (kW)": peak_arr[idx]
    }, ignore_index=True)

    if _ == 12:
        peak_year += 1

PEAK_DF.index = peak_date

# set household
household_name = ["{}01 호".format(_) for _ in range(1, 11)]
household_kwh = [150, 180, 220, 210, 310, 300, 270, 190, 250, 260]


def get_const_households(rate_type):
    CONST_HOUSEHOLDS = list()
    rate_table = COMPREHENSIVE_HOUSEHOLD_RATE_TABLE if rate_type == "종합계약" else SINGLE_RATE_TABLE
    for idx, kwh in enumerate(household_kwh):
        CONST_HOUSEHOLDS.append(
            HOUSEHOLD(name=household_name[idx], kwh=kwh, rate_table=rate_table))

    return CONST_HOUSEHOLDS
