import requests
import datetime as dt
import pandas as pd
from io import StringIO

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 400)

class BMReports:
    def __init__(self):
        self.reportless_uri = "https://api.bmreports.com/BMRS/%s/v1"

    def get_settlemtns_report(self, report_name, API_Key, Settlement_Date, period, ServiceType):

        """
        """
        base_uri = self.reportless_uri % report_name
        params = {
            'APIKey': API_Key,
            'SettlementDate': Settlement_Date,
            'Period': period,
            'ServiceType': ServiceType,
        }
        response = requests.get(base_uri, params=params)
        df = pd.read_csv(StringIO(response.content.decode('utf-8')), skiprows=4)
        return df

def clean_Imbalance_Prices(Imbal_Prices):

    # Remove non essential data
    Imbal_Prices = Imbal_Prices[(Imbal_Prices["DocumentStatus"] == "Final") & (Imbal_Prices["ActiveFlag"] == "Y")]
    Imbal_Prices = Imbal_Prices[["SettlementDate","SettlementPeriod","ControlArea","ImbalancePriceAmount","PriceCategory"]]

    return Imbal_Prices

def clean_Imbalance_Volumes(Imbal_Vol):

    # Remove non essential data
    Imbal_Vol = Imbal_Vol[(Imbal_Vol["Document Status"] == "Final") & (Imbal_Vol["Active Flag"] == "Y")]
    Imbal_Vol = Imbal_Vol[["Settlement Date","Settlement Period","Control Area","Imbalance Quantity (MAW)"]]

    #Rename for standardisation with prices
    Imbal_Vol = Imbal_Vol.rename(columns={"Settlement Date": "SettlementDate", "Settlement Period": "SettlementPeriod", "Control Area": "ControlArea", "Imbalance Quantity (MAW)": "ImbalanceQuantity"})

    return Imbal_Vol

def create_half_hour_timestamps(Imbal_df):
    # convert date column to datetime
    Imbal_df['SettlementDate'] = pd.to_datetime(Imbal_df['SettlementDate'])

    # create a timedelta column for half-hour intervals
    half_hour_delta = pd.to_timedelta((Imbal_df['SettlementPeriod'] - 1) * 30, unit='minutes')

    # create start and end time columns
    Imbal_df['start_time'] = Imbal_df['SettlementDate'] + half_hour_delta
    Imbal_df['end_time'] = Imbal_df['SettlementDate'] + half_hour_delta + pd.Timedelta(minutes=30)
    return Imbal_df

def merge_dfs(Imbal_Prices,Imbal_Vol):
    #merge on rename columns
    Imbal_merged = Imbal_Prices.merge(Imbal_Vol, how="inner", on=["SettlementPeriod","SettlementDate","ControlArea"])
    #select excess balance price for positive balances and insufficient balance for negative balances
    Imbal_merged = Imbal_merged[((Imbal_merged["ImbalanceQuantity"] > 0) & (Imbal_merged["PriceCategory"] == "Excess balance") | (Imbal_merged["ImbalanceQuantity"] < 0) & (Imbal_merged["PriceCategory"] == "Insufficient balance"))]
    Imbal_merged["ImbalanceCost"] = Imbal_merged.ImbalanceQuantity * Imbal_merged.ImbalancePriceAmount

    create_half_hour_timestamps(Imbal_merged)

    return Imbal_merged

def calc_daily_costs(Imbal_merged):

    TotalCost = Imbal_merged["ImbalanceCost"].sum()
    TotalUnitrate = Imbal_merged["ImbalanceQuantity"].sum() / TotalCost

    print(f"Total daily imbalance cost: {TotalCost} ")
    print(f"Daily imbalance unit rate: {TotalUnitrate}")

def calc_highest_hourly_imbalance(Imbal_merged):

    # group by hour and sum volumes
    hourly_vol = Imbal_merged.groupby(pd.Grouper(key='start_time', freq='H'))['ImbalanceQuantity'].sum()
    #select absolute max hour
    max_hour = hourly_vol.abs().idxmax().hour
    print(f"The hour with the highest total imbalance cost is at {max_hour}:00")


if __name__ == "__main__":
    # Get yesterday's date
    prev_day = dt.datetime.now() - dt.timedelta(days=1)
    BMAPI = BMReports()
    Imbal_Prices = BMAPI.get_settlemtns_report("B1770","a4eamu641lgqfyv",prev_day.strftime("%Y-%m-%d"),"*","csv")
    Imbal_Vol = BMAPI.get_settlemtns_report("B1780", "a4eamu641lgqfyv", prev_day.strftime("%Y-%m-%d"), "*", "csv")
    Imbal_Prices = clean_Imbalance_Prices(Imbal_Prices)
    #Imbal_Prices = create_half_hour_timestamps(Imbal_Prices)
    Imbal_Vol = clean_Imbalance_Volumes(Imbal_Vol)

    Imbal_merged = merge_dfs(Imbal_Prices,Imbal_Vol)
    calc_daily_costs(Imbal_merged)
    calc_highest_hourly_imbalance(Imbal_merged)
   # Imbal_Prices = create_half_hour_timestamps(Imbal_Prices)




