import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    # Process each SQS record
    for record in event['Records']:
        try:
            # Parse the SQS message body (single JSON decode)
            message = json.loads(record['body'])
            
            # If message came via SNS, extract the inner "Message" field
            if 'Message' in message:
                message = json.loads(message['Message'])
            
            # Validate required fields
            required_fields = ['orderId', 'userId', 'itemName', 'quantity', 'status', 'timestamp']
            for field in required_fields:
                if field not in message:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert quantity to number (DynamoDB expects numeric type)
            message['quantity'] = int(message['quantity'])
            
            # Save to DynamoDB
            table.put_item(Item=message)
            print(f"Successfully saved order {message['orderId']} to DynamoDB")
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            raise
        except ClientError as e:
            print(f"DynamoDB error: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise
    
    return {
        'statusCode': 200,
        'body': 'All messages processed successfully'
    }