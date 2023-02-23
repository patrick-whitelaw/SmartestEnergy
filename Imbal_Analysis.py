import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md

def calc_daily_costs(Imbal_merged):
    """
    Calculates and prints the total daily imbalance cost and daily imbalance unit rate.

    #Parameters:
        Imbal_merged: DataFrame containing the merged imbalance volumes and prices data.

    # Raises:
        TypeError: If input Imbal_merged is not a pandas DataFrame.
        ValueError: If unable to generate calculated value for imbalances.
    """

    if not isinstance(Imbal_merged, pd.DataFrame):
        raise TypeError("Cost caluclation input must be a pandas DataFrame.")

    try:
        TotalCost = Imbal_merged["ImbalanceCost"].sum()
        TotalUnitrate = Imbal_merged["ImbalancePriceAmount"].mean()
        imbal_date = pd.to_datetime(Imbal_merged["start_time"].iloc[0]).strftime("%Y-%m-%d")

        print(f"Total daily imbalance cost for {imbal_date}: {round(TotalCost,2)} GBP.")
        print(f"Daily imbalance unit rate for {imbal_date}: {round(TotalUnitrate,2)} GBP/MWh.")

    except:
        raise ValueError("Unable to generate calculated value for imbalances")

def calc_highest_hourly_imbalance(Imbal_merged):
    """
    Calculates and prints the highest absolute imbalanced hour.

    #Parameters:
        Imbal_merged: DataFrame containing the merged imbalance volumes and prices data.

    # Raises:
        TypeError: If input Imbal_merged is not a pandas DataFrame.
        ValueError: If unable to generate maximum imbalance value for imbalances.
    """
    if not isinstance(Imbal_merged, pd.DataFrame):
        raise TypeError("Maximum imbalance input must be a pandas DataFrame.")
    try:
        # group by hour and sum volumes
        hourly_vol = Imbal_merged.groupby(pd.Grouper(key='start_time', freq='H'))['ImbalanceQuantity'].sum()
        #select absolute max hour
        max_hour = hourly_vol.abs().idxmax().hour
        max_imbalance = hourly_vol[max_hour]
        imbal_date = pd.to_datetime(Imbal_merged["start_time"].iloc[0]).strftime("%Y-%m-%d")
        if max_imbalance > 0:
            state = "surplus"
        else:
            state = "deficit"
        print(f"The hour with the highest total imbalance for {imbal_date} is at {max_hour:02d}:00 with a imbalance of {max_imbalance} MWh {state}.")
    except:
        raise ValueError("Unable to calculate maximum imbalances")


def create_imbal_graph(Imbal_merged):
    """
    Presents a graph showing imbalance price and imbalance surplus/defecit volumes.

    #Parameters:
        Imbal_merged: DataFrame containing the merged imbalance volumes and prices data.
    # Raises:
        TypeError: If input Imbal_merged is not a pandas DataFrame.
        KeyError: If unable to create a graph to display imbalances.
    """
    if not isinstance(Imbal_merged, pd.DataFrame):
        raise TypeError("Graph input must be a pandas DataFrame.")
    try:
        Imbal_merged['start_time'] = pd.to_datetime(Imbal_merged['start_time'])

        # Sort by start_time in descending order
        Imbal_merged.sort_values(by='start_time', ascending=False, inplace=True)

        # Create a figure with two subplots, sharing the x-axis
        fig, ax1 = plt.subplots()

        # Set the title
        fig.suptitle(Imbal_merged['start_time'].dt.date.unique()[0].strftime('%Y-%m-%d'))

        # Set the x-axis
        ax1.set_xlabel('Time of day')
        xlocator = md.HourLocator(interval=2)
        xminorlocator = md.MinuteLocator(byminute=range(0, 60, 30))
        xformatter = md.DateFormatter('%H:%M')
        ax1.xaxis.set_major_locator(xlocator)
        ax1.xaxis.set_major_formatter(xformatter)
        ax1.xaxis.set_minor_locator(xminorlocator)
        ax1.set_xlim(left=Imbal_merged['start_time'].min(), right=Imbal_merged['start_time'].max())

        # Set the y-axis for the prices line chart
        ax1.set_ylabel('ImbalancePriceAmount', color='blue')
        ax1.tick_params('y', colors='blue')

        # Plot the price line
        ax1.plot(Imbal_merged['start_time'], Imbal_merged['ImbalancePriceAmount'], color='blue', zorder=2)

        # Set the y-axis for the quantity bar chart
        ax2 = ax1.twinx()
        ax2.set_ylabel('ImbalanceQuantity', color='red')
        ax2.tick_params('y', colors='red')

        # Plot the quantity bars
        ax2.bar(Imbal_merged['start_time'], Imbal_merged['ImbalanceQuantity'], width=0.02, color='red', zorder=1)

        # Show the plot
        fig.autofmt_xdate()
        plt.show()
    except:
        raise KeyError("Graph unable to be created")