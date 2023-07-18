import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # TODO implement
    print(event)
    table='User'
    db = boto3.resource('dynamodb')
    table = db.Table(table)
    print(event['pathParameters'])
    key = event['pathParameters']
    for k in key:
        if isinstance(key[k], str) and "%40" in key[k]:
            key[k] = key[k].replace("%40", "@")
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response['Item'])
        res = response['Item']
        api_gateway_response = {
            'statusCode': 200,
            'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    },
            'body': json.dumps(res)
        }
        
        return api_gateway_response
