def lambda_handler(event, context):
    """
    Finaliza o processamento do pedido.
    """

    order_id = event.get("order_id")

    if not order_id:
        raise ValueError("order_id é obrigatório")

    processed = event.get("processed", False)
    duplicate = event.get("duplicate", False)

    if duplicate:
        message = f"Pedido {order_id} já havia sido processado."
    elif processed:
        message = f"Pedido {order_id} finalizado com sucesso."
    else:
        message = f"Pedido {order_id} não foi processado."

    print(message)

    return {
        "order_id": order_id,
        "status": "SUCCESS",
        "processed": processed,
        "duplicate": duplicate,
        "message": message
    }
