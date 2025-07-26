PUT file://../apps/app2/streamlit_app.py @APP2_STAGE OVERWRITE = TRUE AUTO_COMPRESS=FALSE;
PUT file://../apps/app2/apps.json @APP2_STAGE OVERWRITE = TRUE AUTO_COMPRESS=FALSE;
PUT file://../apps/app2/preview.png @APP2_STAGE OVERWRITE = TRUE AUTO_COMPRESS=FALSE;