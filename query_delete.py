import boto3


def lambda_handler(event, context):
    """
    user_id = json.loads(event['body'])['user_id'],
    image_url = json.loads(event['body'])['image_url']
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('image_tag2')
    item = table.get_item(Key={'user_id': "13", 'image_url': "https://angularuploadtest.s3.amazonaws.com/download.jpg"})
    image_file_name = item["Item"]["image_file_name"]
    """
    client = boto3.client('s3')

    #client.delete_object(Bucket='angularuploadtest', Key=image_file_name)

    table.delete_item(
        Key={
            'user_id':json.loads(event['body'])['user_id'],
            'image_url': json.loads(event['body'])['image_url']
        }
    )

    result = "delete image: " + image_file_name

    return {
        "statusCode": 200,
        "body": json.dumps(result),
        "isBase64Encoded": "false"
    }
    """
