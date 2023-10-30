import calendar  # Core Python Module
from datetime import datetime  # Core Python Module
import time
import pandas as pd
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh
import io

trash_icon_html = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
<style>
.trash-icon {
    font-size: 12px;
    color: red;
    cursor: pointer;
}
</style>

<div>
    <span class="trash-icon" id="trash-icon"><i class="fas fa-trash"></i></span>
</div>

<script>
document.getElementById("trash-icon").addEventListener("click", function() {
    // Use Streamlit's setQueryParams to trigger a change in the app state
    Streamlit.setQueryParams({button_clicked: true});
});
</script>
"""

# Criar um DataFrame vazio com as colunas desejadas
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

if "df_result" not in st.session_state:
    st.session_state['df_result'] = df_result = pd.DataFrame(columns=['codigo_exame', 'data', 'idade_paciente',
                                                                      'peso_paciente', 'altura_paciente',
                                                                      'imc_paciente',
                                                                      'imc_paciente_categoria', 'ctdi', 'dlp',
                                                                      'protocolo'])


def determinar_categoria_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif 18.5 <= imc < 24.9:
        return "Peso normal"
    elif 25 <= imc < 29.9:
        return "Sobrepeso"
    elif 30 <= imc < 34.9:
        return "Obesidade Grau I"
    elif 35 <= imc < 39.9:
        return "Obesidade Grau II"
    else:
        return "Obesidade Grau III"


def onAddRow(id_number, data, altura, idade_paciente, peso_paciente, ctdi, dlp, protocolo):
    imc_paciente = peso / (float(altura) * float(altura))
    # st.write(imc_paciente)

    data = pd.DataFrame({'codigo_exame': [id_number],
                         'data': [data],
                         'idade_paciente': [idade_paciente],
                         'peso_paciente': [peso_paciente],
                         'altura_paciente': [altura],
                         'imc_paciente': [imc_paciente],
                         'imc_paciente_categoria': [determinar_categoria_imc(imc_paciente)],
                         'ctdi': [float(ctdi)],
                         'dlp': [float(dlp)],
                         'protocolo': [protocolo],
                         })

    st.session_state['df_result'] = pd.concat([st.session_state['df_result'], data], ignore_index=True)


# Função para ler e processar o arquivo Excel
def process_excel_file(file):
    if file is not None:
        df = pd.read_excel(file)
        # Faça o processamento adicional do DataFrame se necessário
        st.dataframe(df)  # Exibe o DataFrame na interface


def is_valid_excel_file(file):
    if file is not None and file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return True
    return False


def formatar_data(data):
    if data is not None:
        data_formatada = data.strftime("%d/%m/%Y")
        return data_formatada
    return ""


# Função de callback para a mudança de data
def on_date_change(date):
    st.write("Data selecionada:", formatar_data(date))


# import database as db  # local import
# Definir estilo do container

def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)


def remove(df, column_name, values_to_remove):
    df_filtered = df[~df[column_name].isin(values_to_remove)]
    st.session_state['df_result'] = df_filtered


def processar_arquivo(df_result):
    output = io.BytesIO()

    if 'contagem_imc' in st.session_state:
        contagem_imc = st.session_state['contagem_imc']

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for categoria, quantidade in contagem_imc.items():
                if quantidade >= 5:
                    df_categoria = df_result[df_result['imc_paciente_categoria'] == categoria]

                    percentil_50_ctdi = df_categoria['ctdi'].quantile(0.5)
                    percentil_75_ctdi = df_categoria['ctdi'].quantile(0.75)
                    percentil_50_dlp = df_categoria['dlp'].quantile(0.5)
                    percentil_75_dlp = df_categoria['dlp'].quantile(0.75)

                    percentis = pd.DataFrame({
                        'Descrição': ['Percentil 50 - CTDI', 'Percentil 75 - CTDI', 'Percentil 50 - DLP', 'Percentil 75 - DLP'],
                        'Valor': [percentil_50_ctdi, percentil_75_ctdi, percentil_50_dlp, percentil_75_dlp]
                    })

                    sheet_name = categoria

                    df_categoria.to_excel(writer, sheet_name=f'{sheet_name}_percentis', startrow=0, index=False)
                    percentis.to_excel(writer, sheet_name=f'{sheet_name}_percentis', startrow=df_categoria.shape[0] + 5, index=False)

    output.seek(0)
    return output



# -------------- SETTINGS --------------
incomes = ["Salary", "Blog", "Other Income"]
expenses = ["Rent", "Utilities", "Groceries", "Car", "Other Expenses", "Saving"]
currency = "USD"
page_title = "Calculadora de Percentil"
page_icon = '<i class="fas fa-percentage"></i>'
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">',
            unsafe_allow_html=True)
st.markdown(
    """
    <style >
    .header {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-top: -50px;
    }
    .header h1 {
        color: #396285;
        font-size: 24px;
        margin: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

spacer = st.empty()

# Definir o conteúdo do cabeçalho
header_content = """
    <div class="header">
        <h1><i class="fas fa-percentage"></i> Calculadora de Percentil <i class="fas fa-percentage"></i> </h1>
    </div>
"""

# Mostrar o cabeçalho
spacer.markdown(header_content, unsafe_allow_html=True)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

# --- DATABASE INTERFACE ---
# Incluir o CSS personalizado para ocultar o elemento

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Processar Amostras", "Dados Inseridos"],
    icons=["pencil-fill", "bi-clipboard-data"],
    menu_icon="cast", default_index=0, orientation="horizontal"
)

# --- INPUT & SAVE PERIODS ---
if selected == "Processar Amostras":
    with st.container():
        st.markdown(
            """
            <div style="padding: 10px; border-radius: 10px;">
                <h3 style="color: #396285; margin: 0;">Insira as amostras de CTDI E DLP</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Define o conteúdo do aviso
        aviso = """
        📢 Aviso: Coleta de Dados 📊\n
        Lembrando que a categoria será incluída no processo de análise somente quando a categoria estiver com 
        pelo menos 30 amostras.
        """

        # Adiciona o aviso ao componente st.info
        st.info(aviso)
        with st.form("form_manual_data", clear_on_submit=True):

            flag_id = True
            id_input = st.text_input("Código do exame:", placeholder="Para gerar automaticamente deixe em branco",
                                     disabled=False)
            try:
                if id_input:
                    id = int(id_input)
                    flag_id = False
            except:
                lag_id = True

            col1, col2 = st.columns(2)

            with col1:

                # Receber idade, peso, altura, identificação da amostra
                # Receber uma data
                initial_date = st.date_input("Selecione uma data", value=None)

                # Receber um número de ponto flutuante para DLP
                flag_altura = True
                altura_input = st.text_input("Digite a altura do paciente ", placeholder="Insira em metros")
                try:
                    if altura_input:
                        flag_altura = float(altura_input)
                        flag_altura = False
                except:
                    flag_altura = True

                # Receber um número de ponto flutuante para DLP
                flag_dlp = True
                dlp_input = st.text_input("Digite um número de ponto flutuante para DLP ")
                try:
                    if dlp_input:
                        float_dlp = float(dlp_input)
                        flag_dlp = False
                except:
                    flag_dlp = True

            with col2:
                idade_input = st.text_input("Digite a idade do paciente: ", placeholder="Insira em anos")
                flag_idade = True
                try:
                    if idade_input:
                        idade = int(idade_input)
                        flag_idade = False
                except:
                    flag_idade = True

                # Receber idade, peso, altura, identificação da amostra
                peso_input = st.text_input("Digite o peso em Kg: ", placeholder="Insira em quilogramas")
                flag_peso = True
                try:
                    if peso_input:
                        peso = float(peso_input)
                        flag_peso = False
                except:
                    flag_peso = True

                # Receber um número de ponto flutuante para CTDI
                ctdi_input = st.text_input("Digite um número de ponto flutuante para CTDI")
                flag_ctdi = True
                try:
                    if ctdi_input:
                        float_ctdi = float(ctdi_input)
                        flag_ctdi = False
                except:
                    flag_ctdi = True

            opcao_protocolo = st.selectbox('Qual protcolo do registro?', (
                'Selecione um protocolo',
                'Crânio: Crânio cefaleia',
                'Crânio: Crânio trauma',
                'Crânio: Crânio avc',
                'Seios da Face : Sinusite',
                'Coluna Cervical',
                'Coluna Torácica',
                'Coluna Lombar',
                'Abdome total: Apendicite',
                'Abdome total: Cálculo Renal',
                'Abdome total: Dor Abdominal',
                'Abdome total: Apendicite',
                'Tórax: Câncer',
                'Tórax: Pneumonia',
                'Tórax: Covid',

            ))
            if opcao_protocolo == "Selecione um protocolo":
                flag_opcao = True
            else:
                flag_opcao = False

            # Centralizar o botão de envio usando CSS
            # Verificar se o botão de envio foi pressionado
            # Criar uma coluna centralizada
            # Defina a condição (por exemplo, valor maior que 10)
            text1 = "Abaixo do peso: 0/30"
            text2 = "Peso normal: 0/30"
            text3 = "Sobrepeso: 0/30"
            text4 = "Obesidade Grau I: 0/30"
            text5 = "Obesidade Grau II: 0/30"
            text6 = "Obesidade Grau III: 0/30"

            classe_estilo1 = "color-red"
            classe_estilo2 = "color-red"
            classe_estilo3 = "color-red"
            classe_estilo4 = "color-red"
            classe_estilo5 = "color-red"
            classe_estilo6 = "color-red"
            try:
                if 'contagem_imc' in st.session_state:
                    text1 = "Abaixo do peso: " + str(st.session_state['contagem_imc']['Abaixo do peso']) + '/30'
                if st.session_state['contagem_imc']['Abaixo do peso'] >= 5:
                    classe_estilo1 = "color-green"
            except KeyError as e:
                text1 = "Abaixo do peso: 0/30"

            try:
                if 'contagem_imc' in st.session_state:
                    text2 = "Peso normal: " + str(st.session_state['contagem_imc']['Peso normal']) + '/30'
                if st.session_state['contagem_imc']['Peso normal'] >= 30:
                    classe_estilo2 = "color-green"
            except KeyError as e:
                text2 = "Peso normal: 0/30"

            try:
                if 'contagem_imc' in st.session_state:
                    text3 = "Sobrepeso: " + str(st.session_state['contagem_imc']['Sobrepeso']) + '/30'
                if st.session_state['contagem_imc']['Sobrepeso'] >= 30:
                    classe_estilo3 = "color-green"
            except KeyError as e:
                text3 = "Sobrepeso: 0/30"

            try:
                if 'contagem_imc' in st.session_state:
                    text4 = "Obesidade Grau I: " + str(st.session_state['contagem_imc']['Obesidade Grau I']) + '/30'
                    if st.session_state['contagem_imc']['Obesidade Grau I'] >= 30:
                        classe_estilo4 = "color-green"
            except KeyError as e:
                text4 = "Obesidade Grau I: 0/30"

            try:
                if 'contagem_imc' in st.session_state:
                    text5 = "Obesidade Grau II: " + str(
                        st.session_state['contagem_imc']['Obesidade Grau II']) + '/30'
                if st.session_state['contagem_imc']['Obesidade Grau II'] >= 30:
                    classe_estilo5 = "color-green"
            except KeyError as e:
                text5 = "Obesidade Grau II: 0/30"

            try:
                if 'contagem_imc' in st.session_state:
                    text6 = "Obesidade Grau III: " + str(
                        st.session_state['contagem_imc']['Obesidade Grau III']) + '/30'
                if st.session_state['contagem_imc']['Obesidade Grau III'] >= 30:
                    classe_estilo6 = "color-green"

            except KeyError as e:
                text6 = "Obesidade Grau III: 0/30"
            st.write(f'<div class="{classe_estilo1}">{text1}</div>', unsafe_allow_html=True)
            st.write(f'<div class="{classe_estilo2}">{text2}', unsafe_allow_html=True)
            st.write(f'<div class="{classe_estilo3}">{text3}', unsafe_allow_html=True)
            st.write(f'<div class="{classe_estilo4}">{text4}', unsafe_allow_html=True)
            st.write(f'<div class="{classe_estilo5}">{text5}', unsafe_allow_html=True)
            st.write(f'<div class="{classe_estilo6}">{text6}', unsafe_allow_html=True)
            st.write(f'', unsafe_allow_html=True)
            clicked = st.form_submit_button("Adicionar dado", use_container_width=True, on_click=None)
            # Verificar se algum item atingiu 30 e habilitar o botão
            st.session_state['contagem_imc'] = st.session_state['df_result']['imc_paciente_categoria'].value_counts()
            if ('contagem_imc' in st.session_state and
                    ('Abaixo do peso' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Abaixo do peso'] >= 5) or
                    ('Peso normal' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Peso normal'] >= 30) or
                    ('Sobrepeso' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Sobrepeso'] >= 30) or
                    ('Obesidade Grau I' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Obesidade Grau I'] >= 30) or
                    ('Obesidade Grau II' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Obesidade Grau II'] >= 30) or
                    ('Obesidade Grau III' in st.session_state['contagem_imc'] and st.session_state['contagem_imc'][
                        'Obesidade Grau III'] >= 30)):

                button_relatorio = False
            else:
                button_relatorio = True


            if clicked and not (
                    flag_id or flag_idade or flag_dlp or flag_ctdi or flag_peso or flag_opcao or flag_altura):
                onAddRow(id_input, initial_date, altura_input, idade_input, peso_input, float_ctdi, dlp_input,
                         opcao_protocolo)
                st.session_state['contagem_imc'] = st.session_state['df_result'][
                    'imc_paciente_categoria'].value_counts()

            with st.container():
                st.markdown(
                    """
                    <style>
                        .color-red {
                            color: red;
                            font-family: monospace;
                            font-size: 0.9em; /* Ajuste o tamanho da fonte conforme necessário */
                            letter-spacing: -0.7px; /* Ajuste o espaçamento entre as letras conforme necessário */
                            margin-top: 0.5em;
                            margin-bottom = 2.0em;
                        }
                        .color-green {
                            color: rgb(0, 128, 0);
                            font-family: monospace;
                            font-size: 0.9em; /* Ajuste o tamanho da fonte conforme necessário */
                            letter-spacing: -0.7px; /* Ajuste o espaçamento entre as letras conforme necessário */
                            margin-top: 0.5em;
                            margin-bottom = 2.0em;
                        }
                        .color-green-w{
                            color: rgb(57, 98, 133);
                            font-family: monospace;
                            font-size: 0.9em; /* Ajuste o tamanho da fonte conforme necessário */
                            letter-spacing: -0.7px; /* Ajuste o espaçamento entre as letras conforme necessário */
                            margin-top: -0.5em;
                            margin-bottom = 2.0em;
                        }
                        .color-green-h{
                            color: rgb(57, 98, 133);
                            font-family: monospace;
                            font-size: 0.9em; /* Ajuste o tamanho da fonte conforme necessário */
                            letter-spacing: -0.7px; /* Ajuste o espaçamento entre as letras conforme necessário */
                            margin-top: 0.5em;
                            margin-bottom = 7.0em;
                        }


                        }

                    </style>
                    """,
                    unsafe_allow_html=True
                )

            # Verificar se o botão de envio foi clicado

        # Exibir o DataFrame

        if clicked and (flag_id or flag_idade or flag_dlp or flag_ctdi or flag_peso or flag_opcao or flag_altura):
            st.toast('Erro! Veirifique os dados inseridos', icon='🗣️')
        if clicked and not (flag_id or flag_idade or flag_dlp or flag_ctdi or flag_peso or flag_opcao or flag_altura):
            st.toast('Novo dado adicionado com sucesso!', icon='😍')
            time.sleep(1)
            st_autorefresh(interval=100, key="countrefresh")
    st.download_button('Download CSV', data=processar_arquivo(st.session_state['df_result']), file_name='resultados.xlsx')
# --- PLOT PERIODS ---
if selected == "Dados Inseridos":

    st.markdown(
        """
            <div style="padding: 10px; border-radius: 10px;">
                <h3 style="color: #396285; margin: 0;">Dados Inseridos</h3>
            </div>
            """,
        unsafe_allow_html=True
    )
    # Exibir o DataFrame paginado
    gb = GridOptionsBuilder.from_dataframe(st.session_state['df_result'])
    gb.configure_default_column(
        resizable=True,
    )
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=5)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    custom_css = {".ag-header-cell-text": {"font-size": "12px", 'text-overflow': 'revert;', 'font-weight': 700},
                  ".ag-theme-streamlit": {"display": "block"}}
    gb.configure_grid_options(tooltipShowDelay=0)
    gridOptions = gb.build()
    if (len(st.session_state['df_result'])) == 0:
        st.write("Nenhum dado adicionado")
    else:
        button_delete = False
        return_value = AgGrid(st.session_state['df_result'], gridOptions=gridOptions)

        if return_value['selected_rows']:
            system_name = []

            for x in range(0, len(return_value['selected_rows'])):
                system_name.append(return_value['selected_rows'][x]['codigo_exame'])
            st.write(str(len(return_value['selected_rows'])) + " dado(s) selecinado(s)")
        else:
            st.write("Sem dados selecinados")

        if 'system_name' in locals():
            button_delete = False
        else:
            button_delete = True

        if st.button('Excluir', disabled=button_delete, key='excluir_button', use_container_width=True):
            remove(st.session_state['df_result'], 'codigo_exame', system_name)
            st_autorefresh(interval=100, key="dataframerefresh")

