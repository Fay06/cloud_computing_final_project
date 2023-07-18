import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('USD-CNY-1min')
    
    # update_time is in format: '2023-04-03 01:07:53'
    # use prefix to retrieve specific set of data
    # for example, use lookup_key = '2023-04-03' to get every forex data in 2023-04-03
    # use '2023-04-03 01:0' to get every forex data whithin 10 min from 01:00 to 01:10 
    
    msg_from_user = event["queryStringParameters"]["start_time"]
    # lookup_key = '2023-04-03 01:0'
    
    lookup_key = msg_from_user
    
    response = table.scan(
        FilterExpression='begins_with(update_time, :date)',
        ExpressionAttributeValues={':date': lookup_key}
    )
    
    items = response['Items']
    print(items)

    resp = {
        'statusCode': 200,
        'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': items})
    }
    
    return resp
