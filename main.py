import streamlit as st
from xml.dom import minidom

ppis = 0
pcofins = 0

#Função calcular regime tributário
def verificar_regime(pis, cofins):
  pis = float(pis)
  cofins = float(cofins)

  pis = "{:.2f}".format(pis)
  cofins = "{:.2f}".format(cofins)

  if(pis=='1.65' and cofins=='7.60'):
    return "Lucro Real"
  elif(pis=='0.65' and cofins=='3.00'):
    return "Lucro Presumido"
  elif(pis=='2.10' and cofins=='9.65'):
    return "Importação"
  else:
    return "Simples Nacional"

def ler_xml(file):
  root = minidom.parse(file)
  ppis = root.getElementsByTagName('pPIS')[0].childNodes[0].nodeValue
  pcofins = root.getElementsByTagName('pCOFINS')[0].childNodes[0].nodeValue
  regime_tributario = verificar_regime(ppis, pcofins)
  return regime_tributario

st.title("Verificar Regime Tributário por XML de Nota Fiscal")

xml_file = st.file_uploader("Escolha um arquivo XML", type="xml", help="Carregue um arquivo XML para análise", accept_multiple_files=False)

if(xml_file != None):
  st.success("Arquivo carregado com sucesso!")
  read_xml_button = st.button("Ler XML", type="primary")
  if read_xml_button:
    regime = ler_xml(xml_file)
    st.title(f"Regime Tributário: {regime}")
