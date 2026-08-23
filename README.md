# Checkpoint 2 - Arquitetura Serverless Orientada a Eventos

## Descrição

Este projeto corresponde ao Checkpoint 2 da disciplina de Cloud, Serverless e IA.

O objetivo é evoluir uma função serverless HTTP simples para uma arquitetura orientada a eventos (Event-Driven).

Nesta implementação, uma mensagem publicada em um tópico Amazon SNS dispara automaticamente uma função AWS Lambda. A função recebe o evento, extrai a mensagem e o tópico de origem e registra essas informações no Amazon CloudWatch Logs.

A solução utiliza uma arquitetura serverless orientada a eventos, permitindo o desacoplamento entre o produtor da mensagem e o processamento do evento.

## Provedor Utilizado

- AWS (Amazon Web Services)
- AWS Lambda
- Amazon SNS (Simple Notification Service)
- Amazon CloudWatch Logs
- AWS IAM
- AWS CloudShell

## Arquitetura

A arquitetura implementada segue o fluxo:

```
Amazon SNS Topic (orders)
        |
        v
AWS Lambda (checkpoint2-sns-orders)
        |
        v
Amazon CloudWatch Logs
```

O tópico SNS funciona como produtor do evento.

Quando uma nova mensagem é publicada no tópico `orders`, o Amazon SNS aciona automaticamente a função Lambda `checkpoint2-sns-orders`.

A Lambda processa o evento recebido, extrai a mensagem e identifica o tópico de origem. Essas informações são registradas no Amazon CloudWatch Logs.

## Estrutura do Projeto

```
cloud-serverless-checkpoint2/
├── lambda_function.py
├── test_lambda.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Pré-requisitos

Para executar o projeto localmente, é necessário possuir:

- Python 3 instalado
- Git instalado
- Terminal de comandos

Para realizar os testes e utilizar os recursos na AWS, é necessário possuir:

- Uma conta AWS
- AWS CLI configurado
- Permissões adequadas para acessar AWS Lambda, Amazon SNS e Amazon CloudWatch

## Como Rodar Localmente

### 1. Clonar o repositório

Clone o repositório público do GitHub:

```bash
git clone https://github.com/rafaella-machado/cloud-serverless-checkpoint2.git
```

### 2. Entrar na pasta do projeto

```bash
cd cloud-serverless-checkpoint2
```

### 3. Verificar os arquivos do projeto

A estrutura esperada é:

```
cloud-serverless-checkpoint2/
├── lambda_function.py
├── test_lambda.py
├── requirements.txt
├── README.md
└── .gitignore
```

### 4. Executar o teste local

Execute:

```bash
python3 test_lambda.py
```

O arquivo `test_lambda.py` simula localmente um evento enviado pelo Amazon SNS para a função Lambda.

O resultado esperado é:

```
Teste executado com sucesso!
```

## Funcionamento da Lambda

A função `lambda_handler`, localizada no arquivo `lambda_function.py`, é responsável por processar os eventos recebidos do Amazon SNS.

Para cada registro recebido, a função:

1. Obtém os dados do evento SNS.
2. Extrai a mensagem recebida.
3. Identifica o ARN do tópico de origem.
4. Registra a mensagem no Amazon CloudWatch Logs.
5. Registra o tópico de origem no Amazon CloudWatch Logs.
6. Retorna uma mensagem indicando que o evento foi processado com sucesso.

## Teste na AWS

Na AWS foi criado o tópico Amazon SNS:

`orders`

A função Lambda utilizada no projeto é:

`checkpoint2-sns-orders`

O tópico SNS foi configurado para possuir uma assinatura do tipo Lambda apontando para a função.

A assinatura possui o seguinte endpoint:

`arn:aws:lambda:us-east-1:896328389669:function:checkpoint2-sns-orders`

Uma mensagem foi publicada no tópico SNS utilizando o AWS CLI:

```bash
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:896328389669:orders \
  --message "TESTE CHECKPOINT 2 - SNS PARA LAMBDA"
```

A publicação retornou um `MessageId`, confirmando que a mensagem foi aceita pelo Amazon SNS.

A execução da Lambda foi posteriormente confirmada por meio das métricas do Amazon CloudWatch.

## Evidência do Processamento

Após a publicação da mensagem no SNS, a métrica de invocações da AWS Lambda registrou a execução da função.

Também foi possível verificar nos logs do Amazon CloudWatch:

```
Mensagem recebida do SNS: TESTE CHECKPOINT 2 - SNS PARA LAMBDA
```

E o tópico de origem:

```
Tópico de origem: arn:aws:sns:us-east-1:896328389669:orders
```

Isso comprova que a mensagem publicada no Amazon SNS foi recebida e processada pela função AWS Lambda.

O fluxo final validado foi:

```
Amazon SNS
     |
     v
AWS Lambda
     |
     v
Amazon CloudWatch Logs
```

## IAM

Foi criada uma IAM Role para permitir a execução da função Lambda.

A role recebeu a política:

`AWSLambdaBasicExecutionRole`

Essa política permite que a função Lambda envie seus logs para o Amazon CloudWatch Logs.

Também foi configurada uma permissão específica permitindo que o Amazon SNS invoque a função Lambda.

A permissão de invocação utiliza o serviço:

`sns.amazonaws.com`

e está restrita ao tópico SNS utilizado pelo projeto.

## Serviços AWS Utilizados

### Amazon SNS

Responsável por receber e publicar as mensagens do sistema.

### AWS Lambda

Responsável por processar automaticamente os eventos recebidos do Amazon SNS.

### Amazon CloudWatch Logs

Responsável por armazenar os registros gerados durante a execução da função Lambda.

### AWS IAM

Responsável pelo controle de permissões e pela IAM Role utilizada pela função Lambda.

### AWS CloudShell

Utilizado como ambiente de terminal para executar comandos AWS CLI, realizar testes e administrar os recursos utilizados no projeto.

## Segurança

O projeto segue boas práticas de segurança.

O repositório público do GitHub não contém:

- Chaves de acesso da AWS
- Senhas
- Tokens
- Credenciais
- Arquivos JSON contendo credenciais
- Informações secretas

As credenciais utilizadas para acessar os serviços da AWS não fazem parte do código-fonte versionado no GitHub.

## Repositório

O código-fonte do projeto está disponível no GitHub:

https://github.com/rafaella-machado/cloud-serverless-checkpoint2

O repositório contém o código-fonte, os testes, o arquivo `requirements.txt`, o `.gitignore` e este README com as instruções de execução e explicação da arquitetura.

## Conclusão

O Checkpoint 2 demonstra uma arquitetura serverless orientada a eventos utilizando Amazon SNS, AWS Lambda e Amazon CloudWatch Logs.

A solução permite desacoplar o produtor do evento do processamento, fazendo com que uma mensagem publicada no Amazon SNS seja automaticamente encaminhada para a função Lambda.

Dessa forma, a aplicação utiliza um modelo Event-Driven, no qual o processamento ocorre automaticamente em resposta à publicação de novos eventos.

A implementação foi testada na AWS e teve seu funcionamento confirmado por meio da execução da Lambda e dos registros gerados no Amazon CloudWatch Logs.Dessa forma, a aplicação utiliza um modelo Event-Driven, no qual o processamento ocorre automaticamente em resposta à publicação de novos eventos.
