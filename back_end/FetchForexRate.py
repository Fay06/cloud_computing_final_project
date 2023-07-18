import requests
import json
import boto3
from botocore.exceptions import ClientError

from_currency = 'USD'
to_currency = 'CNY'


def insert_data(data_list, db=None, table='USD-CNY-1min'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    for data in data_list:
        response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response


def lambda_handler(event, context):
    # TODO implement
    url = "https://api.fastforex.io/fetch-one?from={}&to={}&api_key={}".format(from_currency,to_currency,api_key)
    headers = {"accept": "application/json"}
    response =  json.loads(requests.get(url, headers=headers).text)
    # response: {"base":"USD","result":{"CNY":6.87022},"updated":"2023-04-02 23:55:16","ms":4}
    # updated time is in Greenwich Mean Time (GMT)
    update_time = response['updated']
    forex_rate = response['result'][to_currency]
    print(update_time + ': ' +  str(forex_rate))
    
    
    forex_data = [{
            'update_time':str(update_time),
            'forex_rate':str(forex_rate)
        }]
    
    insert_data(forex_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
