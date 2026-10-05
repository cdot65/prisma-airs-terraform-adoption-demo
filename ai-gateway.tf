# Discovery: Reference an existing upstream by name without managing its credentials.
data "prisma-airs_gateway_providers" "existing" {
  workspace_id = var.gateway_config.workspace_id
  page_size    = 100
  current_page = 1

  lifecycle {
    postcondition {
      condition     = self.total_count <= length(self.items)
      error_message = "The provider inventory spans more than one page; implement explicit pagination before selecting an upstream."
    }
    postcondition {
      condition     = length([for item in self.items : item if item.name == var.gateway_config.upstream_name && item.status == "active"]) == 1
      error_message = "Select exactly one active provider by its discovered name."
    }
  }
}

locals {
  gateway_upstream = one([for item in data.prisma-airs_gateway_providers.existing.items : item
    if item.name == var.gateway_config.upstream_name && item.status == "active"
  ])
}

# Routing: A leaf edit replaces the document but retains this configuration's identity.
resource "prisma-airs_gateway_config" "demonstration" {
  name         = var.gateway_config.name
  workspace_id = var.gateway_config.workspace_id

  config = {
    provider = "@${local.gateway_upstream.slug}"
    override_params = {
      model = var.gateway_config.model
    }
    retry = {
      attempts = var.gateway_config.retry_attempts
      # Shape: Preserve the generated tuple inside the provider's dynamic document.
      on_status_codes = [for code in var.gateway_config.retry_status_codes : code]
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}
