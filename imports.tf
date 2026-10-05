# Adoption: Bind existing remote identities to meaningful Terraform addresses.
# Import records ownership; review a plan with no configuration-changing actions.
import {
  to = prisma-airs_runtime_custom_topic.demonstration
  id = var.runtime_topic_id
}

import {
  to = prisma-airs_red_team_custom_prompt_set.demonstration
  id = var.red_team_prompt_set_id
}

import {
  to = prisma-airs_gateway_config.demonstration
  id = var.gateway_config_id
}

import {
  to = prisma-airs_supply_chain_security_group.demonstration
  id = var.supply_chain_group_id
}
