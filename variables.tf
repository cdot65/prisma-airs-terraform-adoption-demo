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

