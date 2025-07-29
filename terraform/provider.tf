terraform {
  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = ">= 2.3.0"
    }
  }
  required_version = ">= 1.3.0"
}


provider "snowflake" {

  account_name             = var.snowflake_account_name
  organization_name        = var.snowflake_org_name
  user                     = var.snowflake_user
  password                 = var.snowflake_password
  preview_features_enabled = ["snowflake_stage_resource"]
}
