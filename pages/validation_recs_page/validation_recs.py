import streamlit as st
import pandas as pd
from typing import List
import json
import requests as req
import os

PAGE_URL = 'pages/validation_recs_page/'

def unir_csv(nomes_arquivos_origem, arquivo_destino):
    if not os.path.exists(PAGE_URL+arquivo_destino):
        dfs = [pd.read_csv(PAGE_URL+nome) for nome in nomes_arquivos_origem]
        df_concatenado = pd.concat(dfs, ignore_index=True)
        df_concatenado.to_csv(PAGE_URL+arquivo_destino, index=False)

arquivos_para_unir = []
arquivo_unido = "itens_pai_recs.csv"

unir_csv(arquivos_para_unir, arquivo_unido)

def string_to_list(string: str) -> List:
    return json.loads(string)

def optimize_dataframe(df):
    for col in df.columns:
        col_type = df[col].dtype

        if col_type == 'object':
            num_unique_values = df[col].nunique()
            num_total_values = len(df[col])
            if num_unique_values / num_total_values < 0.5:
                df[col] = df[col].astype('category')
        elif col_type.name.startswith('int'):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif col_type.name.startswith('float'):
            df[col] = pd.to_numeric(df[col], downcast='float')

    return df

def request_image(product_reference: str):
    URL = "https://aramisnova.myvtex.com/_v/api/intelligent-search/product_search/?query="

    response = req.get(URL+product_reference)
    if response.status_code == 200:
        json_response = response.json()
        if json_response['products'] and json_response['products'][0]['productReference'] == product_reference:
            image_url = json_response['products'][0]["items"][0]["images"][0]["imageUrl"]
            return image_url 
        else:
            return None
    else:
        return None

@st.cache_data 
def cached_request_image(product_id):
    return request_image(product_id)

produtos_df = optimize_dataframe(pd.read_csv(PAGE_URL+'produtos_infos.csv'))
produtos_df.set_index('cd_prod_cor', inplace=True)

itens_pai_df = optimize_dataframe(pd.read_csv(PAGE_URL+'itens_pai_recs.csv'))
print(itens_pai_df)
recommendations_dict = itens_pai_df.set_index("cd_prod_cor")["recommendations"].to_dict()
itens_pai_df = itens_pai_df.loc[itens_pai_df["IsActive"] == True]
itens_pai_df = itens_pai_df.drop(columns=["recommendations","IsActive"])

def process_row(row,num_recs):
    cd_prod_cor = row['cd_prod_cor']
    st.subheader(f"Imagem do produto {cd_prod_cor}:")
    image_url = cached_request_image(cd_prod_cor)

    col1, col2 = st.columns([1, 2])
    
    if image_url:
        with col1:
            st.image(image_url, width=300)
    else:
        st.write("Imagem não encontrada.")

    with col2:
        st.write(f"**Nome:** {row['nm_prod']}")
        st.write(f"**Grupo:** {row['ds_grupo']}")
        st.write(f"**Subgrupo:** {row['ds_subgrupo']}")
        st.write(f"**Cor:** {row['ds_cor']}")
        st.write(f"**Cor Predominante:** {row['ds_cor_predominante']}")
        st.write(f"**Modelagem:** {row['ds_modelagem']}")
        st.write(f"**Composição:** {row['ds_composicao']}")

    st.subheader(f"As imagens das {num_recs} primeiras recomendações (que foram encontradas imagens) para o produto {row['cd_prod_cor']}:")
    recs_list = string_to_list(recommendations_dict[cd_prod_cor])
    count_images_showed = 1
    for rec in recs_list:
        rec_infos = produtos_df.loc[rec['productId']]
        image_url = request_image(rec['productId'])
        if image_url:
            st.write(f'{count_images_showed}. {rec['productId']}:')

            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(image_url, width=300)

            with col2:
                st.write(f"**Nome:** {rec_infos['nm_prod']}")
                st.write(f"**Grupo:** {rec_infos['ds_grupo']}")
                st.write(f"**Subgrupo:** {rec_infos['ds_subgrupo']}")
                st.write(f"**Cor:** {rec_infos['ds_cor']}")
                st.write(f"**Cor Predominante:** {rec_infos['ds_cor_predominante']}")
                st.write(f"**Modelagem:** {rec_infos['ds_modelagem']}")
                st.write(f"**Composição:** {rec_infos['ds_composicao']}")

            count_images_showed += 1
        if count_images_showed == num_recs+1:
            break

def validation_recs():

    st.title("Página de validação de recomendações")

    if not itens_pai_df.empty:
        st.write("Selecione a página e linhas do CSV contendo os produtos, para obter as imagens das recomendações:")

        page_size = 9000  
        total_rows = len(itens_pai_df)
        total_pages = (total_rows + page_size - 1) // page_size
    
        page_number = st.number_input("Página", min_value=1, max_value=total_pages, step=1, value=1)

        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size

        st.write(f"Exibindo página {page_number} de {total_pages}")
        
        page_df = itens_pai_df.iloc[start_idx:end_idx]

        grupos_filtro_info = itens_pai_df['ds_grupo'].unique()
        subgrupo_filtro_info = itens_pai_df['ds_subgrupo'].unique()
        cor_filtro_info = itens_pai_df['ds_cor'].unique()
        cor_predominante_filtro_info = itens_pai_df['ds_cor_predominante'].unique()
        modelagem_filtro_info = itens_pai_df['ds_modelagem'].unique()
        composicao_filtro_info = itens_pai_df['ds_composicao'].unique()

        st.write("### Filtros para o CSV:")
        grupo_select = st.selectbox("Grupo: ",grupos_filtro_info,index=None)
        subgrupo_select = st.selectbox("Subgrupo: ",subgrupo_filtro_info,index=None)
        cor_select = st.selectbox("Cor: ",cor_filtro_info,index=None)
        cor_predominante_select = st.selectbox("Cor Predominante: ",cor_predominante_filtro_info,index=None)
        modelagem_select = st.selectbox("Modelagem: ",modelagem_filtro_info,index=None)
        composicao_select = st.selectbox("Composição: ",composicao_filtro_info,index=None)

        filters = {
            'ds_grupo': grupo_select,
            'ds_subgrupo': subgrupo_select,
            'ds_cor': cor_select,
            'ds_cor_predominante': cor_predominante_select,
            'ds_modelagem': modelagem_select,
            'ds_composicao': composicao_select,
        }

        filtered_page_df = page_df.copy()

        for column, value in filters.items():
            if value:
                filtered_page_df = filtered_page_df[filtered_page_df[column] == value]

        filtered_page_df = filtered_page_df.sort_values('qt_venda_tot',ascending=False)

        filtered_page_df = filtered_page_df[['qt_venda_tot','qt_venda_ecomm','estoque_ecomm','cd_prod_cor','nm_prod','ds_grupo','ds_subgrupo','ds_cor','ds_cor_predominante','ds_modelagem','ds_composicao']]

        event = st.dataframe(
            filtered_page_df,
            use_container_width=True,
            on_select="rerun",
            hide_index=True,
            selection_mode="multi-row",
        )

        st.write("### Produtos selecionados:")
        selected_rows = event.selection.rows
        page_selected_rows_df = filtered_page_df.iloc[selected_rows]

        st.dataframe(
            page_selected_rows_df,
            use_container_width=True,
            hide_index=True
        )

        num_recs = st.number_input('Número de recomendações que serão exibidas para cada produto selecionado:', min_value=1, value=5, step=1)

        if st.button("Buscar recomendações"):
            with st.spinner("Buscando recomendações..."):
                if not page_selected_rows_df.empty:
                    for _, row in page_selected_rows_df.iterrows():
                        process_row(row, num_recs)
                else:
                    st.write("Selecione algum produto.")
