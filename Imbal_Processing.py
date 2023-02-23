import requests
from io import StringIO
import pandas as pd


class BMReports:
    """
    A class for interacting with the BMReports API.
    """
    def __init__(self):
        self.reportless_uri = "https://api.bmreports.com/BMRS/%s/v1"

    def get_settlements_report(self, report_name, API_Key, Settlement_Date, period, ServiceType):
        """
        Get settlements report for the specified parameters.

        #Parameters:
            report_name (str): The name of the report to fetch.
            API_Key (str): The API key to use for the request.
            Settlement_Date (str): The settlement date for the report in YYYYMMDD format.
            period (int): The period of the report to fetch.
            ServiceType (str): The service type to fetch.

        #Returns:
            pandas.DataFrame: A pandas DataFrame containing the report data.

        #Raises:
            ValueError: If input returned response is empty.
        """

        base_uri = self.reportless_uri % report_name
        params = {
            'APIKey': API_Key,
            'SettlementDate': Settlement_Date,
            'Period': period,
            'ServiceType': ServiceType,
        }
        try:
            response = requests.get(base_uri, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise e
        df = pd.read_csv(StringIO(response.content.decode('utf-8')), skiprows=4)
        # Check for error message in response
        if len(df) > 0 and 'Message' in df.columns:
            raise ValueError(df['Message'].iloc[0])
        return df

def clean_Imbalance_Prices(Imbal_Prices):
    """
      Clean and standardize the imbalance pricing data.

      #Parameters:
        Imbal_Prices (pd.DataFrame): The original imbalance prices data.

      #Returns:
        pd.DataFrame: The cleaned imbalance pricing data.
      """
    try:
        # Remove non essential data
        Imbal_Prices = Imbal_Prices[(Imbal_Prices["DocumentStatus"] == "Final") & (Imbal_Prices["ActiveFlag"] == "Y")]
        Imbal_Prices = Imbal_Prices[["SettlementDate","SettlementPeriod","ControlArea","ImbalancePriceAmount","PriceCategory"]]

        return Imbal_Prices

    except Exception as e:
        print(f"Error cleaning imbalance volumes data: {e}")


def clean_Imbalance_Volumes(Imbal_Vol):
    """
    Clean and standardize the imbalance volumes data.

    #Parameters
    Imbal_Vol (pd.DataFrame): The original imbalance volumes data.

    #Returns:
    pd.DataFrame: The cleaned imbalance volumes data.
    """
    try:
        # Remove non essential data
        Imbal_Vol = Imbal_Vol[(Imbal_Vol["Document Status"] == "Final") & (Imbal_Vol["Active Flag"] == "Y")]
        Imbal_Vol = Imbal_Vol[["Settlement Date","Settlement Period","Control Area","Imbalance Quantity (MAW)"]]

        #Rename for standardisation with prices
        Imbal_Vol = Imbal_Vol.rename(columns={"Settlement Date": "SettlementDate", "Settlement Period": "SettlementPeriod", "Control Area": "ControlArea", "Imbalance Quantity (MAW)": "ImbalanceQuantity"})

        return Imbal_Vol

    except Exception as e:
        print(f"Error cleaning imbalance volumes data: {e}")


def create_half_hour_timestamps(Imbal_df):
    """
    Create start and end timestamps for half-hour intervals.

    #Parameters
        Imbal_df (pd.DataFrame): The imbalance data with SettlementDate and SettlementPeriod columns.

    #Returns:
        pd.DataFrame: The imbalance data with start_time and end_time columns.
    #Raises:
        ValueError: If input dataframes are undable to create half hourly timestamps.
    """
    try:
        # convert date column to datetime
        Imbal_df['SettlementDate'] = pd.to_datetime(Imbal_df['SettlementDate'])

        # create a timedelta column for half-hour intervals
        half_hour_delta = pd.to_timedelta((Imbal_df['SettlementPeriod'] - 1) * 30, unit='minutes')

        # create start and end time columns
        Imbal_df['start_time'] = Imbal_df['SettlementDate'] + half_hour_delta
        Imbal_df['end_time'] = Imbal_df['SettlementDate'] + half_hour_delta + pd.Timedelta(minutes=30)

        return Imbal_df

    except:
        raise ValueError("Cannot create half hourly timestamps from dataframe.")


def merge_Imbal_dfs(Imbal_Prices,Imbal_Vol):
    """
    Merge imbalance prices and volumes dataframes.

    #Parameters
        Imbal_Prices (pd.DataFrame): Dataframe containing imbalance prices.
        Imbal_Vol (pd.DataFrame): Dataframe containing imbalance volumes.

    #Returns:
        pd.DataFrame: Dataframe containing merged imbalance prices and volumes.

    #Raises:
        ValueError: If input dataframes are empty.
        KeyError: If required columns are missing in input dataframes.

    """
    # Check input dataframes are not empty
    if Imbal_Prices.empty or Imbal_Vol.empty:
        raise ValueError("Input dataframes for merging cannot be empty.")
    #merge on rename columns
    try:
        Imbal_merged = Imbal_Prices.merge(Imbal_Vol, how="inner", on=["SettlementPeriod","SettlementDate","ControlArea"])
        #select excess balance price for positive balances and insufficient balance for negative balances
        Imbal_merged = Imbal_merged[((Imbal_merged["ImbalanceQuantity"] > 0) & (Imbal_merged["PriceCategory"] == "Excess balance") | (Imbal_merged["ImbalanceQuantity"] < 0) & (Imbal_merged["PriceCategory"] == "Insufficient balance"))]
        Imbal_merged["ImbalanceCost"] = Imbal_merged.ImbalanceQuantity * Imbal_merged.ImbalancePriceAmount
    except:
        raise KeyError("Columns do not match those required for merging")
    create_half_hour_timestamps(Imbal_merged)

    return Imbal_merged
