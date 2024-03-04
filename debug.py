""" São um conjunto de funções que so serão utilizadas cado o programado habilite\chame no codigo
    Elas serão utilizadas para debugar o codigo somente e estão fora do escopo do projeto"""


import os
import inspect
import xml.etree.ElementTree as ET

def debug_info():
    """
    Função para imprimir informações de depuração sobre o código em execução.
    """
    # Obtém o diretório do seu projeto (onde seus arquivos de código estão localizados)
    projeto_diretorio = os.path.dirname(os.path.abspath(__file__))  # Onde __file__ é o caminho do arquivo atual
    
    # Obtém a pilha de chamadas atual
    stack = inspect.stack()
    
    # Itera sobre as chamadas na pilha
    for frame_info in stack:
        # Obtém o nome do arquivo
        file_name = frame_info.filename
        
        # Verifica se o arquivo está dentro do diretório do seu projeto
        if projeto_diretorio in file_name:
            # Obtém o nome da função e o número da linha atual
            function_name = frame_info.function
            line_number = frame_info.lineno

            # Imprime as informações de depuração
            print(f"Função: {function_name}, Linha: {line_number}, Arquivo: {file_name}")
            
            # Se a função estiver no mesmo diretório do script atual, imprime o conteúdo da linha atual
            if os.path.abspath(os.path.dirname(__file__)) == os.path.abspath(os.path.dirname(file_name)):
                with open(file_name, 'r') as f:
                    lines = f.readlines()
                    print("Código:")
                    print(lines[line_number - 1])  # -1 pois os índices de lista começam em 0
                    print()
    
    # Limpa a pilha de chamadas
    del stack

def find_invalid_token(xml_data):
    """ Função desenvolvedor para verificar erros na conversão de XML"""
    try:
        # Tente analisar o XML para encontrar o token inválido
        ET.fromstring(xml_data)
        return None, None, None  # Retorna None se não houver erro
    except ET.ParseError as e:
        
        # Se ocorrer um erro ao analisar o XML, extraia a linha e a coluna do token inválido
        error_message = str(e)
        
        # O erro normalmente está na forma "not well-formed (invalid token): line X, column Y"
        start_index = error_message.find("line ") + len("line ")
        end_index = error_message.find(",", start_index)
        line_number = int(error_message[start_index:end_index])
        start_index = error_message.find("column ") + len("column ")
        column_number = int(error_message[start_index:])
        # Encontre a posição inicial e final do trecho do XML onde o erro ocorreu
        lines = xml_data.split('\n')
        error_line = lines[line_number - 1]
        error_column = column_number
        error_text = " " * (error_column - 1) + "^"
        error_message = f"Error found at line {line_number}, column {column_number}:\n"
        error_message += f"{error_line}\n"
        error_message += f"{error_text}"
        # Printa no console a linha, a coluna e o trecho do XML com o erro
        print(line_number)
        print(column_number)
        print(error_message)  

