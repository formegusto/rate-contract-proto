from pymongo import MongoClient as mc
import datetime as dt
from numpy import dot
from numpy.linalg import norm
from scipy.spatial import distance
import pandas as pd
import IPython
import IPython.display
from src.objects import *
from src.rate_table import *


class KETIDB:
    def __init__(self):
        self.mongo_uri = "mongodb://localhost:27017"

    def connect(self):
        print("connect KETIDB,,,")
        self.client = mc(self.mongo_uri)
        self.keti_pr_db = self.client.keti_pattern_recognition
        self.household_col = self.keti_pr_db.household_info
        self.uid_check = []
        print("connect success!!")

    def close(self):
        print("disconnect KETIDB,,,")
        self.client.close()
        self.uid_check = []
        print("disconnect success!!")

    def find(self, is_process=True):
        IPython.display.clear_output()
        print("### DB FIND START ###")
        db_cursor = self.household_col.find({})

        datas = list()
        for _ in db_cursor:
            datas.append(_)

        if is_process:
            print("### Data Process (dict -> dataframe) START ###")
            datas_df = pd.DataFrame()

            for _ in datas:
                uid = _['uid']
                powers = [_['power'] for _ in _['timeslot']]
                datas_df[uid] = powers

            datas_df.index = [dt.datetime.strptime(
                _['time'], "%Y-%m-%d T%H:%M Z") for _ in datas[0]['timeslot']]

            datas = datas_df
        print("### DB FIND SUCCESS :) ###")
        return datas


class DPPSUPPORTER:
    def __init__(self, datas, now_month):
        IPython.display.clear_output()
        print("### SET DATAS ###")
        self.datas = datas
        self.now_month = now_month
        print("### SET DATAS SUCCESS :) ###")

        print("### SET PEAK ###")

        peak_year = 2021
        peak_month = [_ for _ in range(1, 13)]
        self.peak_df = pd.DataFrame(columns=['peak (kW)'])
        peak_date = list()

        for m in peak_month:
            peak = round(
                (datas.loc[datas.index.month == m] * 4).sum(axis=1).max())
            peak_date.append(
                dt.datetime(
                    peak_year,
                    m,
                    1
                )
            )
            self.peak_df = self.peak_df.append(
                {
                    "peak (kW)": peak,
                }, ignore_index=True)

        self.peak_df.index = peak_date

        print("### SET PEAK SUCCESS :) ###")

        print("### SET SUM DATAS ###")

        sum_df = pd.DataFrame(
            datas.loc[datas.index.month == now_month].sum()).T.copy()

        sum_df.index = ['kwh']
        self.sum_df = round(sum_df)

        print("### SET SUM DATAS SUCCESS ###")

    def get_households(self, rate_type):
        print(COMPREHENSIVE_HOUSEHOLD_RATE_TABLE)
        rate_table = COMPREHENSIVE_HOUSEHOLD_RATE_TABLE(
            self.now_month) if rate_type == "종합계약" else SINGLE_RATE_TABLE(self.now_month)
        households = list()

        print(rate_table)

        for col in self.sum_df:
            households.append(
                HOUSEHOLD(
                    name=col,
                    kwh=self.sum_df[col]['kwh'],
                    rate_table=rate_table,
                    now_month=self.now_month
                )
            )

        return households
