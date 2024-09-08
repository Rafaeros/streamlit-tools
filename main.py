import streamlit as st
import datetime as dt
from xml.dom import minidom
from bs4 import BeautifulSoup
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
  
  if st.button("Buscar"):
    cotacao = buscar_cotacao(m, d)
    st.write(f"Valor da cotação na data {d.strftime("%d/%m/%Y")}: {cotacao}")

paginas = {
  "Verificar Regime Tributário": pagina_regime,
  "Buscar Cotação Moeda": pagina_cotacao
}

st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.selectbox("Selecione uma página", paginas.keys())

paginas[pagina_selecionada]()