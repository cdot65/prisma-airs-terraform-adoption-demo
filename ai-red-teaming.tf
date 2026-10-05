# Prompt set: This container remains unused; importing it does not run an assessment.
resource "prisma-airs_red_team_custom_prompt_set" "demonstration" {
  name        = var.red_team_prompt_set.name
  description = var.red_team_prompt_set.description

  lifecycle {
    prevent_destroy = true
  }
}
