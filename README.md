# Checkpoint 2 - Arquitetura Serverless Orientada a Eventos

## Descrição

Este projeto corresponde ao Checkpoint 2 da disciplina de Cloud, Serverless e IA.

O objetivo é evoluir uma função serverless simples para uma arquitetura orientada a eventos (Event-Driven), utilizando serviços da AWS.

Nesta implementação, uma mensagem publicada em um tópico Amazon SNS dispara automaticamente uma função AWS Lambda. A função recebe o evento, extrai a mensagem e o tópico de origem e registra essas informações no Amazon CloudWatch Logs.

## Provedor Utilizado

- AWS (Amazon Web Services)
- AWS Lambda
- Amazon SNS (Simple Notification Service)
- Amazon CloudWatch Logs
- AWS IAM
- AWS CloudShell

## Arquitetura

A arquitetura implementada segue o fluxo:

SNS Topic (orders)
↓
AWS Lambda (checkpoint2-sns-orders)
↓
Amazon CloudWatch Logs

O tópico SNS funciona como produtor do evento. Quando uma nova mensagem é publicada no tópico orders, o SNS aciona automaticamente a função Lambda.

A Lambda processa o evento recebido e registra a mensagem e o tópico de origem nos logs do CloudWatch.

## Estrutura do Projeto

cloud-serverless-checkpoint2/
├── lambda_function.py
├── test_lambda.py
├── requirements.txt
├── README.md
└── .gitignore

## Funcionamento

A função lambda_handler recebe eventos enviados pelo Amazon SNS.

Para cada registro recebido, a função:

1. Obtém os dados do evento SNS.
2. Extrai a mensagem recebida.
3. Identifica o ARN do tópico de origem.
4. Registra essas informações no CloudWatch Logs.
5. Retorna uma mensagem indicando que o evento foi processado com sucesso.

## Teste Local

Foi criado o arquivo test_lambda.py para simular um evento SNS localmente.

O teste foi executado com:

python3 test_lambda.py

O teste apresentou uma mensagem recebida do SNS, identificou o tópico de origem e apresentou a mensagem "Teste executado com sucesso!".

## Teste na AWS

Após o deploy da função Lambda, foi criado o tópico SNS orders e configurada uma assinatura para a função Lambda checkpoint2-sns-orders.

Uma mensagem foi publicada no tópico SNS utilizando o AWS CLI.

A execução da Lambda foi confirmada por meio dos logs do Amazon CloudWatch.

Nos logs foi registrada a mensagem:

Mensagem recebida do SNS: Novo pedido recebido - Checkpoint 2

Também foi registrado o tópico de origem:

arn:aws:sns:us-east-1:896328389669:orders

## IAM

Foi criada a role checkpoint2-lambda-role para permitir que a função Lambda seja executada pela AWS.

A role recebeu a política AWSLambdaBasicExecutionRole, permitindo que a Lambda envie seus logs para o Amazon CloudWatch Logs.

Também foi configurada uma permissão para que o Amazon SNS possa invocar a função Lambda.

## Serviços AWS Utilizados

### Amazon SNS

Responsável por receber e publicar as mensagens do sistema.

### AWS Lambda

Responsável por processar automaticamente os eventos recebidos do SNS.

### Amazon CloudWatch Logs

Responsável por armazenar os registros gerados durante a execução da Lambda.

### AWS IAM

Responsável pelo controle de permissões e pela role utilizada pela função Lambda.

## Conclusão

O Checkpoint 2 demonstra uma arquitetura serverless orientada a eventos utilizando Amazon SNS, AWS Lambda e Amazon CloudWatch Logs.

A solução permite desacoplar o produtor do evento do processamento, fazendo com que uma mensagem publicada no SNS seja automaticamente encaminhada para a função Lambda.

Dessa forma, a aplicação utiliza um modelo Event-Driven, no qual o processamento ocorre automaticamente em resposta à publicação de novos eventos.
