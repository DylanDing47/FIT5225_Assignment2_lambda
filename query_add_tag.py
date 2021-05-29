import json

import boto3


def lambda_handler(event, context):
    event = json.loads(event['body'])
    operation = event['operation']
    if operation == 'add_tag':
        user_id = event['user_id']
        image_url = event['image_url']
        tags = event['tags']
        response_body = add_tag(user_id, image_url, tags)
    elif operation == 'add':
        response_body = insert_item()

    response = {
        "statusCode": 200,
        "headers": {
            "query_operation": "success"
        },
        "body": json.dumps(response_body),
        "isBase64Encoded": False
    }
    return response


def add_tag(user_id, image_url, tags):
    tags = list(set(tags))
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('assignment_image')
    try:
        item = table.get_item(Key={'user_id': user_id, 'image_url': image_url})
    except Exception:
        print(Exception)
    current_tags = item["Item"]["image_tag"]
    for new_tag in tags:
        current_tags.append(new_tag)
    current_tags = list(set(current_tags))
    try:
        response = table.put_item(
            Item={
                'user_id': user_id,
                'image_tag': current_tags,
                'image_url': image_url
            })
    except Exception:
        print(Exception)
    else:
        return response


def insert_item():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('assignment_image')
    try:
        response = table.put_item(
            Item={
                'user_id': '1',
                'image_tag': ['dog', 'iphone'],
                'image_url': 'http://aws/123/234/48'
            })
    except Exception:
        print(Exception)
    else:
        return response
