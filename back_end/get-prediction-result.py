import json
import boto3
import csv
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # TODO implement
    currency="HKD"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('forecast-data-6998')
    prediction_files=["predicted_prices.csv"]
    # for object in bucket.objects.all():
    #     if object.key.startswith("part-00000"):
    #         prediction_files.append(object.key)
        
    # print(prediction_files)
    s3 = boto3.client('s3')
    all_predictions=[]
    for file in prediction_files:
        all_predictions += list(csv.reader(s3.get_object(Bucket='forecast-data-6998', Key=file)['Body'].read().decode('utf-8').split('\n')))[1:-1]
    print(all_predictions)
    predictions=[]
    for money, time, p5 in all_predictions:
        money = money.upper()
        time = time[:10]
        if money == currency and datetime.strptime(time, "%Y-%m-%d")>datetime.now():
            predictions.append([currency, time, p5])
    print(predictions)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
