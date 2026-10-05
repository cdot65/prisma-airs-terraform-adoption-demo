# Model group: Organize future models; this example neither onboards nor scans them.
resource "prisma-airs_supply_chain_security_group" "demonstration" {
  name        = var.supply_chain_group.name
  description = var.supply_chain_group.description
  source_type = var.supply_chain_group.source_type

  lifecycle {
    prevent_destroy = true
  }
}
