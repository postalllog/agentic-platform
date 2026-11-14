provider "aws" {
  region = var.region
}

locals {
  manifest   = yamldecode(file("${path.module}/${var.workload_dir}/agent.yaml"))
  workload   = local.manifest.metadata.name
  runtime_id = replace("${var.environment}_${local.workload}", "-", "_")
  protocol   = local.manifest.spec.runtime.protocol
  model_arns = try(local.manifest.spec.models.arns, [])
}

module "runtime" {
  # Pinned tag recommended for production after PR #1 is merged.
  source     = "git::ssh://git@github.com/postalllog/infra-modules.git//bedrock-agentcore-runtime?ref=main"
  name       = local.runtime_id
  protocol   = local.protocol
  s3_bucket  = var.artifact_bucket
  s3_key     = var.artifact_key
  entry_point = [local.manifest.spec.runtime.entrypoint]
  model_arns = local.model_arns
  tags = {
    application = "agentic-platform"
    workload    = local.workload
    environment = var.environment
    owner       = local.manifest.metadata.owner
  }
}
