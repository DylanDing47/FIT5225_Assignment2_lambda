import json

import boto3
from boto3.dynamodb.conditions import Attr, Or


def lambda_handler(event, context):
    query_parameters = json.loads(event["body"])["queryStringParameters"]
    print(type(query_parameters))

    tags = []
    for value in query_parameters.values():
        tags = tags + value

    if len(tags) == 0:
        return {
            "statusCode": 200,
            "body": "Please input valid tag(s)",
            "isBase64Encoded": "false"
        }
    elif len(tags) == 1:
        filter_expression = Attr("image_tag").contains(tags[0])

    else:
        filter_expression = Or(*[(Attr("image_tag").contains(value)) for value in tags])

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("assignment_image")

    response = table.scan(
        FilterExpression=filter_expression
    )

    result = {"links": []}
    for item in response["Items"]:
        print(item)
        result["links"].append(item["image_url"])

    return {
        "statusCode": 200,
        "body": json.dumps(result),
        "isBase64Encoded": "false"
    }
