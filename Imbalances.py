import datetime as dt
import pandas as pd
import Imbal_Analysis
import Imbal_Processing
import sys

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 400)

def Get_previous_Day_Imbalances(API_Key):
    """
    Retrieve the Imbalance settlements for previous day from BM Reports.
    Calculate the total imabalnce cost and unit rate as well as the maximum imbalance hour.
    Provide a graph of balance cost and imbalance volume.

    #Parameters:
    API_Key (str): The string of the API key given to acces BM Reports
    """
    try:
        # Get yesterday's date
        prev_day = dt.datetime.now() - dt.timedelta(days=1)
        BMAPI = Imbal_Processing.BMReports()
        #Get data from BM Repots
        Imbal_Prices = BMAPI.get_settlements_report("B1770", API_Key, prev_day.strftime("%Y-%m-%d"), "*", "csv")
        Imbal_Vol = BMAPI.get_settlements_report("B1780", API_Key, prev_day.strftime("%Y-%m-%d"), "*", "csv")
        #Clean data and merge data
        Imbal_Prices = Imbal_Processing.clean_Imbalance_Prices(Imbal_Prices)
        Imbal_Vol = Imbal_Processing.clean_Imbalance_Volumes(Imbal_Vol)
        Imbal_merged = Imbal_Processing.merge_Imbal_dfs(Imbal_Prices, Imbal_Vol)
        #Present Analysis
        Imbal_Analysis.calc_daily_costs(Imbal_merged)
        Imbal_Analysis.calc_highest_hourly_imbalance(Imbal_merged)
        Imbal_Analysis.create_imbal_graph(Imbal_merged)
        return Imbal_merged
    except Exception as e:
        print(f"Error occurred while gathering imbalances: {e}")


if __name__ == "__main__":
    #Get_previous_Day_Imbalances(API_Key="a4eamu641lgqfyv")
    Get_previous_Day_Imbalances(API_Key=sys.argv[1])



