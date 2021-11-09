from numpy.core.numeric import full
from src.datas import PEAK_DF
from src.rate_table import COMPREHENSIVE_PUBLIC_RATE_TABLE, COMPREHENSIVE_RATE_TABLE, SINGLE_RATE_TABLE, COMPREHENSIVE_HOUSEHOLD_RATE_TABLE
import math
import pandas as pd
from src.datas import KEPCO_FEE

# set common
skip_calc = ["사용량 (kwh)"]
bill_step = ['전기요금계', '4사 5입', '전력산업기반기금 (절사)']

# set household
household_name = ["{}01 호".format(_) for _ in range(1, 11)]
household_kwh = [150, 180, 220, 210, 310, 300, 270, 190, 250, 260]


class HOUSEHOLD:
    def __init__(self, rate_table, name="", kwh=0, ):
        self.name = name
        self.kwh = kwh
        self.rate_table = rate_table

    def calc_meter(self):
        self.fee_dict = {
            "사용량 (kwh)": self.kwh,
            "기본요금": self.basic,
            "전력량요금": self.electricity_rate,
            "기후환경요금": self.env_fee,
            "연료비조정액": self.fuel_cost,
            "필수사용량보장공제": self.deduction,
        }

        self.fee = 0
        for _ in self.fee_dict.keys():
            if _ in skip_calc:
                continue
            self.fee += self.fee_dict[_]

        self.fee_dict['전기요금계'] = self.fee
        self.fee_dict['부가세'] = self.vat
        self.fee_dict['4사 5입'] = self.vat_process
        self.fee_dict['전력산업기반기금'] = self.infra_fund
        self.fee_dict['전력산업기반기금 (절사)'] = self.infra_fund_process
        self.fee_dict['청구금액'] = self.bill
        self.fee_dict['청구금액 (절사)'] = self.bill_process


def get_const_households(rate_type):
    CONST_HOUSEHOLDS = list()
    rate_table = COMPREHENSIVE_HOUSEHOLD_RATE_TABLE if rate_type == "종합계약" else SINGLE_RATE_TABLE
    for idx, kwh in enumerate(household_kwh):
        CONST_HOUSEHOLDS.append(
            HOUSEHOLD(name=household_name[idx], kwh=kwh, rate_table=rate_table))

    return CONST_HOUSEHOLDS


class MGMTOFFICE:
    def __init__(self, rate_type, households=None, now_month=2, APT_METER=3000, peak_df=PEAK_DF):
        self.rate_contract = ComprehensiveContract(
            peak_df=peak_df,
            now_month=now_month
        ) if rate_type == "종합계약" else SingleContract(now_month=now_month)
        self.APT_METER = APT_METER
        self.households = get_const_households(
            rate_type=rate_type) if households == None else households
        self.now_month = now_month

    def __repr__(self) -> str:
        return "########## 관리사무소 ##########\n" +\
            "---------- 계약정보 ----------\n\n" +\
            "{}".format(self.households) +\
            "{}\n".format(self.rate_contract) +\
            "#############################\n"

    def bill(self):
        return self.rate_contract.calc_meter(households=self.households, apt_meter=self.APT_METER)


class RATECONTRACT:
    def __init__(self, rate_type, now_month):
        self.rate_type = rate_type
        self.now_month = now_month
        if rate_type == "종합계약":
            self.rate_table = COMPREHENSIVE_RATE_TABLE
        else:
            self.rate_table = SINGLE_RATE_TABLE

    def __repr__(self) -> str:
        return "계약 : {}\n".format(self.rate_type) +\
            "요금제 : \n{}\n".format(self.rate_table)

    def calc_meter(self, households):
        bill = pd.DataFrame(columns=['사용량 (kwh)', '기본요금', '전력량요금', '기후환경요금', '연료비조정액', '필수사용량보장공제', '전기요금계',
                                     '부가세', '4사 5입'	, '전력산업기반기금', '전력산업기반기금 (절사)', '청구금액', '청구금액 (절사)'])
        for _ in households:
            _.calc_meter()
            bill = bill.append(_.fee_dict, ignore_index=True)

        bill.index = [_.name for _ in households]
        return bill


class PUBLIC:
    def __init__(self, apt_meter, rate_type, kwh, peak_df, now_month):
        self.apt_meter = apt_meter
        self.maximum_power_demand = None
        self.kwh = kwh
        self.rate_type = rate_type
        self.rate_table = COMPREHENSIVE_PUBLIC_RATE_TABLE if rate_type == "종합계약" else SINGLE_RATE_TABLE
        self.peak_df = peak_df
        self.now_month = now_month

    def calc_meter(self):
        if self.rate_type == "종합계약":
            peak_calc_month = [1, 2, 7, 8, 9, 12] + [self.now_month]
            peak_calc_index = list()
            for _ in self.peak_df.index:
                if (_.month in peak_calc_month):
                    peak_calc_index.append(_)

            self.maximum_power_demand = self.peak_df.loc[peak_calc_index]['peak (kW)'].max(
            )

        self.fee_dict = {
            "사용량 (kwh)": self.kwh,
            "기본요금": self.basic,
            "전력량요금": self.electricity_rate,
            "기후환경요금": self.env_fee,
            "연료비조정액": self.fuel_cost,
        }

        self.fee = 0
        for _ in self.fee_dict.keys():
            if _ in skip_calc:
                continue
            self.fee += self.fee_dict[_]

        self.fee_dict['전기요금계'] = self.fee
        self.fee_dict['부가세'] = self.vat
        self.fee_dict['4사 5입'] = self.vat_process
        self.fee_dict['전력산업기반기금'] = self.infra_fund
        self.fee_dict['전력산업기반기금 (절사)'] = self.infra_fund_process
        self.fee_dict['청구금액'] = self.bill
        self.fee_dict['청구금액 (절사)'] = self.bill_process

        return self.fee_dict


class ComprehensiveContract(RATECONTRACT):
    def __init__(self, now_month, peak_df=PEAK_DF):
        super().__init__(rate_type="종합계약", now_month=now_month)
        self.peak_df = peak_df

    def calc_meter(self, households, apt_meter):
        bill = super().calc_meter(households)
        households_sum_dict = dict()
        for _ in bill:
            households_sum_dict[_] = bill[_].sum()

        sum_row_name = "[2월] 세대 전체 요금 합산"
        bill = bill.append(
            pd.Series(households_sum_dict, name=sum_row_name),
        )

        households_kwh = bill.loc[sum_row_name]['사용량 (kwh)']
        public_row_name = "[2월] 공동사용설비요금"
        public_dict = PUBLIC(rate_type=self.rate_type,
                             apt_meter=apt_meter,
                             kwh=(apt_meter - households_kwh),
                             peak_df=self.peak_df,
                             now_month=self.now_month).calc_meter()
        bill = bill.append(
            pd.Series(public_dict, name=public_row_name)
        )

        all_sum_dict = dict()
        all_sum_list = [sum_row_name, public_row_name]
        for _ in bill:
            all_sum_dict[_] = bill.loc[all_sum_list][_].sum()
        bill = bill.append(
            pd.Series(all_sum_dict, name="[2월] 관리사무소 청구서")
        )

        public_bill = round(bill.loc[public_row_name]['청구금액 (절사)'] / len(
            households))
        bill['공동전기사용료'] = [public_bill for _ in range(
            0, len(households))] + [0, 0, 0]

        bill['최종청구금액'] = [public_bill + bill.iloc[_]['청구금액 (절사)'] for _ in range(
            0, len(households))] + [0, 0, 0]

        return bill.fillna(0)


class SingleContract(RATECONTRACT):
    def __init__(self, now_month):
        super().__init__(rate_type="단일계약", now_month=now_month)

    def calc_all_meter(self):
        self.fee_dict = dict()

        # mean kwh
        self.kwh = int(self.apt_meter / self.household_length)
        self.fee_dict = {
            "사용량 (kwh)": self.apt_meter,
            "기본요금": int(self.basic * self.household_length),
            "전력량요금": self.electricity_rate * self.household_length,
        }

        self.kwh = self.apt_meter
        self.fee_dict["기후환경요금"] = self.env_fee
        self.fee_dict["연료비조정액"] = self.fuel_cost

        self.fee = 0
        for _ in self.fee_dict.keys():
            if _ in skip_calc:
                continue
            self.fee += self.fee_dict[_]

        self.fee_dict['전기요금계'] = self.fee
        self.fee_dict['부가세'] = self.vat
        self.fee_dict['4사 5입'] = self.vat_process
        self.fee_dict['전력산업기반기금'] = self.infra_fund
        self.fee_dict['전력산업기반기금 (절사)'] = self.infra_fund_process
        self.fee_dict['청구금액'] = self.bill
        self.fee_dict['청구금액 (절사)'] = self.bill_process

        return self.fee_dict

    def calc_meter(self, households, apt_meter):
        self.household_length = len(households)
        self.apt_meter = apt_meter
        bill = super().calc_meter(households)
        households_sum_dict = dict()
        for _ in bill:
            households_sum_dict[_] = bill[_].sum()

        sum_row_name = "[2월] 세대 전체 요금 합산"
        bill = bill.append(
            pd.Series(households_sum_dict, name=sum_row_name),
        )

        all_dict = self.calc_all_meter()
        public_dict = dict()

        public_dict['사용량 (kwh)'] = apt_meter - \
            bill.loc[sum_row_name]['사용량 (kwh)']
        public_dict['청구금액 (절사)'] = all_dict['청구금액 (절사)'] - \
            bill.loc[sum_row_name]['청구금액 (절사)']

        public_row_name = "[2월] 공동사용설비요금"
        bill = bill.append(
            pd.Series(public_dict, name=public_row_name)
        )

        mgmt_bill_name = "[2월] 관리사무소 청구서"
        bill = bill.append(
            pd.Series(all_dict, name=mgmt_bill_name)
        )

        public_bill = round(bill.loc[public_row_name]['청구금액 (절사)'] / len(
            households))
        bill['공동전기사용료'] = [public_bill for _ in range(
            0, len(households))] + [0, 0, 0]

        bill['최종청구금액'] = [public_bill + bill.iloc[_]['청구금액 (절사)'] for _ in range(
            0, len(households))] + [0, 0, 0]

        return bill.fillna(0)


@property
def ENVFEE(self):
    unit = KEPCO_FEE['기후환경요금']
    return int(self.kwh * unit)


@property
def FUELCOST(self):
    unit = KEPCO_FEE['연료비조정액']
    return int(self.kwh * unit)


@property
def VAT(self):
    return self.fee * 0.1


@property
def VATPROCESS(self):
    return round(self.vat)


@property
def INFRAFUND(self):
    return self.fee * 0.037


@property
def DEDUCTION(self):
    is_deduction = True if (self.kwh > 1000) \
        or (self.kwh <= 200) else False
    if is_deduction:
        rate_type = self.rate_table['type'].values[0]
        if rate_type == "주택용 저압":
            unit = KEPCO_FEE['필수사용량 보장공제 (월 1,000 kWh 초과), 저압'] if (self.kwh > 1000) \
                else KEPCO_FEE['필수사용량 보장공제 (월 200 kWh 이하), 저압']
        else:
            unit = KEPCO_FEE['필수사용량 보장공제 (월 1,000 kWh 초과), 고압'] if (self.kwh > 1000) \
                else KEPCO_FEE["필수사용량 보장공제 (월 200 kWh 이하), 고압"]

        return (unit * (self.kwh - 1000) if (self.kwh > 1000)
                else unit) * -1
    else:
        return 0


@property
def INFRAFUNDPROCESS(self):
    return math.floor(self.infra_fund / 10) * 10


@property
def BASIC(self):
    return self.rate_table[
        self.rate_table['max kWh'] >= self.kwh
    ]['basic'].iloc[0]


@property
def BASIC_PUBLIC(self):
    if self.maximum_power_demand != None:
        charge_applied_power = self.maximum_power_demand *\
            (self.kwh / self.apt_meter)
        return int(self.rate_table[
            self.rate_table['max kWh'] >= self.kwh
        ]['basic'].iloc[0] * charge_applied_power)
    else:
        return self.rate_table[
            self.rate_table['max kWh'] >= self.kwh
        ]['basic'].iloc[0] * 1


@property
def ELECTRICITYRATE_PROGRESSIVETAX(self):
    rate = 0
    usage = self.kwh
    step_bak = 0
    step_bak = 0
    idx = 0

    while usage > 0:
        progressive_tax = self.rate_table['fee'].iloc[idx]
        max_kwh = self.rate_table['max kWh'].iloc[idx]

        step_kwh = usage if usage < max_kwh else max_kwh - step_bak
        rate += int(progressive_tax * step_kwh)

        usage -= step_kwh
        step_bak = max_kwh
        idx += 1

    return rate


@property
def BILL(self):
    fee = 0
    for _ in self.fee_dict.keys():
        if _ in bill_step:
            fee += self.fee_dict[_]
    return fee


@property
def BILLPROCESS(self):
    return math.floor(self.bill / 10) * 10


PUBLIC.basic = BASIC_PUBLIC
PUBLIC.electricity_rate = ELECTRICITYRATE_PROGRESSIVETAX
PUBLIC.env_fee = ENVFEE
PUBLIC.fuel_cost = FUELCOST
PUBLIC.vat = VAT
PUBLIC.vat_process = VATPROCESS
PUBLIC.infra_fund = INFRAFUND
PUBLIC.infra_fund_process = INFRAFUNDPROCESS
PUBLIC.bill = BILL
PUBLIC.bill_process = BILLPROCESS

HOUSEHOLD.basic = BASIC
HOUSEHOLD.electricity_rate = ELECTRICITYRATE_PROGRESSIVETAX
HOUSEHOLD.env_fee = ENVFEE
HOUSEHOLD.fuel_cost = FUELCOST
HOUSEHOLD.deduction = DEDUCTION
HOUSEHOLD.vat = VAT
HOUSEHOLD.vat_process = VATPROCESS
HOUSEHOLD.infra_fund = INFRAFUND
HOUSEHOLD.infra_fund_process = INFRAFUNDPROCESS
HOUSEHOLD.bill = BILL
HOUSEHOLD.bill_process = BILLPROCESS

SingleContract.basic = BASIC
SingleContract.electricity_rate = ELECTRICITYRATE_PROGRESSIVETAX
SingleContract.env_fee = ENVFEE
SingleContract.fuel_cost = FUELCOST
SingleContract.vat = VAT
SingleContract.vat_process = VATPROCESS
SingleContract.infra_fund = INFRAFUND
SingleContract.infra_fund_process = INFRAFUNDPROCESS
SingleContract.bill = BILL
SingleContract.bill_process = BILLPROCESS
