import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Get the table name from environment variable
        table_name = os.environ.get('TABLE_NAME', 'CloudResumeVisitorCount')
        table = dynamodb.Table(table_name)
        
        # Atomically increment the visitor count
        response = table.update_item(
            Key={
                'id': 'visitors'
            },
            UpdateExpression='ADD count_value :incr',
            ExpressionAttributeValues={
                ':incr': 1
            },
            ReturnValues='UPDATED_NEW'
        )
        
        # Get the new count
        new_count = int(response['Attributes']['count_value'])
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # Or specific domain
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'count': new_count
            })
        }
    except ClientError as e:
        print(f"Error updating DynamoDB: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Could not update visitor count'
            })
        }
    except Exception as e:
        print(f"Unknown error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
