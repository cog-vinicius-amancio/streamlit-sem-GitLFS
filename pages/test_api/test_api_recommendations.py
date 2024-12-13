import streamlit as st
import requests as req

from typing import Tuple

BASE_URL = "https://apimanagementrecomendacoes.azure-api.net/api/v2/products/recommendations"

MAPPER_ENDPOINTS = {
    "Aramis Recomenda": {
        "url": f"{BASE_URL}/aramis-recomenda",
        "key": "email"
    },
    "Aproveite e Leve Junto": {
        "url": f"{BASE_URL}/leve-junto",
        "key": "product"
    },
    "Você Pode Gostar": {
        "url": f"{BASE_URL}/voce-pode-gostar",
        "key": "product"
    },
    "Você Pode Gostar - B": {
        "url": f"{BASE_URL}/voce-pode-gostar-testeb",
        "key": "product"
    },
    "Produto Indisponível": {
        "url": f"{BASE_URL}/produto-indisponivel",
        "key": "product"
    }
}

def request_api(endpoint: str, key: str) -> Tuple:
    url = MAPPER_ENDPOINTS[endpoint]["url"]

    body = {
        MAPPER_ENDPOINTS[endpoint]["key"]: key
    }

    response = req.post(url, json=body)

    try:
        return response.json(), True
    except Exception:
        return response.text, False

def process_json(response: list):
    products = []

    for product in response:
        products.append({
            "id": product["VtexProduct"]["productReference"],
            "name": product["VtexProduct"]["productName"],
            "image": product["VtexProduct"]["items"][0]["images"][0]["imageUrl"],
            "link": f"https://aramis.com.br{product['VtexProduct']['link']}",
            "price_per": product["VtexProduct"]["priceRange"]["listPrice"]["highPrice"],
            "price_of": product["VtexProduct"]["priceRange"]["sellingPrice"]["highPrice"],
        })

    return products

def search_recommendations():
    st.title("Página de Teste da API de Recomendação de Aramis")

    option = st.selectbox(
        "Escolha qual endpoint deseja testar",
        ["Aramis Recomenda", "Aproveite e Leve Junto", "Você Pode Gostar", "Você Pode Gostar - B", "Produto Indisponível"],
        index=None
    )

    if option == "Aramis Recomenda":
        key = st.text_area("Digite o email para buscar as recomendações:", "")
    else:
        key = st.text_area("Digite o código do produto (sem cor) para buscar as recomendações:", "")

    if st.button("Buscar recomendações"):
        with st.spinner("Buscando recomendações..."):
            response, success = request_api(option, key)

            if success:
                products = process_json(response)

                for product in products:
                    st.write(f"**ID:** {product['id']}")
                    st.write(f"**Nome:** {product['name']}")
                    st.image(product["image"], width=300)
                    st.write(f"**Link:** {product['link']}")
                    st.write(f"**Preço de:** R$ {product['price_per']}")
                    st.write(f"**Preço por:** R$ {product['price_of']}")
                    st.write("---")
            else:
                st.error(response)

