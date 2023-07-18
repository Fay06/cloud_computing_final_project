import json
import boto3
import time

def lambda_handler(event, context):
    # Create an SES client
    client = boto3.client('ses')
    
    table='LatestRates'
    db = boto3.resource('dynamodb')
    table = db.Table(table)
    response = table.scan()
    items = response['Items']

    # Keep scanning the table until all items have been retrieved
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    # Print all items
    # print(items)
    
    result = [{'currency': currency_info['currency'], 'latest_rate': currency_info['rates']['latest_rate']} for currency_info in items]
    
    output = "Here's your daily currency update: \n"
    for currency_info in result:
        output += f"{currency_info['currency']} {currency_info['latest_rate']}\n "
    output = output[:-2] # remove trailing comma and space
    output += "."
    
    table='User'
    db = boto3.resource('dynamodb')
    table = db.Table(table)
    response = table.scan()
    items = response['Items']

    # Keep scanning the table until all items have been retrieved
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    # Print all items
    print("User:", items)
    
    emails=[user['email'] for user in items]
    
    print('emails: ', emails)
    
    for email in emails:
        # Set up the email message
        message = {
            'Source': 'yl5099@columbia.edu',
            'Destination': {
                'ToAddresses': [
                    email
                ]
            },
            'Message': {
                'Subject': {
                    'Data': 'Today\'s currency update'
                },
                'Body': {
                    'Text': {
                        'Data': output
                    }
                },
            }
        }
        
        # Send the email
        try:
            response = client.send_email(
                Destination=message['Destination'],
                Message=message['Message'],
                Source=message['Source']
            )
        except:
            print('Failed to send ', email)
        
        # Print the response
        print(response)
        time.sleep(1)
    return
