import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone, timedelta


def update_item(key, feature, db=None, table='User'):
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
            "#feature": "balance"
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    return response



def get_transaction_rate(buy_currency, rates, sell_currency):
    rate = float(rates['Items'][0]['results'][buy_currency])
    if (sell_currency != 'USD'):
        rate = rate / float(rates['Items'][0]['results'][sell_currency])
    return rate


def update_user_balance(buy_currency, buy_currency_amount, sell_currency, sell_currency_amount, user, user_id):
    new_balance = user['Item']['balance']
    print("balance before update", new_balance)
    new_balance[buy_currency] = buy_currency_amount
    new_balance[sell_currency] = sell_currency_amount
    new_balance = {k: str(v) if isinstance(v, float) else v for k, v in new_balance.items()}
    print("balance after update", new_balance)
    res = update_item({
        'email': user_id}, new_balance)
    print(res)
    return res


def calculate_new_balance(amount, buy_currency, rate, sell_currency, user):
    sell_currency_amount = float(user['Item']['balance'][sell_currency])
    print(buy_currency)
    buy_currency_amount = float(user['Item']['balance'][buy_currency])
    sell_currency_amount -= amount / rate
    buy_currency_amount += amount
    return buy_currency_amount, sell_currency_amount


def get_user(user_id):
    dynamodb = boto3.resource('dynamodb')
    user_table = dynamodb.Table('User')
    response = user_table.get_item(Key={
        'email': user_id})
    print(response)
    return response


def get_rates():
    dynamodb = boto3.resource('dynamodb')
    rate_table = dynamodb.Table('CurrencyRate')
    currentDateAndTime = datetime.now() - timedelta(minutes=1)
    currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M")
    print(currentTime)
    response = rate_table.scan(
        FilterExpression='begins_with(update_time, :date)',
        ExpressionAttributeValues={
            ':date': currentTime}
    )
    if len(response["Items"]) == 0:
        currentDateAndTime = datetime.now() - timedelta(minutes=2)
        currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M")
        print(currentTime)
        response = rate_table.scan(
            FilterExpression='begins_with(update_time, :date)',
            ExpressionAttributeValues={
                ':date': currentTime}
            )
    print(response)
    return response


def lambda_handler(event, context):
    # event = {'resource': '/buy/{userID}/{sellCurrency}/{buyCurrency}/{amount}', 'path': '/buy/123/usd/jpy/1000', 'httpMethod': 'PUT', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Host': 'jks1yxo910.execute-api.us-east-1.amazonaws.com', 'Postman-Token': '283d09a2-8058-4e8e-8b64-917c78cf7600', 'User-Agent': 'PostmanRuntime/7.31.3', 'X-Amzn-Trace-Id': 'Root=1-642c9014-7d3c6d111344bd5a38cc9d14', 'X-Forwarded-For': '128.59.178.118', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Host': ['jks1yxo910.execute-api.us-east-1.amazonaws.com'], 'Postman-Token': ['283d09a2-8058-4e8e-8b64-917c78cf7600'], 'User-Agent': ['PostmanRuntime/7.31.3'], 'X-Amzn-Trace-Id': ['Root=1-642c9014-7d3c6d111344bd5a38cc9d14'], 'X-Forwarded-For': ['128.59.178.118'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'amount': '1000', 'sellCurrency': 'usd', 'buyCurrency': 'jpy', 'userID': '123'}, 'stageVariables': None, 'requestContext': {'resourceId': 'cj3ypi', 'resourcePath': '/buy/{userID}/{sellCurrency}/{buyCurrency}/{amount}', 'httpMethod': 'PUT', 'extendedRequestId': 'C3tzPEUqIAMFreA=', 'requestTime': '04/Apr/2023:21:01:08 +0000', 'path': '/test-user/buy/123/usd/jpy/1000', 'accountId': '811219959239', 'protocol': 'HTTP/1.1', 'stage': 'test-user', 'domainPrefix': 'jks1yxo910', 'requestTimeEpoch': 1680642068420, 'requestId': 'f0efb2d2-0c53-41e9-968d-b792e0c3ba26', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '128.59.178.118', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.31.3', 'user': None}, 'domainName': 'jks1yxo910.execute-api.us-east-1.amazonaws.com', 'apiId': 'jks1yxo910'}, 'body': None, 'isBase64Encoded': False}
    print(event)
    user_id = event['pathParameters']['userID']
    sell_currency = event['pathParameters']['sellCurrency'].upper()
    if sell_currency not in ['USD','EUR','GBP','JPY','CNY','CHF','AUD','CAD','HKD']:
        return {
            'statusCode': 403,
            'body': "Currency {} is not supported.".format(sell_currency)
        }
    buy_currency = event['pathParameters']['buyCurrency'].upper()
    if buy_currency not in ['USD','EUR','GBP','JPY','CNY','CHF','AUD','CAD','HKD']:
        return {
            'statusCode': 403,
            'body': "Currency {} is not supported.".format(buy_currency)
        }
    amount = float(event['pathParameters']['amount'])
    if amount < 0:
        return {
            'statusCode': 403,
            'body': "Transaction amount must larger than 0."
        }

    rates = get_rates()
    rate = get_transaction_rate(buy_currency, rates, sell_currency)

    user = get_user(user_id)
    buy_currency_amount, sell_currency_amount = calculate_new_balance(amount, buy_currency, rate, sell_currency, user)
    print(sell_currency_amount)
    print(buy_currency_amount)

    if sell_currency_amount < 0:
        return {
            'statusCode': 403,
            'body': "Insufficient {} asset, at leaset {} {} needed.".format(sell_currency, float(amount) / rate,
                                                                            sell_currency)
        }

    res = update_user_balance(buy_currency, buy_currency_amount, sell_currency, sell_currency_amount, user, user_id)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        'body': json.dumps(res)
    }
