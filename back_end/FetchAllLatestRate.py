import json
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone, timedelta





def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('LatestRates')

    response = table.scan()

    items = response['Items']
    while response.get('LastEvaluatedKey'):
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    response={"rates":{}, "update_time": items[0]['rates']['update_time'], 'base':'USD'}
    for item in items:
        currency = item['currency']
        if item['currency'] not in response['rates']:
            response['rates'][currency] = {}
        response['rates'][currency]['rate']=item['rates']['latest_rate']
        response['rates'][currency]['highest']=item['rates']['highest']
        response['rates'][currency]['lowest'] = item['rates']['lowest']


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        'body': json.dumps(response)
    }
