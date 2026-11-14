# Acesso aos modelos Amazon Bedrock — por agente e com permissões específicas

O exemplo **Hello World não invoca um modelo**. Um agente que utiliza LLM precisa declarar os ARNs exatos dos modelos, inference profiles ou recursos permitidos em seu `agent.yaml`.

Exemplo **ilustrativo** (substitua pelo ARN verdadeiro da sua conta):

```yaml
spec:
  models:
    arns:
      - arn:aws:bedrock:us-east-1:123456789012:inference-profile/SUBSTITUIR_POR_ID_REAL
```

O módulo Terraform de Runtime concede somente `bedrock:InvokeModel` e `bedrock:InvokeModelWithResponseStream` para os recursos listados. Inference profiles com inferência entre regiões podem exigir autorização dos modelos de destino nas regiões correspondentes. Verifique isso na documentação de IAM do Bedrock.

## Exemplo Python com Converse API

Adicione `boto3` ao `requirements.txt` do agente.

```python
import os
import boto3

client = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)


def perguntar_ao_modelo(pergunta: str) -> str:
    model_id = os.environ["BEDROCK_MODEL_ID"]
    resposta = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": pergunta}]}],
        inferenceConfig={"maxTokens": 256, "temperature": 0.0},
    )
    blocos = resposta["output"]["message"]["content"]
    return "".join(bloco.get("text", "") for bloco in blocos)
```

O nome da variável `BEDROCK_MODEL_ID` não é um segredo, mas precisa ser configurado corretamente no ambiente do Runtime. **Atenção:** a raiz Terraform desta versão ainda **não** mapeia automaticamente um identificador de modelo do manifesto para essa variável. Apenas acrescentar ARNs ao YAML **não é suficiente** para o exemplo realizar a chamada.

## Antes de executar

- Confirmar acesso e eventuais requisitos de habilitação/assinatura do modelo na conta AWS.
- Confirmar compatibilidade de região e IDs/ARNs, inclusive inference profiles.
- Conceder permissões ao **execution role do Runtime**, não apenas à role da pipeline de deploy.
- Não inserir chaves de API, credenciais ou tokens no código, YAML, GitHub Actions logs ou Terraform state.
- Fazer um smoke test em DEV antes de ampliar a autorização.

A role OIDC do GitHub executa operações de provisionamento, enquanto a execution role do AgentCore invoca o modelo em tempo de execução. São papéis diferentes.
