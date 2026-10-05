# Detection topic: Preserve the complete example list when editing its description.
resource "prisma-airs_runtime_custom_topic" "demonstration" {
  topic_name  = var.runtime_topic.name
  description = var.runtime_topic.description
  examples    = var.runtime_topic.examples

  lifecycle {
    prevent_destroy = true
  }
}
