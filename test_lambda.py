from lambda_function import lambda_handler


def test_lambda_handler():
    event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "Sns": {
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:orders",
                    "Message": "Novo pedido recebido"
                }
            }
        ]
    }

    response = lambda_handler(event, None)

    assert response["message"] == "Evento SNS processado com sucesso"


if __name__ == "__main__":
    test_lambda_handler()
    print("Teste executado com sucesso!")
