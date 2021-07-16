import json


def lambda_handler(event, context):

    success='SUCCEEDED'
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! [Get Status]'),
        'status': json.dumps(success).encode('utf8'),
        'guid': json.dumps("guid")

    }
