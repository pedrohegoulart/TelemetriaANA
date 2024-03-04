# Bibliotecas
import socket
import xml.etree.ElementTree as ET
import re

# Funções externas
from path_utils import pathFilesAdd
from logger import *
from convert import *
from debug import *

# Import Logs
logger = Logger(pathFilesAdd('logfile.log'))

def request_xml(url):
    """ Função de requisição e tramento do returno XML"""
    try:
        # Parseando a URL
        url_parts = url.split('/')
        host = url_parts[2]
        path = '/' + '/'.join(url_parts[3:])
        
        # Criando o socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            s.connect((host, 80)) # Conectando ao servidor
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n" # Construindo a solicitação HTTP GET
            s.sendall(request.encode()) # Enviando a solicitação
            response = b"" # Inicializando a variável para armazenar a resposta
            
            # Recebendo os dados em pedaços
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            
            # Decodificando a resposta para UTF-8 e encontrando o início do corpo da resposta
            response = response.decode("utf-8")
            index = response.find("\r\n\r\n") + 4
            
            # Tratar XML
            xml_data = response[index:]
            xml_start = xml_data.find('<?xml')
            if xml_start == -1:
                return None  # XML não encontrado na resposta
            xml_data = xml_data[xml_start:]
            end_index = xml_data.rfind('</DataTable>') + len('</DataTable>')
            xml_data = xml_data[:end_index]

            #Limpeza de residuos
            xml_data = re.sub(r'\r\n[^\W_]+\r\n', '', xml_data)

            # Tente analisar o XML
            try:
                # Verifica se retornou vazio e verifica erros de conversão
                if xml_data == '<?xml versi':
                    return 0
                else:
                    return ET.fromstring(xml_data)
            except ET.ParseError as e:
                #find_invalid_token(xml_data) # Função via console que mostra linha do erro no XML
                logger.log_error(f"Erro ao analisar o XML: {e}\n URL: {url}")
                #print(f"Erro ao analisar o XML: {e}\n URL: {url}")
                #print(url)
                return None
       
        finally:
            s.close() # Fechando o socket
    
    except socket.error as e:
        logger.log_error(f"Ocorreu um erro de socket: {e}")
        return None
    except IndexError as e:
        logger.log_error(f"Ocorreu um erro de índice: {e}")
        return None


