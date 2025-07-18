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

variable "database" {
  description = "Snowflake database for app"
  type        = string
  default     = "STREAMLIT_APPS"
}

variable "schema" {
  description = "Schema for app"
  type        = string
  default     = "APP1"
}

variable "app_folder_name" {
  description = "Folder name for the Streamlit app"
  type        = string
  default     = "app1"

}