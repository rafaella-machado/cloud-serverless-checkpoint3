# Checkpoint 3 - Serverless Order Processing Workflow

Projeto desenvolvido para o Checkpoint 3 da disciplina de **Serverless Computing e Arquiteturas Event-Driven**.

O projeto evolui uma aplicação serverless de processamento de pedidos para uma arquitetura orquestrada utilizando **AWS Lambda, AWS Step Functions, Amazon DynamoDB e Amazon SQS**.

## Arquitetura

```text
HTTP POST
   |
   v
Function URL
   |
   v
StartOrder Lambda
   |
   v
AWS Step Functions
   |
   +--> ValidateOrder Lambda
   |
   +--> ProcessOrder Lambda
   |        |
   |        v
   |    DynamoDB
   |    Idempotency
   |
   +--> FinishOrder Lambda
   |
   v
OrderCompleted
```

### Tratamento de falhas

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

## Tecnologias

* AWS Lambda
* AWS Step Functions
* Amazon DynamoDB
* Amazon SQS
* AWS IAM
* Python 3.12
* pytest
* Git/GitHub

## Estrutura do projeto

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

## Fluxo de processamento

### 1. StartOrder

A Lambda `start-order` recebe um pedido através de uma **Lambda Function URL** HTTP e inicia uma execução do AWS Step Functions.

Exemplo de entrada:

```json
{
  "order_id": "ORDER-001",
  "customer": "Rafaella",
  "amount": 100
}
```

A função inicia a execução do workflow e retorna HTTP `202` juntamente com o ARN da execução do Step Functions.

### 2. ValidateOrder

A Lambda `validate-order` valida os dados básicos do pedido:

* `order_id`
* `customer`
* `amount`
* `amount` maior que zero

Pedidos inválidos geram uma exceção e são direcionados para o tratamento de falhas do workflow.

### 3. ProcessOrder

A Lambda `process-order` realiza o processamento do pedido e utiliza o **Amazon DynamoDB** para garantir idempotência.

A tabela utilizada é:

```text
orders-idempotency
```

A chave de partição é:

```text
order_id
```

Quando um pedido é processado pela primeira vez, seu `order_id` é registrado no DynamoDB.

Quando o mesmo `order_id` é processado novamente, a função identifica o pedido como duplicado e não realiza um novo processamento.

Exemplo de resultado para um pedido duplicado:

```json
{
  "processed": false,
  "duplicate": true,
  "order_id": "ORDER-001",
  "message": "Pedido já processado"
}
```

### 4. FinishOrder

A Lambda `finish-order` finaliza o processamento e retorna o status do pedido.

Exemplo:

```json
{
  "order_id": "ORDER-001",
  "status": "SUCCESS",
  "processed": true,
  "duplicate": false,
  "message": "Pedido ORDER-001 finalizado com sucesso."
}
```

## Orquestração com AWS Step Functions

O AWS Step Functions é responsável por controlar a ordem de execução das funções:

```text
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

Cada etapa recebe a saída da etapa anterior, permitindo que o processamento seja realizado de forma organizada e controlada.

Em caso de erro, o workflow utiliza `Catch` para direcionar a execução para o fluxo de tratamento de falhas.

O fluxo de falha utiliza a etapa `SendToDLQ`, responsável pelo envio da mensagem para a fila SQS `orders-dlq`.

## Retry

As tarefas Lambda do Step Functions possuem política de retry para erros transitórios da infraestrutura AWS.

São considerados:

* `Lambda.ServiceException`
* `Lambda.AWSLambdaException`
* `Lambda.SdkClientException`

Configuração utilizada:

```text
IntervalSeconds: 2
MaxAttempts: 3
BackoffRate: 2
```

Erros de validação, como um valor negativo para `amount`, não são tratados como erros transitórios e seguem para o fluxo de falha.

## Dead-Letter Queue

O workflow possui tratamento de falhas utilizando **Amazon SQS**.

Quando uma tarefa falha e não consegue ser concluída após as tentativas configuradas, o `Catch` direciona a execução para a etapa `SendToDLQ`.

```text
Catch
  |
  v
SendToDLQ
  |
  v
orders-dlq
  |
  v
OrderFailed
```

A mensagem enviada para a DLQ contém os dados do pedido e as informações relacionadas ao erro.

## Idempotência

A idempotência é implementada na Lambda `process-order` utilizando o Amazon DynamoDB.

Quando um pedido é processado pela primeira vez, seu `order_id` é armazenado na tabela.

Quando o mesmo pedido é enviado novamente, o sistema identifica que o `order_id` já existe e evita um novo processamento.

Exemplo:

```text
Primeira execução:
ORDER-001
processed = true
duplicate = false

Segunda execução:
ORDER-001
processed = false
duplicate = true
```

O resultado da segunda execução está registrado em:

```text
process-response-duplicate.json
```

O resultado de processamento normal está registrado em:

```text
process-response.json
```

Dessa forma, o mesmo pedido não é processado novamente.

## Segurança

O projeto não utiliza chaves de acesso AWS, arquivos de credenciais ou secrets no código-fonte.

As permissões são controladas através de **AWS IAM Roles** específicas para cada componente.

As permissões seguem o princípio do menor privilégio, permitindo somente as ações necessárias para cada serviço.

Exemplos:

* Lambda `process-order`: acesso ao DynamoDB necessário para idempotência.
* Lambda `start-order`: permissão para iniciar a execução do Step Functions.
* Step Functions: permissão para executar as Lambdas e enviar mensagens para a SQS.

A URL pública da Function URL não é armazenada neste repositório.

## Pré-requisitos

* Conta AWS
* AWS CLI configurado
* Python 3.12+
* Git

## Execução dos testes locais

Clone o repositório:

```bash
git clone https://github.com/rafaella-machado/cloud-serverless-checkpoint3.git
cd cloud-serverless-checkpoint3
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute os testes:

```bash
python -m pytest -q
```

Resultado obtido durante a validação do projeto:

```text
......... [100%]
9 passed in 0.04s
```

Os testes verificam:

* validação de pedidos;
* rejeição de dados inválidos;
* finalização de pedidos;
* tratamento de pedidos duplicados;
* estrutura e configurações principais do workflow.

## Validação na AWS

Além dos testes unitários locais, o fluxo foi validado diretamente no ambiente AWS.

### Teste da Function URL

A entrada HTTP foi enviada para a Function URL da Lambda `start-order`.

Exemplo:

```json
{
  "order_id": "ORDER-001",
  "customer": "Rafaella",
  "amount": 100
}
```

A Function URL recebeu corretamente a requisição e iniciou uma execução do AWS Step Functions.

A resposta obtida foi no formato:

```json
{
  "message": "Pedido enviado para processamento",
  "executionArn": "arn:aws:states:...",
  "startDate": "2026-09-03T04:17:05.337000+00:00"
}
```

A URL pública da Function URL não é publicada neste README.

### Teste de processamento

O processamento do pedido foi validado através do workflow do Step Functions, seguindo as etapas:

```text
ValidateOrder
      ↓
ProcessOrder
      ↓
FinishOrder
      ↓
OrderCompleted
```

O processamento utiliza o DynamoDB para controle de idempotência.

### Teste de idempotência

Foi validado o comportamento de duplicidade utilizando o mesmo `order_id`.

Na primeira execução:

```text
processed = true
duplicate = false
```

Em uma nova execução utilizando o mesmo `order_id`:

```text
processed = false
duplicate = true
```

O segundo processamento é identificado como duplicado e não realiza novamente o processamento do pedido.

Os resultados utilizados como evidência estão nos arquivos:

```text
process-response.json
process-response-duplicate.json
```

### Teste de validação

Também foi validado o tratamento de pedidos inválidos, incluindo pedidos com valor (`amount`) menor ou igual a zero.

Quando a validação falha, a exceção é propagada para o workflow e o mecanismo de `Catch` direciona o processamento para o fluxo de falha.

## Recursos AWS utilizados

**Região:**

```text
us-east-1
```

### AWS Lambda

* `start-order`
* `validate-order`
* `process-order`
* `finish-order`

### AWS Step Functions

* `order-processing-workflow`

### Amazon DynamoDB

* `orders-idempotency`

### Amazon SQS

* `orders-dlq`

### AWS IAM

Roles específicas para:

* Lambda `start-order`
* Lambda `validate-order`
* Lambda `process-order`
* Lambda `finish-order`
* AWS Step Functions

## Resultado

O projeto implementa uma arquitetura serverless orquestrada para processamento de pedidos, contemplando os principais requisitos do Checkpoint 3:

* Orquestração através do AWS Step Functions;
* Funções serverless utilizando AWS Lambda;
* Idempotência utilizando Amazon DynamoDB;
* Retry para erros transitórios;
* Tratamento de falhas utilizando `Catch`;
* Dead-Letter Queue utilizando Amazon SQS;
* Controle de acesso utilizando AWS IAM;
* Entrada HTTP através de Lambda Function URL;
* Testes automatizados utilizando pytest;
* Organização do código em funções independentes;
* Evidências de processamento normal e duplicado.

## Autor

**Rafaella Machado**
