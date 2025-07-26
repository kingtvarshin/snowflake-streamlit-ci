variable "snowflake_account_name" {
  description = "Your Snowflake account identifier"
  type        = string
}

variable "snowflake_org_name" {
  description = "Your Snowflake account identifier"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Role to use"
  type        = string
  default     = "SYSADMIN"
}

# variable "snowflake_region" {
#   description = "Region (e.g., ap-south-1)"
#   type        = string
# }

variable "snowflake_warehouse" {
  description = "Warehouse to use"
  type        = string
  default     = "COMPUTE_WH"
}

variable "apps" {
  description = "List of apps with their configurations"
  type = list(object({
    app_name         = string
    stage_name  = string
    database         = string
    schema           = string
  }))
  default = [
    {
      app_name         = "app1"
      stage_name  = "app1"
      database         = "STREAMLIT_APPS"
      schema           = "APP"
    },
    {
      app_name         = "app2"
      stage_name  = "app2"
      database         = "STREAMLIT_APPS"
      schema           = "APP"
    },
    {
      app_name         = "app3"
      stage_name  = "app3"
      database         = "STREAMLIT_APPS"
      schema           = "APP"
    }
  ]
}
