# Ownership: These are the four adopted identities, not the shared Gateway prerequisites.
output "managed_resource_ids" {
  description = "Record these identities before state migration and verify them afterward."
  value = {
    runtime_topic       = prisma-airs_runtime_custom_topic.demonstration.id
    red_team_prompt_set = prisma-airs_red_team_custom_prompt_set.demonstration.id
    gateway_config      = prisma-airs_gateway_config.demonstration.id
    supply_chain_group  = prisma-airs_supply_chain_security_group.demonstration.id
  }
}
