# Bibliotecas
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta, time
import time
import datetime

# Funções externas
from path_utils import pathFilesAdd
from convert import *
from db import *
from logger import *
from request_ import *


# Import Logs
logger = Logger(pathFilesAdd('logfile.log'))

def telemetry(data_init, data_end, sql_enabled):
    """ Função para buscar dados no servidor MG e passar para .cvs e para o banco de dados"""

    # Abrir arquivo de configurações
    data = writeJson(pathFilesAdd('data.json'))
    
    # Busca os dados no arquivo de configuração
    arrayStation = data.get("estacoes", "")
    path = data.get("path", "")
    dataHost = data.get("host", "")
    dataUser = data.get("user", "")
    dataPassword = data.get("password", "")
    dataDataBase = data.get("database", "")
    dataTable = data.get("tabela", "")

    # Instacia classe de conexão com o banco de dados
    connect_instance = Connect(dataHost, dataUser, dataPassword, dataDataBase) 
    
    # Retorna para a barra de progresso
    result = 0

    # Caso esta habilitado salvar no DB ira se conectar ao banco de dados
    if sql_enabled:
        connection = connect_instance.connectDatabase()
        if not connection:
            return None
    else:
        connection = False
    
    # Cria pasta para armazenar o csv
    pathDay = createPaste(path)
    if pathDay is None:
        logger.log_error("Erro ao criar a Pasta.")
        return
            
    for codEstacao in arrayStation:
        url = f"http://telemetriaws1.ana.gov.br//ServiceANA.asmx/DadosHidrometeorologicos?CodEstacao={codEstacao}&DataInicio={data_init}&DataFim={data_end}"
        time.sleep(0.5) # Aguarda 1 segundo antes de realizar a requisição e tratar os dados
        
        response = request_xml(url)
        if response is not None:
            dados = []
            if response != 0:
                for dado in response.findall(".//DadosHidrometereologicos"):
                    codEstacao = f'"{dado.find("CodEstacao").text}"'
                    dataHora = f'"{dado.find("DataHora").text}"'
                    vazao = (f'"{dado.find("Vazao").text}"') if dado.find("Vazao").text else '""'
                    nivel = (f'"{dado.find("Nivel").text}"') if dado.find("Nivel").text else '""'
                    chuva = (f'"{dado.find("Chuva").text}"') if dado.find("Chuva").text else '""'
                    dados.append({'CodEstacao': codEstacao, 'DataHora': dataHora, 'Vazao': vazao, 'Nivel': nivel, 'Chuva': chuva})

            # Verifica erros no XML do servidor ANA    
            if not dados:
                logger.log_warning(f"Estação: {codEstacao} esta em 'ErrorTable'")
                dados = dataErroTable(codEstacao, data_init, data_end)
            
            # Insere os dados na tabela
            if connection:
                connect_instance.Insert(dataTable, dados, codEstacao)

            # Converte em .csv 
            df = pd.DataFrame(dados)
            df.to_csv(f"{pathDay}/{codEstacao.replace('"', '')}.csv", sep=';', index=False, header=True)
            logger.log_info(f"Planilha: {codEstacao}.csv criada com sucesso")

            # Retorna informações atualizar a barra de progresso
            result += 1
            yield result
        else:
            logger.log_error('Falha na tentativa de conexão via request.')
            result += 1
            yield result

    logger.log_info("-------- Extração Concluida --------")
    if sql_enabled:
        connect_instance.disconnectDatabase() # Desconectar banco de dados

def dataErroTable(codEstacao, data_init, data_end):
    """ Função de tratamento de <Error>Sem dados para esta estação (Código: xxxxxxxx) no período solicitado!</Error>"""
    
    dados = []

    # Pega o horario atual e formata
    current_time = datetime.now()
    horas = f" {current_time.hour}:{current_time.minute}:{current_time.second}"

    # Inicio do horario e final (começando as 00:00:00 ate o dia e horario atual)
    start_datetime = datetime.strptime(data_init + " 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_datetime = datetime.strptime(data_end + horas, "%d/%m/%Y %H:%M:%S")

    # Loop para incrementar a data de 15 em 15 minutos até a data máxima
    while start_datetime <= end_datetime:
        
        dataHora = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        dados.append({
            'CodEstacao': f'"{codEstacao}"',
            'DataHora': f'"{dataHora}"',
            'Vazao': '""',
            'Nivel': '""',
            'Chuva': '""'
        })

        # Incrementa a data de 15 em 15 minutos
        start_datetime += timedelta(minutes=15)
    return dados
