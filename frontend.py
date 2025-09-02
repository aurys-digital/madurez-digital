import streamlit as st
from loguru import logger

import msal
import config as cfg
from backend import map_results, to_excel

print(cfg.TENANT_ID)


# def auth():
#     app = msal.PublicClientApplication(
#         client_id=cfg.CLIENT_ID,
#         authority=f"https://login.microsoftonline.com/{cfg.TENANT_ID}",
#     )
#
#     accounts = app.get_accounts()
#     chosen = accounts[0] if accounts else None
#
#     result = None
#     if chosen:
#         result = app.acquire_token_silent(
#             scopes=["User.Read"],
#             account=chosen,
#         )
#
#     if not result:
#         # interactive login via browser
#         result = app.acquire_token_interactive(
#             scopes=["User.Read"],
#         )
#
#     if "access_token" in result:
#         st.session_state["access_token"] = result["access_token"]
#         st.success(
#             f"Autenticado como {result['id_token_claims'].get('preferred_username')}"
#         )
#     else:
#         st.error(f"Error: {result.get('error')}")
#         st.warning(result.get("error_description"))
#         st.stop()
#
#
# # Run authentication at app start
# if "access_token" not in st.session_state:
#     auth()
#
# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Analisis de Madurez Mapping Tool")

st.markdown("""
Sube tus excels de **Resultados**, **Preguntas** y **Respuestas**.
Especifica una lista de los **niveles** (nombres de las hojas) a procesar.
""")

results_file = st.file_uploader("Subir Excel de Resultados", type=["xlsx"])
questions_file = st.file_uploader("Subir Excel de Preguntas", type=["xlsx"])
answers_file = st.file_uploader("Subir Excel de Respuestas", type=["xlsx"])

levels_input = st.text_input(
    "Niveles (nombres de hojas separados por coma)", value=",".join(cfg.LEVELS)
)
levels = [level.strip() for level in levels_input.split(",") if level.strip()]

# -----------------------------
# Redirect logger to Streamlit
# -----------------------------
log_container = st.empty()  # placeholder for logs
error_messages = []  # keep track of errors


class StreamlitLogger:
    def write(self, message):
        message = message.strip()
        if message:
            error_messages.append(message)
            # Display in red
            log_container.markdown(
                f"<span style='color:red'>ERROR: {message}</span>",
                unsafe_allow_html=True,
            )


logger.remove()  # remove default loguru handlers
logger.add(StreamlitLogger(), level="ERROR")  # redirect ERROR logs to Streamlit

# -----------------------------
# Button to process mapping
# -----------------------------
if st.button("Procesar Mapeo"):
    if not (results_file and questions_file and answers_file):
        st.error("Por favor sube los tres archivos de Excel.")
    elif not levels:
        st.error("Por favor especifica al menos un nivel.")
    else:
        error_messages.clear()  # reset for this run
        with st.spinner("Procesando..."):
            try:
                mapped_results = map_results(
                    levels, results_file, questions_file, answers_file
                )

                # If there were errors during mapping, stop and show messages
                if error_messages:
                    st.error(
                        "Se detectaron errores. Corrige los problemas antes de continuar."
                    )
                else:
                    excel_data = to_excel(mapped_results)
                    st.success("Mapeo completado!")

                    st.download_button(
                        label="Descargar Excel Mapeado",
                        data=excel_data,
                        file_name="resultados_mapeados.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            except Exception as e:
                logger.error(f"Error general: {e}")
