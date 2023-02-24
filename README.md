# SmartestEnergy Python Coding Test
The Imbalances Python package provides functionality to retrieve and analyze Imbalance Quantity and Imbalance prices from the BM Reports API for the previous day.

Installation:

To use the Imbalances package, you will need to clone the patrick-whitelaw/SmartestEnergy Github repository and run the Imbalances.py file.

	git clone https://github.com/patrick-whitelaw/SmartestEnergy.git
	cd SmartestEnergy
	python Imbalances.py

The required packages for running the Imbalances package are specified in the requirements.txt file, which can be installed using pip.

	pip install -r requirements.txt

Usage:

The Imbalances.py file retrieves the previous day's Imbalance Quantity and Imbalance prices report from the BM Reports API.
It then cleans and merges both reports, and then prints out the total daily imbalance cost, 
daily imbalance unit rate, and the hour with the maximum imbalance. 
Additionally, a graph of the day's imbalance price and volumes is provided.

Import the Imbalances module in your Python script:

	import Imbalances

Call the Get_previous_Day_Imbalances function with your API Key for BM Reports as a parameter:

	imbalance_data = Imbalances.Get_Previous_Day_Imbalances(<API_Key>)

This will print details about the previous days imbalance data and a provide a graph.
The imbalance_data variable will contain the imbalances dataframe returned by the function,
containing the merged pricing, quantity and cost information which you can then use for further processing.

Alternately the Imbalances file can be run directly like so

	imbalances.py <API_Key>

Future investigations into determining the pattern between the consistency/model of the imbalance unit price increase when the imbalance is in surplus compared to when there is a defeceit, 
as there is a clear difference between the two.
