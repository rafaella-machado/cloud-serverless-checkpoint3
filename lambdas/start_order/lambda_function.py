import json
import boto3


stepfunctions = boto3.client("stepfunctions")

STATE_MACHINE_ARN = (
    "arn:aws:states:us-east-1:896328389669:"
    "stateMachine:order-processing-workflow"
)


def lambda_handler(event, context):
    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    response = stepfunctions.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(body)
    )

    return {
        "statusCode": 202,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Pedido enviado para processamento",
            "executionArn": response["executionArn"],
            "startDate": response["startDate"].isoformat()
        })
    }
