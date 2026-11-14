# Plataforma de Agentes de IA — Postalllog

Monorepo de agentes e servidores MCP em **Python**, com empacotamento **ZIP no S3 (CodeZip)**, execução no **Amazon Bedrock AgentCore**, infraestrutura em **Terraform** e integração às esteiras compartilhadas do GitHub Actions da Postalllog. **Não utiliza Docker nem ECR para os workloads AgentCore deste bootstrap.**

> **Estado atual:** bootstrap inicial para revisão e testes em **DEV**. Ainda **não houve deploy real na AWS**. Os módulos de infraestrutura e o workflow compartilhado estão em Pull Requests separados e precisam ser revisados, validados e mesclados antes do primeiro deploy. Gateway, Memory, Browser, Identity, Policy e Code Interpreter **não são provisionados automaticamente** nesta entrega.

## Organização do projeto

```text
.github/workflows/                  # CI e disparo manual do deploy
workloads/agents/hello-world/      # Exemplo de agente HTTP
workloads/mcp-servers/hello-tools/  # Exemplo de servidor MCP
infra/runtime/                     # Terraform para cada workload
scripts/platform.py                # CLI para criar, validar, executar e empacotar
requirements-platform.txt          # Ferramentas de desenvolvimento

docs/ARCHITECTURE.md               # Decisões de arquitetura
docs/BEDROCK_MODELS.md             # Permissões e invocação de modelos
docs/REVIEW_CHECKLIST.md           # Checklist antes do deploy
```

## 1. Branches: preciso criar `develop`?

**Não é necessário.** Para o início, use `main` como branch estável e `feat/*` para mudanças. Abra um Pull Request para `main`, valide a CI e faça merge após aprovação. DEV, HOM e PROD são ambientes da AWS, não branches do Git. O workflow de deploy deste pacote é **manual**, iniciado no GitHub Actions; não publica automaticamente quando ocorre um push.

## 2. Como subir os arquivos no repositório

Este ZIP revisado contém os arquivos **diretamente na raiz**. Não envie o arquivo ZIP como um único arquivo para o GitHub: extraia seu conteúdo dentro da pasta do clone.

No Windows PowerShell (ajuste o caminho do ZIP conforme onde você o salvou):

```powershell
git clone https://github.com/postalllog/agentic-platform.git
cd agentic-platform
git switch -c feat/bootstrap-agentcore
Expand-Archive "$env:USERPROFILE\Downloads\agentic-platform-bootstrap-ptbr.zip" -DestinationPath . -Force
git add -A
git commit -m "feat: iniciar plataforma AgentCore com documentação em português"
git push -u origin feat/bootstrap-agentcore
```

Depois, no GitHub, use **Compare & pull request** e abra o PR de `feat/bootstrap-agentcore` para `main`. Se você já comitou o ZIP antigo na `main`, crie uma branch para a correção, remova o ZIP antigo do repositório e substitua pelos arquivos descompactados; não sobrescreva alterações existentes sem revisar o diff.

**Atenção:** o GitHub precisa receber a pasta oculta `.github/workflows`, que contém as duas esteiras.

## 3. Pré-requisitos para testar localmente

- Python **3.13** instalado.
- Git e PowerShell (Windows) ou shell equivalente.
- A AWS CLI será necessária para fazer deploy/invocação na AWS, mas **não** para os testes locais.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-platform.txt
python scripts/platform.py validate-all
python -m pytest -q workloads
```

Em Linux/macOS, ative o ambiente com `source .venv/bin/activate`.

## 4. Executar o Hello World HTTP localmente

```powershell
python -m pip install -r workloads/agents/hello-world/requirements.txt
python scripts/platform.py dev workloads/agents/hello-world
```

Em outro terminal PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8080/invocations' -ContentType 'application/json' -Body '{"name":"Postalllog"}'
```

Resposta esperada:

```json
{"message":"Hello, Postalllog!"}
```

Se quiser criar seu próprio agente:

```powershell
python scripts/platform.py new agent meu-agente
python scripts/platform.py validate workloads/agents/meu-agente
```

Depois, implemente a lógica de negócio em `workloads/agents/meu-agente/main.py`.

## 5. Executar o servidor MCP localmente

```powershell
python -m pip install -r workloads/mcp-servers/hello-tools/requirements.txt
python scripts/platform.py dev workloads/mcp-servers/hello-tools
```

O endpoint Streamable HTTP é `http://127.0.0.1:8000/mcp`. Utilize um cliente compatível com MCP (por exemplo, MCP Inspector). **Não** trate esse endpoint como uma API REST comum. Para criar outro servidor:

```powershell
python scripts/platform.py new mcp-server minhas-ferramentas
```

## 6. O que precisa acontecer antes do deploy na AWS

1. Revisar, validar e mesclar o **PR #1** em `postalllog/infra-modules` (módulo AgentCore Runtime CodeZip).
2. Revisar, validar e mesclar o **PR #10** em `postalllog/reusable-workflows` (esteira compartilhada AgentCore).
3. Mesclar o PR de bootstrap do próprio `agentic-platform`.
4. Configurar no GitHub os **Environments** `dev`, `hom` e `prod`; adotar aprovação obrigatória em produção.
5. Criar ou identificar um bucket de artefatos S3 **por conta/ambiente**. Cadastrar as Actions Variables `AGENTCORE_ARTIFACT_BUCKET_DEV`, `AGENTCORE_ARTIFACT_BUCKET_HOM` e `AGENTCORE_ARTIFACT_BUCKET_PROD` com os nomes reais dos buckets.
6. Cadastrar o secret `INFRA_MODULES`, usado pela esteira para ler o repositório privado de módulos Terraform; usar chave SSH somente leitura, em conjunto com o procedimento de segurança da equipe.
7. Revisar as permissões da role OIDC já utilizada pela Postalllog: Terraform backend (S3/DynamoDB), artefatos S3, criação/atualização do AgentCore e IAM/`iam:PassRole` restrito às roles previstas.
8. Confirmar suporte da versão do AWS provider, arquitetura ARM64 e runtime Python na região `us-east-1`; executar `terraform fmt` e `terraform validate` com dependências reais.
9. Só então, em **GitHub → Actions → Publicar agente no AgentCore → Run workflow**, informar o workload `workloads/agents/hello-world` e o ambiente `dev`.
10. Após o apply, obter o ARN gerado em `runtime_arn`, invocar com um principal IAM autorizado e conferir logs/custos no CloudWatch.

**Este pacote sozinho não faz deploy.** Antes dos merges, o workflow chamado em `reusable-workflows@main` e o módulo apontado para `infra-modules@main` ainda não existirão nesses caminhos. Nenhum deploy automático para PROD está configurado.

## 7. Comandos disponíveis da CLI

```text
python scripts/platform.py new agent NOME
python scripts/platform.py new mcp-server NOME
python scripts/platform.py validate workloads/agents/NOME
python scripts/platform.py validate-all
python scripts/platform.py build workloads/agents/NOME --output-dir dist
python scripts/platform.py dev workloads/agents/NOME
```

## 8. O que ainda **não** está pronto

- Suporte completo a AgentCore Gateway, Memory, Browser, Identity, Policy e Code Interpreter no monorepo.
- Templates funcionais e testes integrados de A2A/AG-UI.
- Integração automática de um `model_id` aos manifests e às variáveis de ambiente do agente.
- Deploy integrado validado em uma conta AWS real.
- Promoção imutável e testes de regressão/smoke test remoto após publicação.

**Próximo objetivo:** validar o primeiro agente HTTP em DEV, depois adicionar as capacidades opcionais por módulos independentes, sem conceder permissões amplas por padrão. Consulte os arquivos em `docs/`.
