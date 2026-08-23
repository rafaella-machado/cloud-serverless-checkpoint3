def lambda_handler(event, context):
    """
    Processa mensagens recebidas de um tópico SNS.
    """

    for record in event.get("Records", []):
        sns = record.get("Sns", {})

        topic_arn = sns.get("TopicArn")
        message = sns.get("Message")

        print(f"Mensagem recebida do SNS: {message}")
        print(f"Tópico de origem: {topic_arn}")

    return {
        "message": "Evento SNS processado com sucesso"
    }
