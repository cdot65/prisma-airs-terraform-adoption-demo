# Adoption: Use the identity discovered from your existing Runtime topic ID.
variable "runtime_topic_id" {
  description = "Existing Runtime topic ID to adopt; never import an object owned by another state."
  type        = string
  nullable    = false
}

# Adoption: Use the identity discovered from your existing Red Team prompt set UUID.
variable "red_team_prompt_set_id" {
  description = "Existing Red Team prompt set UUID to adopt; never import an object owned by another state."
  type        = string
  nullable    = false
}

# Adoption: Use the identity discovered from your existing Gateway routing configuration UUID.
variable "gateway_config_id" {
  description = "Existing Gateway routing configuration UUID to adopt; never import an object owned by another state."
  type        = string
  nullable    = false
}

# Adoption: Use the identity discovered from your existing Supply Chain security group UUID.
variable "supply_chain_group_id" {
  description = "Existing Supply Chain security group UUID to adopt; never import an object owned by another state."
  type        = string
  nullable    = false
}

# Settings: Terraform reads these typed values directly from your HCL tfvars file.
variable "runtime_topic" {
  description = "Recovered Runtime topic settings; keep all examples during updates."
  type = object({
    name        = string
    description = string
    examples    = list(string)
  })
  nullable = false
  validation {
    condition     = length(var.runtime_topic.description) > 0 && length(var.runtime_topic.examples) >= 2 && length(var.runtime_topic.examples) <= 5
    error_message = "Use a nonempty description and two to five example prompts."
  }
}

variable "red_team_prompt_set" {
  description = "Recovered prompt set name and a nonempty description; clearing it requires replacement."
  type = object({
    name        = string
    description = string
  })
  nullable = false
  validation {
    condition     = length(var.red_team_prompt_set.description) > 0
    error_message = "Keep a nonempty description to avoid replacement when clearing it."
  }
}

variable "gateway_config" {
  description = "Recovered routing settings and an existing upstream selected by name."
  type = object({
    name               = string
    workspace_id       = string
    upstream_name      = string
    model              = string
    retry_attempts     = number
    retry_status_codes = list(number)
  })
  nullable = false
  validation {
    condition     = var.gateway_config.retry_attempts >= 0 && var.gateway_config.retry_attempts <= 3 && floor(var.gateway_config.retry_attempts) == var.gateway_config.retry_attempts
    error_message = "Use an integer from zero to three for bounded demo retries."
  }
}

variable "supply_chain_group" {
  description = "Recovered empty group settings; changing source_type requires replacement."
  type = object({
    name        = string
    description = string
    source_type = string
  })
  nullable = false
}
