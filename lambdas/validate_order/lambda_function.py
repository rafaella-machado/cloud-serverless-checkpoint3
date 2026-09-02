def lambda_handler(event, context):
    """
    Valida os dados básicos de um pedido antes do processamento.
    """

    order_id = event.get("order_id")
    customer = event.get("customer")
    amount = event.get("amount")

    if not order_id:
        raise ValueError("order_id é obrigatório")

    if not customer:
        raise ValueError("customer é obrigatório")

    if amount is None:
        raise ValueError("amount é obrigatório")

    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("amount deve ser um número maior que zero")

    print(f"Pedido validado: {order_id}")

    return {
        "valid": True,
        "order_id": order_id,
        "customer": customer,
        "amount": amount
    }
