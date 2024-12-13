import streamlit as st

from pages.fathes_days_page.fathers_days import fathers_day
from pages.alr_test_ab.validation_recs_alt_test_ab import model_alr
from pages.test_api.test_api_recommendations import search_recommendations
from pages.validation_recs_page.validation_recs import validation_recs

st.set_page_config(
    page_title="Aramis Testing Pages",
    page_icon=":tshirt:",
    layout="centered"
)

PAGES = {
    "Dia dos Pais": fathers_day,
    "Modelo ALR - Teste A/B": model_alr,
    "Teste API Recomendação": search_recommendations,
    "Validação de Recomendação": validation_recs
}

st.sidebar.title("Menu")

selection = st.sidebar.radio("Escolha a página:", list(PAGES.keys()))

page = PAGES[selection]
page()