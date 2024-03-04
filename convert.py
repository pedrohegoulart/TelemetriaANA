# Bibliotecas
import json
from datetime import datetime
import os
from path_utils import pathFilesAdd

# Import Logs
from logger import *
logger = Logger(pathFilesAdd('logfile.log'))

def str2arr(string):
    """ Converte string para vetor """
    string = string.strip("[]").replace(" ", "").replace("\n","").replace("\"","") # Remove os caracteres especiais
    elements = string.split(",") # Separa os elementos da string pela vírgula
    return elements

def arr2str(array):
    """ Converte vetor para string """
    string = json.dumps(array, ensure_ascii=False)
    string = string.replace(" ", "").replace('\\', '').replace('""', '')
    return string

def writeJson(path):
    """ Abre e carrega arquivo em JSON"""
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return data
        
    except FileNotFoundError:
        pass

def formatQuery(data, table, lastDataTime):
    """ Formata Array dados e Montando a query SQL"""
    dataQuery = []
    dataKey = []
    duplicate = False

    # Pega os nomes dos campos
    for key, value in data[0].items(): # Iterar sobre cada par chave-valor no objeto
        dataKey.append(key)
                
    # Pega e trata os valores dos campos e verificada duplicatas
    for item in data: # Iterar sobre cada objeto no array
        dataValue = []
        for key, value in item.items(): # Iterar sobre cada par chave-valor no objeto
            cleaned_value = formatDataSql(key, value.strip('" ').strip())
            
            if key == "DataHora" and lastDataTime:
                if cleaned_value <= lastDataTime: # caso seja duplicado
                    duplicate = True
                    dataValue = []
                    break

            dataValue.append(cleaned_value)

        if dataValue: # Caso esteja vazia não adiciona formatada
            dataQuery.append(f"({dataValue[0]}, '{dataValue[1]}', {dataValue[2]}, {dataValue[3]}, {dataValue[4]})")
        
    # Montando a query SQL verificando dados duplicados
    if dataQuery and not duplicate:
        columns = ', '.join(dataKey)
        values_rows = ', '.join(dataQuery)
    elif dataQuery and duplicate:
        columns = ', '.join(dataKey)
        values_rows = ', '.join(dataQuery)
        logger.log_warning("Dados PARCIALMENTE duplicados.")
    else:
        logger.log_warning("Dados COMPLETAMENTE duplicados.")
        return

    # Montando a query de inserção completa
    query = f"INSERT INTO {table} ({columns}) VALUES {values_rows}"
    return query


def formatDataSql(key, value):
    """ Formata os valores que serão inseridos no banco de dados"""
    if key == 'CodEstacao':
        return int(value.strip('" '))
    elif key == 'DataHora':
        return  str(datetime.strptime(value.strip('" '), '%Y-%m-%d %H:%M:%S'))
    elif key in ['Vazao', 'Nivel', 'Chuva']:
        if value.strip('" ') == "":
            return 'NULL'
        return float(value.strip('" '))
    else:
        return value.strip('" ')
    
def createPaste(path):
    """ Cria a pasta diaria para incluir o .csv""" 
    current_date = datetime.now().strftime("%Y-%m-%d")
    new_folder_path = os.path.join(path, current_date)
    
    try:
        # Tenta criar a pasta
        os.makedirs(new_folder_path)
        logger.log_info(f"Pasta '{current_date}' criada com sucesso")
        return new_folder_path
    
    except FileExistsError:
        # Se a pasta já existir, exibe uma mensagem informando
        logger.log_warning(f"Pasta '{current_date}' já existe")
        return new_folder_path
    
    except Exception as e:
        # Se ocorrer algum erro inesperado, exibe uma mensagem de erro
        logger.log_warning(f"Erro ao criar a pasta: {e}")
        return None


