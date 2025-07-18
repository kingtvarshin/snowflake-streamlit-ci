resource "snowflake_stage" "app1_stage" {
  name      = "APP1_STAGE"
  database  = var.database
  schema    = var.schema
  comment   = "Stage for Streamlit app 1 files"
  directory = "ENABLE = true"
}

resource "snowflake_streamlit" "app1_app" {
  name            = "APP1_STREAMLIT"
  database        = var.database
  schema          = var.schema
  stage           = "${var.database}.${var.schema}.${snowflake_stage.app1_stage.name}"
  main_file       = "streamlit_app.py"
  comment         = "Deployed via Terraform"
  query_warehouse = "COMPUTE_WH"
}

resource "null_resource" "upload_streamlit_script" {
  provisioner "local-exec" {
    environment = {
      SNOWSQL_PWD = var.snowflake_password
    }

    command = "snowsql -a ${var.snowflake_org_name}-${var.snowflake_account_name} -u ${var.snowflake_user} -r ${var.snowflake_role} -d ${var.database} -s ${var.schema} -f ../apps/${var.app_folder_name}/upload_app.sql"
  }

  triggers = {
    always_run = timestamp()
  }
}

