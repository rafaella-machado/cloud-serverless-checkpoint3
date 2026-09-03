# Checkpoint 3 - Serverless Order Processing Workflow

Projeto desenvolvido para o Checkpoint 3 da disciplina **Serverless Computing e Arquiteturas Event-Driven**.

O objetivo é implementar um fluxo de processamento de pedidos utilizando serviços serverless da AWS, com orquestração por AWS Step Functions, processamento desacoplado, tratamento de falhas, Dead-Letter Queue (DLQ) e controle de idempotência com DynamoDB.

---

## Architecture

```text
Client
   |
   v
Lambda Function URL
   |
   v
StartOrder Lambda
   |
   v
AWS Step Functions
   |
   +----------------------+
   |                      |
   v                      v
ValidateOrder         ProcessOrder
   |                      |
   |                      +--> DynamoDB
   |                           (Idempotency)
   |                      
   v
FinishOrder
   |
   v
OrderCompleted
```

### Failure handling

```text
Lambda Task
   |
   +--> Retry
   |
   +--> Catch
         |
         v
      SendToDLQ
         |
         v
      Amazon SQS
      orders-dlq
         |
         v
      OrderFailed
```

---

## Technologies

* AWS Lambda
* AWS Step Functions
* Amazon DynamoDB
* Amazon SQS
* AWS IAM
* Lambda Function URL
* Python 3.12
* boto3
* pytest
* Git/GitHub

---

## Project Structure

```text
cloud-serverless-checkpoint3/
├── lambdas/
│   ├── start_order/
│   │   └── lambda_function.py
│   ├── validate_order/
│   │   └── lambda_function.py
│   ├── process_order/
│   │   └── lambda_function.py
│   └── finish_order/
│       └── lambda_function.py
├── tests/
│   └── test_lambdas.py
├── workflow/
│   └── order-processing-workflow.json
├── process-response.json
├── process-response-duplicate.json
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Processing Flow

### 1. StartOrder

Receives the order through the Lambda Function URL and starts the AWS Step Functions execution.

Example input:

```json
{
  "order_id": "ORDER-001",
  "customer": "Rafaella",
  "amount": 100
}
```

Example response:

```json
{
  "message": "Pedido enviado para processamento",
  "executionArn": "arn:aws:states:...",
  "startDate": "2026-09-03T04:17:05.337000+00:00"
}
```

The Function URL was successfully validated by sending an order and confirming that a Step Functions execution was started.

---

### 2. ValidateOrder

Validates the required order information.

The following conditions are checked:

* `order_id` must be provided.
* `customer` must be provided.
* `amount` must be greater than zero.

Invalid orders generate an error and follow the failure path defined in the Step Functions workflow.

---

### 3. ProcessOrder

Processes the order and performs an idempotency check using Amazon DynamoDB.

The DynamoDB table used for idempotency is:

```text
orders-idempotency
```

The partition key is:

```text
order_id
```

If the order has already been processed, the Lambda identifies the duplicate and avoids processing the same order again.

---

### 4. FinishOrder

Finalizes the order after successful processing.

Example response:

```json
{
  "order_id": "ORDER-001",
  "status": "SUCCESS",
  "processed": true,
  "duplicate": false,
  "message": "Pedido ORDER-001 finalizado com sucesso."
}
```

---

## Orchestration with AWS Step Functions

The workflow is defined in:

```text
workflow/order-processing-workflow.json
```

The Step Functions state machine coordinates the Lambda functions responsible for:

1. Validating the order.
2. Processing the order.
3. Finalizing the order.

The workflow also defines the retry and failure mechanisms.

---

## Retry

The workflow contains retry configuration for transient AWS Lambda failures.

The following errors are configured for retry:

```text
Lambda.ServiceException
Lambda.AWSLambdaException
Lambda.SdkClientException
```

Configuration:

```text
IntervalSeconds: 2
MaxAttempts: 3
BackoffRate: 2
```

This allows transient failures to be retried automatically before the workflow proceeds to the failure path.

---

## Dead-Letter Queue (DLQ)

When an error cannot be successfully processed after the configured retry attempts, the Step Functions workflow uses the `Catch` mechanism.

The error is routed to the `SendToDLQ` state, which sends the failure information to:

```text
Amazon SQS
orders-dlq
```

The workflow then reaches the `OrderFailed` state.

This provides a mechanism for retaining failed messages for later analysis or reprocessing.

---

## Idempotency

Idempotency is implemented in the `ProcessOrder` Lambda using Amazon DynamoDB.

The same `order_id` cannot be successfully processed more than once.

For example, when the same order is submitted twice:

### First execution

```text
ORDER-001
processed = true
duplicate = false
```

### Second execution

```text
ORDER-001
processed = false
duplicate = true
```

The duplicate execution returns:

```json
{
  "processed": false,
  "duplicate": true,
  "order_id": "ORDER-001",
  "message": "Pedido já processado"
}
```

The response examples are stored in:

```text
process-response.json
process-response-duplicate.json
```

---

## Security

The project follows basic AWS security practices:

* No AWS access keys or credentials are stored in the source code.
* Lambda functions use IAM execution roles.
* AWS permissions are granted according to the required operations.
* DynamoDB and other AWS resources are accessed through IAM permissions.
* The public Function URL is not stored in the repository.
* No secrets or sensitive credentials are committed to GitHub.

---

## Prerequisites

* Python 3.12+
* AWS account
* AWS CLI configured for deployment/testing
* Access to the required AWS services
* Git

---

## Local Tests

Clone the repository:

```bash
git clone https://github.com/rafaella-machado/cloud-serverless-checkpoint3.git
cd cloud-serverless-checkpoint3
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -q
```

Result:

```text
......... [100%]
9 passed in 0.04s
```

All local tests passed successfully.

---

## AWS Validation

### Function URL

The Lambda Function URL was tested with the following request:

```json
{
  "order_id": "ORDER-001",
  "customer": "Rafaella",
  "amount": 100
}
```

The Function URL successfully received the request and started an AWS Step Functions execution.

The response returned the execution ARN and the execution start time.

The public Function URL is intentionally not published in this repository.

---

### Order Processing

The order processing workflow was validated through the configured Step Functions states:

```text
StartOrder
    |
    v
ValidateOrder
    |
    v
ProcessOrder
    |
    v
FinishOrder
    |
    v
OrderCompleted
```

---

### Idempotency Validation

Idempotency was validated by processing the same `order_id` more than once.

The first execution was identified as a new order:

```text
processed = true
duplicate = false
```

The subsequent execution was identified as a duplicate:

```text
processed = false
duplicate = true
```

The response examples are included in:

```text
process-response.json
process-response-duplicate.json
```

---

### Validation of Invalid Orders

The validation Lambda rejects orders where:

```text
amount <= 0
```

The Step Functions workflow contains a `Catch` path for failures, allowing invalid or failed executions to follow the configured failure-handling flow.

---

## AWS Resources

The project uses the following AWS resources:

```text
AWS Lambda
├── start-order
├── validate-order
├── process-order
└── finish-order

AWS Step Functions
└── order-processing-workflow

Amazon DynamoDB
└── orders-idempotency

Amazon SQS
└── orders-dlq

Lambda Function URL
└── StartOrder
```

---

## Result

The Checkpoint 3 implementation demonstrates a serverless order-processing workflow with:

* AWS Lambda
* AWS Step Functions orchestration
* Lambda Function URL
* Amazon DynamoDB idempotency
* Retry mechanisms
* Catch-based failure handling
* Amazon SQS Dead-Letter Queue
* IAM-based permissions
* Automated local tests

The project was successfully tested locally with:

```text
9 passed
```

and the Lambda Function URL was successfully validated by starting a Step Functions execution.

---

## Author

**Rafaella Machado**

Projeto acadêmico desenvolvido para a disciplina de **Serverless Computing e Arquiteturas Event-Driven**.
