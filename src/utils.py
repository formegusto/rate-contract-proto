import math

from src.datas import KEPCO_FEE


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
    return round(self.VAT * 0.1)


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
    return math.floor(self.INFRAFUND / 10) * 10


@property
def BASIC(self):
    return self.rate_table[
        self.rate_table['max kWh'] >= self.kwh
    ]['basic'].iloc[0]


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
