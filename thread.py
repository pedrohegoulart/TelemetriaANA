# Bibliotecas
import time
from datetime import time
import time
import threading
from tkinter import filedialog

# Funções externas
from tkinter import *
from data import *

class Threads:
    """ Classe de criação de threads"""
    
    def __init__(self):
        self.cancel_requested_logs = False # Variavel de controle de encerramento da thread de logs
        self.cancel_requested = False # Variavel de controle de encerramento da thread da requisição (telemetry) 

    def createThreadRequest(self, root, date_init, date_end, db, logger, dataFile, barProgess, lb_log, bt_exec):
        """ Cria e inicia a thread de telemetry"""
        self.threadRequest = threading.Thread(target=self.mainTelemetry, args=(root, date_init, date_end, db, logger, dataFile, barProgess, lb_log, bt_exec))
        self.threadRequest.start()

    def createThreadLog(self, root, logger, lb_log):
        """ Cria e inicia a thread de logs no strolled"""
        self.threadLog = threading.Thread(target=self.print_logs, args=(root, logger, lb_log))
        self.threadLog.start()

    def createThreadPaste(self, path_paste):
        """ Cria e inicia a thread de seleção de pasta"""
        self.threadPaste = threading.Thread(target=self.openPaste, args=(path_paste,))
        self.threadPaste.start()

    def closeThread(self, root):
        """ Cria uma nova thread para aguardar a finalização das threads e finalização da janela e programa"""
        self.wait_thread = threading.Thread(target=self.waitForThreads, args=(root, ))
        self.wait_thread.start()

    def closeThreadRequest(self):
        """ Cria uma nova thread para aguardar a finalização das threads"""
        root = None
        self.wait_thread = threading.Thread(target=self.waitForThreads, args=(root, ))
        self.wait_thread.start()

    def waitForThreads(self, root, ):
        """ Thread para aguardar a finalização das threads """
        self.cancel_requested = True
        time.sleep(1)
        self.cancel_requested_logs = True

        threads_to_join = []

        # Verifica se a thread esta "viva" e para sua execuxão
        if hasattr(self, 'threadLog'):
            self.threadLog.do_run = False
            threads_to_join.append(self.threadLog)
        if hasattr(self, 'threadRequest'):
            self.threadRequest.do_run = False
            threads_to_join.append(self.threadRequest)
        if hasattr(self, 'threadPaste'):
            self.threadPaste.do_run = False
            threads_to_join.append(self.threadPaste)

        # Loop para fechar as threads
        for thread in threads_to_join:
            thread.join()

        # Limpa o arquivo de logs
        open(pathFilesAdd('logfile.log'), 'w').close()

        # Caso seja chamada pela função closeThread ira finalizar da janela e programa
        if root is not None:
            root.destroy()
            

    def mainTelemetry(self, root, input_date_init, input_date_end, insert_db, logger, dataFile, getProgressBar, lb_log, bt_exec):
        """ Função que faz a chamada da função de telemtria e retorna o progresso"""
        # datas de inicio e fim da extração e requisição
        data_init = input_date_init.get_date().strftime("%d/%m/%Y")
        data_end = input_date_end.get_date().strftime("%d/%m/%Y")
        
        lb_log.delete('1.0', 'end') # Limpa console
        stationTot = len(dataFile.get("estacoes", "")) # Pega as estações
        logger.log_info(f"Extração Iniciada....")

        for result in telemetry(data_init, data_end, insert_db): 
            if self.cancel_requested:  # Verifica se o cancelamento foi solicitado
                break  # Interrompe a iteração se o cancelamento foi solicitado

            # Atualiza a barra de progresso na thread principal
            root.after(0, getProgressBar, result, stationTot)
        
        bt_exec.config(state=NORMAL) # Habilita botão a executar novamente
        self.closeThreadRequest() # Finaliza as threads envolvidas na extração

    def print_logs(self, root, logger, lb_log):
        """ Função de atualização de logs no strolled"""
        self.last_position = 0 # Posição inicial no arquivo
        previous_logs = []  # Lista para armazenar os logs já inseridos

        while not self.cancel_requested_logs:
            # Abre o arquivo e pega os logs apartir da posição inicial
            with open(logger.filename, 'r') as f:
                f.seek(self.last_position)
                new_logs = f.readlines()
                root.last_position = f.tell()

            # Itera sobre os novos logs
            for log in new_logs:
                # Verifica se o log já foi inserido anteriormente
                if log not in previous_logs:
                    if 'INFO' in log:
                        lb_log.insert('end', log, 'info')
                    elif 'WARNING' in log:
                        lb_log.insert('end', log, 'warning')
                    elif 'ERROR' in log:
                        lb_log.insert('end', log, 'error')

                    # Adiciona o log à lista de logs anteriores
                    previous_logs.append(log)

            lb_log.see('end')
            time.sleep(0.5)  # Verifica a cada segundo se há novos logs

    def openPaste(self, path_paste):
        """ Função que abre a tela de seleção de pasta"""
        pasta_selecionada = filedialog.askdirectory()
        if pasta_selecionada:
            path_paste.config(text=pasta_selecionada)