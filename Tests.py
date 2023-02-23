import Imbalances as imb
import Imbal_Analysis as imb_Ana
import Imbal_Processing as imb_pro
import pandas as pd
import datetime

def test_BMReports():
    # Valid inputs
    bm = imb_pro.BMReports()
    report = bm.get_settlements_report('B1770', 'a4eamu641lgqfyv', '20220201', 1, 'csv')
    assert isinstance(report, pd.DataFrame)

    # Invalid inputs
    try:
        bm.get_settlements_report('invalid_report', 'test_key', '20220101', 1, 'csv')
    except ValueError as e:
        assert str(e) == 'Invalid report name'

def test_clean_Imbalance_Prices():
    # Create some test data
    imbalance_prices = pd.DataFrame({
        "DocumentID": ["ELX-EMFIP-IMBP-32110862", "ELX-EMFIP-IMBP-32110862"],
        "DocumentRevNum": [1.0, 1.0],
        "ActiveFlag": ["Y", "Y"],
        "ProcessType": ["Realised", "Realised"],
        "DocumentType": ["Imbalance prices", "Imbalance prices"],
        "Resolution": ["PT30M", "PT30M"],
        "CurveType": ["Sequential fixed size block", "Sequential fixed size block"],
        "PriceCategory": ["Excess balance", "Insufficient balance"],
        "ImbalancePriceAmount": [93.0, 93.0],
        "SettlementPeriod": [48.0, 48.0],
        "SettlementDate": ["2023-02-22", "2023-02-22"],
        "ControlArea": ["10YGB----------A", "10YGB----------A"],
        "BusinessType": ["Balance energy deviation", "Balance energy deviation"],
        "TimeSeriesID": ["ELX-EMFIP-IMBP-TS-2", "ELX-EMFIP-IMBP-TS-1"],
        "DocumentStatus": ["Final", "Final"]
    })

    # Call the clean_Imbalance_Prices function with the test data
    cleaned_data = imb_pro.clean_Imbalance_Prices(imbalance_prices)

    # Define the expected output
    expected_output = pd.DataFrame({
        "SettlementDate": ["2023-02-22", "2023-02-22"],
        "SettlementPeriod": [48.0, 48.0],
        "ControlArea": ["10YGB----------A", "10YGB----------A"],
        "ImbalancePriceAmount": [93.0, 93.0],
        "PriceCategory": ["Excess balance", "Insufficient balance"]
    })

    # Check that the output matches the expected output
    pd.testing.assert_frame_equal(cleaned_data, expected_output)


def test_clean_Imbalance_Volumes():
    # Create some test data
    imbalance_volumes = pd.DataFrame({
        "Document Status": ["Final", "Draft", "Final", "Final"],
        "Active Flag": ["Y", "Y", "N", "Y"],
        "Settlement Date": ["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"],
        "Settlement Period": [1, 2, 1, 2],
        "Control Area": ["CA1", "CA1", "CA1", "CA1"],
        "Imbalance Quantity (MAW)": [100, 200, 300, 400]
    })

    # Call the clean_Imbalance_Volumes function with the test data
    cleaned_data = imb_pro.clean_Imbalance_Volumes(imbalance_volumes)

    # Define the expected output
    expected_output = pd.DataFrame({
        "SettlementDate": ["2022-01-01", "2022-01-02"],
        "SettlementPeriod": [1, 2],
        "ControlArea": ["CA1", "CA1"],
        "ImbalanceQuantity": [100, 400]
    })

    # Check that the output matches the expected output
    pd.testing.assert_frame_equal(cleaned_data, expected_output)

def test_create_half_hour_timestamps():
    # Create some test data
    imbalance_data = pd.DataFrame({
        "SettlementDate": ["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"],
        "SettlementPeriod": [1, 2, 1, 2],
        "ImbalanceQuantity": [100, 200, 300, 400]
    })

    # Call the create_half_hour_timestamps function with the test data
    data_with_timestamps = imb_pro.create_half_hour_timestamps(imbalance_data)

    # Define the expected output
    expected_output = pd.DataFrame({
        "SettlementDate": ["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"],
        "SettlementPeriod": [1, 2, 1, 2],
        "ImbalanceQuantity": [100, 200, 300, 400],
        "start_time": ["2022-01-01 00:00:00", "2022-01-01 00:30:00", "2022-01-02 00:00:00", "2022-01-02 00:30:00"],
        "end_time": ["2022-01-01 00:30:00", "2022-01-01 01:00:00", "2022-01-02 00:30:00", "2022-01-02 01:00:00"]
    })

    # Check that the output matches the expected output
    pd.testing.assert_frame_equal(data_with_timestamps, expected_output)

def test_merge_dfs():
    prices_df = pd.DataFrame({
        'SettlementPeriod': [1, 2, 3],
        'SettlementDate': ['2022-01-01', '2022-01-01', '2022-01-02'],
        'ControlArea': ['UK1', 'UK1', 'UK1'],
        'PriceCategory': ['Excess balance', 'Excess balance', 'Insufficient balance'],
        'ImbalancePriceAmount': [10, 20, 5],
    })
    volumes_df = pd.DataFrame({
        'SettlementPeriod': [1, 2, 3],
        'SettlementDate': ['2022-01-01', '2022-01-01', '2022-01-02'],
        'ControlArea': ['UK1', 'UK1', 'UK1'],
        'ImbalanceQuantity': [100, -50, 80],
    })
    expected_df = pd.DataFrame({
        'SettlementPeriod': [1, 3],
        'SettlementDate': ['2022-01-01', '2022-01-02'],
        'ControlArea': ['CA1', 'CA1'],
        'PriceCategory': ['Excess balance', 'Insufficient balance'],
        'ImbalancePriceAmount': [10, 5],
        'ImbalanceQuantity': [100, 80],
        'ImbalanceCost': [1000, -400],
        'start_time': pd.to_datetime(['2022-01-01 00:00:00', '2022-01-02 00:00:00']),
        'end_time': pd.to_datetime(['2022-01-01 00:30:00', '2022-01-02 00:30:00'])
    })

    merged_df = imb_pro.merge_dfs(prices_df, volumes_df)
    pd.testing.assert_frame_equal(merged_df, expected_df)

def test_calc_highest_hourly_imbalance():
    # Define input DataFrame
    Imbal_merged = pd.DataFrame({
        "SettlementDate": ["2023-02-22", "2023-02-22", "2023-02-22", "2023-02-22", "2023-02-22", "2023-02-22"],
        "SettlementPeriod": [48.0, 47.0, 46.0, 48.0, 47.0, 46.0],
        "ControlArea": ["10YGB----------A", "10YGB----------A", "10YGB----------A", "10YGB----------A", "10YGB----------A", "10YGB----------A"],
        "ImbalancePriceAmount": [93.0000, 100.0000, 92.6300, 93.0000, 100.0000, 92.6300],
        "PriceCategory": ["Insufficient balance", "Insufficient balance", "Insufficient balance", "Excess balance", "Excess balance", "Excess balance"],
        "ImbalanceQuantity": [-117.3014, -10.7602, -2.7719, 66.3014, 10.7602, 2.7719],
        "ImbalanceCost": [-10909.0302, -1076.02, -256.761097, 6161.47, 1154.2, 276.467903],
        "start_time": [datetime(2023, 2, 22, 21, 30), datetime(2023, 2, 22, 21, 0), datetime(2023, 2, 22, 22, 00), datetime(2023, 2, 22, 22, 30), datetime(2023, 2, 22, 23, 0), datetime(2023, 2, 22, 23, 30)],
        "end_time": [datetime(2023, 2, 22, 22, 0), datetime(2023, 2, 22, 21, 30), datetime(2023, 2, 22, 20, 30), datetime(2023, 2, 23, 23, 0), datetime(2023, 2, 22, 23, 30), datetime(2023, 2, 23, 0, 0)]
    })

    # Define expected output string
    expected_output = "The hour with the highest total imbalance for 2023-02-22 is at 21:00 with a imbalance of -128.0616 MWh deficit."

    # Call the function to be tested
    output = imb_Ana.calc_highest_hourly_imbalance(Imbal_merged)

    # Check the expected output against the actual output
    assert output == expected_output