import streamlit as st
import plotly.express as px
import pandas as pd
import datetime as dt
from xml.dom import minidom
import requests
import time

ppis = 0
pcofins = 0

def verificar_regime(natOp: str, pis: str, cofins: str) -> str:
  pis = float(pis)
  cofins = float(cofins)

  # Formatando o valor de pis e cofins para apenas 2 casas decimais
  pis = "{:.2f}".format(pis)
  cofins = "{:.2f}".format(cofins)

  #Verificando se a nota é do modelo  DIR antes de puxar outras informações
  try:
    if(natOp=="COMPRA IMPORTAÇÃO P/ INDUSTRIALIZAÇÃO - DIR"):
      return "Importação - DIR"
    
    if(pis=='1.65' and cofins=='7.60'):
      return "Lucro Real"
    elif(pis=='0.65' and cofins=='3.00'):
      return "Lucro Presumido"
    elif(pis=='2.10' and cofins=='9.65'):
      return "Importação"
    else:
      return "Simples Nacional"
  except Exception as e:
    return f"Erro {e}"

def ler_xml(file: any) -> str:
  root = minidom.parse(file)
  # Coletando natureza da operação da nota fiscal
  natOp = root.getElementsByTagName('natOp')[0].childNodes[0].nodeValue
  # Coletando aliquota pis e cofins da nota fiscal
  try:
    ppis = root.getElementsByTagName('pPIS')[0].childNodes[0].nodeValue
    pcofins = root.getElementsByTagName('pCOFINS')[0].childNodes[0].nodeValue
  except:
    ppis = '0.00'
    pcofins = '0.00'
  regime_tributario = verificar_regime(natOp, ppis, pcofins)
  return regime_tributario

def pagina_regime():
  st.title("Verificar Regime Tributário por XML de Nota Fiscal")

  xml_file = st.file_uploader("Escolha um arquivo XML", type="xml", help="Carregue um arquivo XML para análise", accept_multiple_files=False)

  if(xml_file != None):
    st.success("Arquivo carregado com sucesso!")
    read_xml_button = st.button("Ler XML", type="primary")
    if read_xml_button:
      regime = ler_xml(xml_file)
      st.title(f"Regime Tributário: {regime}")

def buscar_cotacao(moeda: str, data: str) -> str:
  # m-d-yyyy
  data_busca = data.strftime("%m-%d-%Y")
  url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodoFechamento(codigoMoeda='{moeda}',dataInicialCotacao='{data_busca}',dataFinalCotacao='{data_busca}')?$select=cotacaoCompra"
  response = requests.get(url)
  time.sleep(1)

  if response.status_code == 200:
    dados = response.json()
    cotacao_compra = dados['value'][0]['cotacaoCompra']

    return cotacao_compra
    
def pagina_cotacao():
  
  st.title("Cotação de moedas")
  m = st.radio("Escolha a Moeda",["USD","EUR","CAD"],index=None)
  d = st.date_input("Data para verificar a cotação da moeda:", format="DD/MM/YYYY")
  d_formatado= d.strftime("%d/%m/%Y")
  
  if st.button("Buscar"):
    cotacao = buscar_cotacao(m, d)
    st.write(f"Valor da cotação na data {d_formatado}: {cotacao}")

def calcular_tempo_producao(qtd_pecas: int, colaboradores: int):
  tempo_por_peca = 415 #segundos
  horas_por_dia = 8
  segundos_por_hora = 3600

  tempo_total_segundos = qtd_pecas * tempo_por_peca
  tempo_total_segundos_colaboradores = tempo_total_segundos / colaboradores
  tempo_total_horas = tempo_total_segundos_colaboradores / segundos_por_hora
  dias_trabalho = tempo_total_horas / horas_por_dia

  return tempo_total_horas, dias_trabalho

def gerar_grafico_equipe_sipat(teams: pd.DataFrame, colaborators: pd.DataFrame):
  teams_sorted = teams.sort_values(by='Pontuação', ascending=False)
  color_map = {
    "Preto": "black",
    "Branco": "white",
    "Azul": "blue",
    "Verde": "green"
  }
  teams_plot = px.bar(
      teams_sorted,
      x="Equipe",
      y="Pontuação",
      color="Equipe",
      color_discrete_map=color_map,
      text="Pontuação"
  )

  teams_plot.update_traces(textposition="outside")
  teams_plot.update_layout(
      title="Pontuação das Equipes",
      xaxis_title="Equipe",
      yaxis_title="Pontuação",
      showlegend=False,
      bargap=0.3,
  )
  teams_plot.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))

  colaborators_sorted = colaborators.sort_values(by='Pontuação', ascending=False)
  colaborators_plot = px.bar(
      colaborators_sorted,
      x="Nome",
      y="Pontuação",
      color="Nome"
  )
  colaborators_plot.update_traces(textposition="outside")
  colaborators_plot.update_layout(
      title="Pontuação dos Colaboradores",
      xaxis_title="Colaborador",
      yaxis_title="Pontuação",
      showlegend=False,
      bargap=0.3
    )
  return teams_plot, colaborators_plot

def pagina_gerar_grafico_sipat():
  st.title("Gerar Gráfico de Equipes para SIPAT 2025")
  xlsx_file = st.file_uploader("Escolha um arquivo XLSX", type="xlsx", help="Carregue um arquivo XLSX para análise", accept_multiple_files=False)
  if(xlsx_file != None):
    st.success("Arquivo carregado com sucesso!")
    read_xlsx_button = st.button("Ler XLSX", type="primary")
    if read_xlsx_button:
      df_teams = pd.read_excel(xlsx_file, sheet_name="Equipes")
      df_colaboratos = pd.read_excel(xlsx_file, sheet_name="Colaboradores")
      plot_t, plot_c = gerar_grafico_equipe_sipat(df_teams, df_colaboratos)
      st.plotly_chart(plot_t, use_container_width=True)
      st.plotly_chart(plot_c, use_container_width=True)
  

def pagina_producao():
  st.title("Tempo Producao TKC145")

  qtd_pecas = st.number_input("Quantidade de peças:")
  qtd_colaboradoes = st.number_input("Quantidade Colaboradoes:")


  calcularTempo = st.button("Calcular tempo de produção:")

  if calcularTempo:
    horas, dias = calcular_tempo_producao(qtd_pecas, qtd_colaboradoes)
    if dias < 1:
      st.write(f"Para produzir {qtd_pecas} peças, com {qtd_colaboradoes} colaboradores, serão necessários aproximadamente: {horas:.2f} horas")
    else:
      st.write(f"Para produzir {qtd_pecas} peças, com {qtd_colaboradoes} colaboradores, serão necessários aproximadamente: {dias:.2f} dias")
paginas = {
  "Verificar Regime Tributário": pagina_regime,
  "Buscar Cotação Moeda": pagina_cotacao,
  "Tempo de Producao": pagina_producao,
  "Gerar Gráfico Sipat": pagina_gerar_grafico_sipat
}

st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.selectbox("Selecione uma página", paginas.keys())

paginas[pagina_selecionada]()