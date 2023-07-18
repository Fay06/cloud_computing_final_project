import json
import boto3
from boto3.dynamodb.conditions import Key
import csv
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # TODO implement
    currency = event['pathParameters']['currency'].upper()
    if currency not in ['USD','EUR','GBP','JPY','CNY','CHF','AUD','CAD','HKD']:
        return {
            'statusCode': 403,
            'body': "Currency {} is not supported.".format(currency)
        }
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CurrencyRate')
    
    # update_time is in format: '2023-04-03 01:07:53'
    # use prefix to retrieve specific set of data
    # for example, use lookup_key = '2023-04-03' to get every forex data in 2023-04-03
    # use '2023-04-03 01:0' to get every forex data whithin 10 min from 01:00 to 01:10 
    
    msg_from_user = event["queryStringParameters"]["start_time"]
    # lookup_key = '2023-04-03 01:0'
    
    lookup_key = msg_from_user
    
    response = table.scan(
        FilterExpression='begins_with(update_time, :date)',
        ExpressionAttributeValues={
            ':date': lookup_key}
    )
    
    items = response['Items']
    print(items)
    res = []
    for rate in items:
        res.append({
            'forex_rate': rate['results'][currency],
            'update_time': rate['update_time']
        })
        
    prediction_files=["predicted_prices.csv"]
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
    resp = {
        'statusCode': 200,
        'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': res, 'predictions': predictions})
    }
    
    return resp
