import os
import boto3
from botocore.exceptions import ClientError


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("IDEMPOTENCY_TABLE", "orders-idempotency"))


def lambda_handler(event, context):
    """
    Processa um pedido garantindo idempotência.
    """

    order_id = event.get("order_id")

    if not order_id:
        raise ValueError("order_id é obrigatório")

    try:
        response = table.get_item(
            Key={"order_id": order_id}
        )

        if "Item" in response:
            print(f"Pedido {order_id} já foi processado.")

            return {
                "processed": False,
                "duplicate": True,
                "order_id": order_id,
                "message": "Pedido já processado"
            }

        print(f"Processando pedido: {order_id}")

        # Simula o processamento do pedido.
        result = {
            "processed": True,
            "duplicate": False,
            "order_id": order_id,
            "message": "Pedido processado com sucesso"
        }

        table.put_item(
            Item={
                "order_id": order_id,
                "status": "COMPLETED"
            }
        )

        return result

    except ClientError as error:
        print(f"Erro ao acessar o DynamoDB: {error}")
        raise
