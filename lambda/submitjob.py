import json


def lambda_handler(event, context):

    return {
        'statusCode': 200,
        'body':'Hello from Lambda! [Get Status]',
        'waitSeconds': 10,
        'guid': json.dumps('guid')

    }
