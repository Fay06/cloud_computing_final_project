import requests
import json
import boto3
from datetime import datetime, date
from botocore.exceptions import ClientError


api_key = 'fa8e9199c2-b3d35b2bf0-rsignh'


def insert_data(data, db=None, table='CurrencyRate'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response

def rolling_update(data, db=None, table='LatestRates'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    for currency in data['results']:
        print("rolling update:", currency)
        currency_record = table.get_item(Key={'currency': currency})['Item']['rates']
        if datetime.strptime(data['update_time'][:10], "%Y-%m-%d") > datetime.strptime(currency_record['update_time'][:10], "%Y-%m-%d"):
            currency_record['highest'] = data['results'][currency]
            currency_record['lowest'] = data['results'][currency]
        currency_record['latest_rate'] = data['results'][currency]
        currency_record['highest'] = max(data['results'][currency], currency_record['highest'])
        currency_record['lowest'] = min(data['results'][currency], currency_record['lowest'])
        currency_record['update_time'] = data['update_time']
        res = update_rate({'currency': currency}, currency_record)
        print("rolling update:",res)
        

def update_rate(key, feature, db=None, table='LatestRates'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # change user balance
    response = table.update_item(
        Key=key,
        UpdateExpression="set #feature=:f",
        ExpressionAttributeValues={
            ':f': feature
        },
        ExpressionAttributeNames={
            "#feature": "rates"
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    return response




def lambda_handler(event, context):
    # TODO implement
    from_currency = 'USD'
    to_currency = 'CNY'
    url = "https://api.fastforex.io/fetch-one?from={}&to={}&api_key={}".format(from_currency, to_currency, api_key)
    url = "https://api.fastforex.io/fetch-multi?from=USD&to=EUR,GBP,CHF,JPY,AUD,CAD,CNY,HKD&api_key={}".format(api_key)
    headers = {"accept": "application/json"}
    response = json.loads(requests.get(url, headers=headers).text)
    print(response)
    # response: {"base":"USD","result":{"CNY":6.87022},"updated":"2023-04-02 23:55:16","ms":4}
    # updated time is in Greenwich Mean Time (GMT)
    response['update_time'] = response['updated']
    response.pop('ms',None)
    response.pop('updated', None)
    for k in response['results']:
        response['results'][k] = str(response['results'][k])
    print("modified_response: ", response)
    insert_data(response)
    rolling_update(response)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

