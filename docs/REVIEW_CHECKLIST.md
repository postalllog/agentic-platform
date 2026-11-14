# Checklist de revisão do PR e do primeiro deploy

## Código e segurança

- [ ] O ZIP foi **descompactado na raiz** e contém `.github/workflows/`.
- [ ] O PR é de uma branch `feat/*` para `main`; a CI concluiu com sucesso.
- [ ] A execution role tem permissões mínimas; `iam:PassRole` da pipeline está restrito.
- [ ] Os ARNs autorizados de modelos são específicos (sem `bedrock:*` ou acesso irrestrito).
- [ ] Não existem credenciais, tokens ou segredos versionados.
- [ ] Nenhuma chave SSH privada é impressa nos logs.

## Infraestrutura

- [ ] PR do módulo Terraform de Runtime no `infra-modules` revisado e mesclado.
- [ ] PR do workflow reutilizável no `reusable-workflows` revisado e mesclado.
- [ ] `terraform fmt -check` e `terraform validate` executados com o provider AWS real.
- [ ] Confirmados CodeZip, Python 3.13, arquitetura ARM64 e entrypoint em `us-east-1`.
- [ ] Backend Terraform (buckets S3 + tabela de locking) existe e está acessível.
- [ ] Bucket de artefatos separado por ambiente e configurado no GitHub Actions.
- [ ] GitHub Environments `dev`, `hom`, `prod` e regras de aprovação conferidos.
- [ ] Verificados limites de tamanho de ZIP e ZIP descompactado do AgentCore.

## Primeiro teste em DEV

- [ ] Workflow executado manualmente selecionando `workloads/agents/hello-world` e `dev`.
- [ ] O Terraform retornou o ARN do Runtime sem erro.
- [ ] Invocação remota realizada por principal IAM com `InvokeAgentRuntime` autorizado.
- [ ] Resposta Hello World, logs, tracing e custos inspecionados.
- [ ] Fluxo de reversão/rollback discutido antes da produção.
- [ ] Versões do módulo e workflow fixadas em tags ou commits revisados.

## Próximas funcionalidades

- [ ] Gateway e Gateway Targets somente quando uma integração real precisar deles.
- [ ] Memory com isolamento por agente/ator/sessão.
- [ ] Browser e Code Interpreter após política de uso, segurança e testes.
- [ ] Identity, Policy e demais integrações avaliados separadamente.
