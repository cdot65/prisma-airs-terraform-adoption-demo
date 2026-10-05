# Installation: Pin the released provider used throughout this walkthrough.
terraform {
  required_version = "= 1.16.4"
  required_providers {
    prisma-airs = {
      source  = "cdot65/prisma-airs"
      version = "= 0.12.0"
    }
  }
}
