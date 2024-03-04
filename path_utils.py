import os
import sys

def pathFilesAdd(file):
    """ Retornar caminho absoluto dos arquivos adicionais de configuração e log """
    
    # Verifica se está sendo executado como um executável (.exe) ou terminal
    if sys.argv[0].endswith(".exe"):
        dir_dist = os.path.dirname(os.path.abspath(sys.executable))
        dir = os.path.dirname(dir_dist)
    else:
        dir = os.path.dirname(os.path.abspath(__file__))  # Pasta do script Python

    # Retorna caminho do arquivo
    if file == "logfile.log":
        return os.path.join(dir, "log", "logfile.log")
    elif file == "data.json":
        return os.path.join(dir, "config", "data.json")
    elif file == "favicon.ico":
        return os.path.join(dir, "img", "favicon.ico")
    else:
        pass