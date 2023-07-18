import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import requests
import json
import csv
import boto3
import os
api_key="fa8e9199c2-b3d35b2bf0-rsignh"

def lambda_handler(event, context):
    target_currencies = ['EUR','GBP','CHF','JPY','AUD','CAD','CNY','HKD']
    current_date = (datetime.now()-timedelta(days=0)).strftime("%Y-%m-%d")
    past_date = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")
    all_hist={}
    for currency in target_currencies:
        url = "https://api.fastforex.io/time-series?from=USD&to={}&interval=P1D&start={}&end={}&api_key={}".format(currency,past_date,current_date,api_key)
        hist = json.loads(requests.get(url).text)['results']
        all_hist[currency]=hist[currency]

    rows=[["currency", "timestamp", "price"]]
    for currency, hist in all_hist.items():
        for date, price in hist.items():
            rows.append([currency, date, price])

    filename = "currency_records.csv"
    with open('/tmp/'+filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the data rows
        csvwriter.writerows(rows)
    # Load the data
    data = pd.read_csv('/tmp/'+filename, index_col='timestamp', parse_dates=True)

    # Get the unique currency types in the input data
    currencies = data['currency'].unique()

    # Initialize an empty dataframe to store the predicted prices
    predicted_data = pd.DataFrame(columns=['Currency', 'Date', 'Price'])

    # Loop over each currency type and generate predictions
    for currency in currencies:
        # Extract the data for the current currency
        currency_data = data.loc[data['currency'] == currency]['price']

        # Fit an ARIMA model
        model = ARIMA(currency_data, order=(2, 1, 2))
        model_fit = model.fit()

        predicted_days=int(os.getenv('PREDICTED_DAYS'))
        # Make predictions for the next x days
        predictions = model_fit.forecast(steps=predicted_days)

        today = datetime.now().date()
        dates = [str(today + timedelta(days=i)) for i in range(1, predicted_days+1)]
        currency_predictions = pd.DataFrame({
                                                'Currency': [currency] * predicted_days,
                                                'Date': dates,
                                                'Price': predictions})
        predicted_data = pd.concat([predicted_data, currency_predictions],axis=0)

    # Save the predicted data to a CSV file
    predicted_data.to_csv('/tmp/predicted_prices.csv', index=False)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('forecast-data-6998')

    bucket.upload_file('/tmp/predicted_prices.csv', 'predicted_prices.csv')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

if __name__ == '__main__':
    lambda_handler(None, None)
