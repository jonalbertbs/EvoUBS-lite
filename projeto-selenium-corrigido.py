
import streamlit as st 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time

st.title('Envio de mensagens Whatsapp - UBS Julia Seffer (ESF PARQUE ANI)')

# Estados globais
if 'qr_ok' not in st.session_state:
    st.session_state['qr_ok'] = False
if 'driver' not in st.session_state:
    st.session_state.driver = None
if 'dados' not in st.session_state:
    st.session_state.dados = None

# Upload do Excel
uploaded_file = st.file_uploader('Envie o arquivo Excel com os dados', type=['xlsx'])

if uploaded_file is not None and st.session_state.dados is None:
    try:
        dados = pd.read_excel(uploaded_file)
        dados.columns = dados.columns.str.strip()

        colunas_esperadas = {'nome', 'telefone', 'procedimento'}
        if not colunas_esperadas.issubset(set(dados.columns)):
            st.error('O arquivo deve conter as colunas: nome, telefone, procedimento')
        else:
            st.session_state.dados = dados
            st.success('✅ Arquivo carregado com sucesso!')
            st.dataframe(dados)

    except Exception as e:
        st.error(f'Erro ao ler o arquivo: {e}')

# Inicializa navegador
if st.session_state.dados is not None and st.session_state.driver is None:
    if st.button('Inicializar navegador e abrir WhatsApp Web'):
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            options.add_argument(r"--user-data-dir=C:\PerfilSelenium")
            options.add_argument(r"--profile-directory=Default")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get("https://web.whatsapp.com")
            st.session_state.driver = driver

            st.warning('⚠️ Escaneie o QR Code no WhatsApp Web e depois clique no botão abaixo.')

        except Exception as e:
            st.error(f'Erro ao iniciar o navegador: {e}')

# Confirmação do QR Code
if st.session_state.driver:
    if st.button('Já escaneei o QR Code'):
        st.session_state.qr_ok = True

# Envio das mensagens
if st.session_state.qr_ok:
    dados = st.session_state.dados
    driver = st.session_state.driver
    progress_bar = st.progress(0)
    total = len(dados)

    for index, linha in dados.iterrows():
        try:
            nome = linha['nome']
            telefone = ''.join(filter(str.isdigit, str(linha['telefone'])))
            telefone = f"+{telefone}"
            procedimento = linha['procedimento']

            mensagem = (f'Olá {nome}, a Unidade de Saúde do Julia Seffer informa que o procedimento '
                        f'{procedimento} foi liberado e o(a) Sr(a) tem 48 horas para retirar a documentação. (Esta é uma mensagem automática, por favor não responda...)')

            link = f'https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}'

            st.write(f'📤 Enviando mensagem para: {nome} ({telefone})')
            driver.get(link)


            #Aguarda o campo de digitação estar disponivel
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )

            # Aguarda o botão de envio estar disponivel
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Enviar"]'))
            )

            #CLica no botao de enviar
            
            botao_enviar = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
            botao_enviar.click()
            time.sleep(2) # aguarda envio


           
            
            st.success(f'✅ Mensagem enviada com sucesso: {nome}')

        except Exception as e:
            st.error(f'❌ Erro ao enviar para {nome}: {e}')

        progress_bar.progress((index + 1) / total)
        time.sleep(5)

    st.success('🎉 Todas as mensagens foram processadas com sucesso.')
    st.info("A janela do WhatsApp Web permanecerá aberta para que você possa verificar manualmente.")
