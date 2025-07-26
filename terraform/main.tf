resource "snowflake_stage" "app_stage" {
  for_each = { for app in var.apps : app.app_name => app }
  name     = "${each.value.stage_name}_STAGE"
  database = each.value.database
  schema   = each.value.schema
  comment  = "Stage for ${each.value.app_name} files"
  directory = "ENABLE = true"
}

resource "snowflake_streamlit" "streamlit_app" {
  for_each = { for app in var.apps : app.app_name => app }
  name            = "${each.value.stage_name}_STREAMLIT"
  database        = each.value.database
  schema          = each.value.schema
  stage           = "${each.value.database}.${each.value.schema}.${snowflake_stage.app_stage[each.value.app_name].name}"
  main_file       = "streamlit_app.py"
  comment         = "Streamlit app for ${each.value.app_name}"
  query_warehouse = var.snowflake_warehouse
}

resource "null_resource" "upload_streamlit_script" {
  for_each = { for app in var.apps : app.app_name => app }
  depends_on = [snowflake_streamlit.streamlit_app]
  provisioner "local-exec" {
    environment = {
      SNOWSQL_PWD = var.snowflake_password
    }
    
    command = "snowsql -a ${var.snowflake_org_name}-${var.snowflake_account_name} -u ${var.snowflake_user} -r ${var.snowflake_role} -d ${each.value.database} -s ${each.value.schema} -f ../apps/${each.value.stage_name}/upload_app.sql"
  }

  triggers = {
    always_run = timestamp()
  }
}

