import streamlit as st
from pages.validation_recs_page.validation_recs import validation_recs

st.set_page_config(
    page_title="Aramis Testing Pages",
    page_icon=":tshirt:",
    layout="centered"
)

PAGES = {
    "Validação de Recomendação": validation_recs
}

st.sidebar.title("Menu")

selection = st.sidebar.radio("Escolha a página:", list(PAGES.keys()))

page = PAGES[selection]
page()