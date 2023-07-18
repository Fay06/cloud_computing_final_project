import requests
import json
from datetime import datetime, timedelta
import csv
import boto3
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
    with open("/tmp/"+filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the data rows
        csvwriter.writerows(rows)
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('forecast-data-6998')

    bucket.upload_file("/tmp/"+filename, filename)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

