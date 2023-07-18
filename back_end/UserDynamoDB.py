import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # email is the primary/paritition key
    # email is the userid
    user = {
        'email': 'sample001@columbia.edu',
        'password': 'cloud6998',
        'balance': {
            'usd': '100',
            'gbp': '200',
            'jpy': '1000',
            'cny': '500'
            }
        }
    user['balance']['usd'] = '1000'
    new_balance = user['balance']
    new_balance['cny'] = '300'
    # insert_data(user)
    # lookup_data({'email': 'sample001@columbia.edu'})
    update_item({'email': 'sample001@columbia.edu'}, user['balance'])

    return


def insert_data(data, db=None, table='User'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response


def lookup_data(key, db=None, table='User'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response['Item'])
        return response['Item']


def update_item(key, feature, db=None, table='User'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    
    response = table.update_item(
        Key=key,
        UpdateExpression="set #feature=:f",
        ExpressionAttributeValues={
            ':f': feature
        },
        ExpressionAttributeNames={
            "#feature": "balance"
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    return response


