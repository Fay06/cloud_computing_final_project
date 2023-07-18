import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    print(event)
    email = event['pathParameters']['email']
    password = event['pathParameters']['password']
    user = {
        'email': email,
        'password': password,
        'balance': {
            'USD': '20000',
            'EUR': '0',
            'GBP': '0',
            'JPY': '0',
            'CNY': '0',
            'CHF': '0',
            'AUD': '0',
            'CAD': '0',
            'HKD': '0'
            }
        }
    db = boto3.resource('dynamodb')
    table = db.Table('User')
    # overwrite if the same index is provided
    response = table.put_item(Item=user)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
