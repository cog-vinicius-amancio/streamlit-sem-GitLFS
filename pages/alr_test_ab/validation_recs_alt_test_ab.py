import streamlit as st
import pandas as pd

from pages.fathes_days_page.fathers_days import request_api_vtex


def model_alr():
    st.title("Modelo ALR - Teste A/B")

    model_type = st.sidebar.selectbox(
        "Modelo",
        ["Categorias Diferentes", "Categorias Iguais"],
    )

    if model_type == "Categorias Diferentes":
        data = pd.read_csv("pages/alr_test_ab/diff_categ.csv")
    else:
        data = pd.read_csv("pages/alr_test_ab/same_categ.csv")

    product = st.text_input("Digite o código do produto (sem cor):").upper().strip()

    recs_filtered = (
        data.loc[data["productId"].str.contains(product, case=False)]
        .sort_values("rank", ascending=True)["cd_prods_rec"]
        .unique()
    )

    st.dataframe(data.loc[data["productId"].str.contains(product, case=False)])

    if st.button("Buscar Imagens e Informações"):
        if recs_filtered.size > 0:
            st.write("Produtos recomendados:")
            for rec in recs_filtered:
                response = request_api_vtex(rec)
                if response:
                    for product in response["products"]:
                        if product["productReference"][:10] == rec:
                            st.write(f"**Nome**: {product['productName']}")
                            st.image(
                                product["items"][0]["images"][0]["imageUrl"],
                                width=200,
                            )
                            st.write(f"**Descrição**: {product['description']}")
                            st.write(
                                f"**Preço**: R$ {product['items'][0]['sellers'][0]['commertialOffer']['Price']}"
                            )
                            st.write("---" * 50)
                else:
                    st.write("Erro ao processar requisição")
        else:
            st.write("Produto não encontrado")
