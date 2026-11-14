# Arquitetura e limites da primeira versão

Este monorepo é a fonte da verdade para o **código Python** e a **configuração declarativa** de workloads do Amazon Bedrock AgentCore. As peças compartilhadas de infraestrutura e CI/CD continuam nos repositórios corporativos existentes.

## Responsabilidades

- `workloads/agents/`: agentes Python em AgentCore Runtime. O primeiro exemplo implementa HTTP; A2A e AG-UI ainda não possuem templates funcionais.
- `workloads/mcp-servers/`: servidores MCP Python hospedados no AgentCore, com transporte Streamable HTTP.
- `agent.yaml`: contrato declarativo de cada workload, validado pelo `scripts/platform.py`. Recursos não suportados provocam erro de validação; não são ignorados silenciosamente.
- `infra/runtime/`: root Terraform parametrizado para fazer deploy individual de um workload. O backend S3 usa chave de estado separada por workload e ambiente.
- `postalllog/infra-modules`: módulos Terraform e políticas IAM dos recursos físicos AWS.
- `postalllog/reusable-workflows`: lógica reutilizável de CI/CD e autenticação AWS via OIDC.

## Segurança e evolução

**CodeZip no S3 é o formato padrão**, sem ECR. Cada Runtime tem uma execution role própria. Invocar modelos Bedrock é opcional e depende da lista explícita de ARNs aprovada no manifesto. O Hello World não utiliza LLM.

Gateway, Memory, Browser, Identity, Policy e Code Interpreter exigem módulos e revisão de permissões específicos antes de serem habilitados. A primeira versão bloqueia recursos que ainda não implementa. **IAM inbound** (quem invoca o agente) e **permissões outbound** (o que o agente pode acessar) são responsabilidades diferentes.

### Evolução prevista

- **Gateway:** criar módulo, autorizações, Gateway Targets e estado Terraform independentes. Não criar um Gateway por agente automaticamente; definir fronteiras por domínio/segurança.
- **Memory:** módulo opcional, isolamento de ator/sessão, retenção e permissões restritas. Não compartilhar memória entre todos os agentes por padrão.
- **Browser:** revisar segurança de sessão, destinos permitidos, credenciais e ações autorizadas.
- **A2A/AG-UI:** adicionar handlers específicos, contratos e testes de integração antes de disponibilizar.

## Artefatos e isolamento do Terraform

Cada workload mantém seu `requirements.txt` e gera um ZIP próprio para **Linux ARM64**. Dependências nativas incompatíveis devem falhar durante o build, em vez de criar acidentalmente pacotes x86.

Não armazenar tokens ou senhas em `agent.yaml`, Git ou Terraform state. Para integrações futuras, usar Secrets Manager e IAM com menor privilégio.

O estado usa uma chave no formato:

```text
agentic-platform/workloads/agents/<nome>/terraform.tfstate
```

O bucket é separado por ambiente: `postall-log-tfstates-dev`, `postall-log-tfstates-hom` ou `postall-log-tfstates-prod`, seguindo o padrão encontrado na organização. Esses recursos precisam existir.

## Implantação controlada

O workflow `platform-deploy.yaml` é acionado **manualmente**. O ambiente `prod` deve ser protegido pelas regras do GitHub Environments; sem elas, a seleção manual de `prod` não oferece a aprovação desejada. Após a primeira validação, fixar versões revisadas dos workflows reutilizáveis e módulos Terraform por commit/tag imutável.
