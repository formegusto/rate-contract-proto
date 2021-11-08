from src.datas import PEAK_DF, get_const_households
from src.rate_table import COMPREHENSIVE_RATE_TABLE, SINGLE_RATE_TABLE
from src.utils import *


class MGMTOFFICE:
    peak = PEAK_DF

    def __init__(self, rate_type, APT_METER=3000):
        self.rate_contract = ComprehensiveContract(
        ) if rate_type == "종합계약" else SingleContract()
        self.APT_METER = APT_METER
        self.households = get_const_households(rate_type=rate_type)

    def __repr__(self) -> str:
        return "########## 관리사무소 ##########\n" +\
            "---------- 계약정보 ----------\n\n" +\
            "{}".format(self.households) +\
            "{}\n".format(self.rate_contract) +\
            "#############################\n"


class RATECONTRACT:
    def __init__(self, rate_type):
        self.rate_type = rate_type
        if rate_type == "종합계약":
            self.rate_table = COMPREHENSIVE_RATE_TABLE
        else:
            self.rate_table = SINGLE_RATE_TABLE

    def __repr__(self) -> str:
        return "계약 : {}\n".format(self.rate_type) +\
            "요금제 : \n{}\n".format(self.rate_table)


class ComprehensiveContract(RATECONTRACT):
    def __init__(self):
        super().__init__(rate_type="종합계약")


class SingleContract(RATECONTRACT):
    def __init__(self):
        super().__init__(rate_type="단일계약")


class HOUSEHOLD:
    def __init__(self, rate_table, name="", kwh=0):
        self.name = name
        self.kwh = kwh
        self.rate_table = rate_table

    def calc_meter(self):
        self.fee_dict = {
            "사용량": self.kwh,
            "기본요금": self.basic,
            "전력량요금": self.electricity_rate,
            "기후환경요금": self.env_fee,
            "연료비조정액": self.fuel_cost,
            "필수사용량보장공제": self.deduction
        }


HOUSEHOLD.basic = BASIC
HOUSEHOLD.electricity_rate = ELECTRICITYRATE_PROGRESSIVETAX
HOUSEHOLD.env_fee = ENVFEE
HOUSEHOLD.fuel_cost = FUELCOST
HOUSEHOLD.deduction = DEDUCTION
