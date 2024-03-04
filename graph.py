# Bibliotecas
import json
import os
import time
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# TkInter
from tkinter import *
from tkcalendar import DateEntry
from tkinter.ttk import Progressbar, Notebook
from tkinter import messagebox, scrolledtext

# Funções externas
from path_utils import pathFilesAdd
from data import *
from convert import *
from db import *
from logger import *
from thread import *

# Import Logs e Threads
logger = Logger(pathFilesAdd('logfile.log'))
threads = Threads()

# Abrir arquivo de configurações
dataFile = writeJson(pathFilesAdd('data.json'))

class window:
    """Classe que apresenta a janela grafica em python"""
    def __init__(self, root):
        """Construtor: inicializa as configurações da janela grafica"""
        
        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.onClosing) 
        
        # Busca imagem do favicon
        icon_path = pathFilesAdd("favicon.ico")

        root.title("Dados Hidrometeorologicos") #Titulo da Janela
        root.iconbitmap(icon_path) #Localização do icone
        root.geometry("600x450") #Tamanho da janela

        self.createMenu(root) # Inicializa elementos apartir do menu

    
    def createMenu(self, root):
        """Cria menu de paginas (Notebook)"""    
        
        notebook = Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)  # Ajuste de espaçamento

        # Criação de paginas (frames)
        self.main = Frame(notebook, width=600, height=380)
        self.config = Frame(notebook, width=600, height=380)
        self.main.pack(fill='both', expand=True)
        self.config.pack(fill='both', expand=True)

        # add frames to notebook
        notebook.add(self.main, text='Principal')
        notebook.add(self.config, text='Configuração')

        # Adicionar elementos na pagina (Frame)
        wMain(self.main, root)
        wConfig(self.config, root)

    def onClosing(self):
        """ Evento de fechar a tela e encerrar as threads"""
        if messagebox.askokcancel("Fechar", "Tem certeza que deseja sair?"):
            messagebox.showinfo("Aviso!", "Encerrando o programa DURANTE a execução. Aguarde até a janela FECHAR")
            threads.closeThread(self.root)


class wMain:
    """ Menu Principal"""
    def __init__(self, root, mainRoot):
       
        self.root = mainRoot
        self.rootFrame = root
        self.insert_db = BooleanVar(value=True) # Habilitar insert no banco
        
        # Label do texto inicial
        lb_title = Label (root, text= "Insira os dados necessários", font = ("Arial Bold", 20), fg='blue', pady=10, padx=125)
        lb_title.grid (column = 0, row = 0, columnspan = 10)

        # Espaçamento
        lb_esp_1 = Label (root, padx=20)
        lb_esp_1.grid(column = 0, row = 2)

        # Legenda da entrada data inicio
        lb_txt_date_init = Label (root, text = "Data de ínicio:", font = ("Arial Bold", 10))
        lb_txt_date_init.grid(column = 1, row = 2)

        # Input da entrada data inicio
        self.input_date_init = DateEntry(root, selectmode='day', width=20)
        self.input_date_init.grid(column = 2, row = 2)

        # Espaçamento
        lb_esp_1 = Label (root, padx=20)
        lb_esp_1.grid(column = 3, row = 2)

        # Legenda da entrada data fim
        lb_txt_date_end = Label (root, text = "Data de Fim:", font = ("Arial Bold", 10))
        lb_txt_date_end.grid (column = 4, row = 2)

        # Input da entrada data fim
        self.input_date_end = DateEntry(root, selectmode='day', width=20)
        self.input_date_end.grid(column = 5, row = 2)

        # Espaçamento
        lb_esp_1 = Label (root, padx=20)
        lb_esp_1.grid(column = 6, row = 2)

        # Check bos para habilitar a inserção no banco de dados
        chek_db = Checkbutton(root, text='Salvar no banco de dados', var=self.insert_db, onvalue=1, offvalue=0, padx=10)
        chek_db.grid(column=0, row=3, columnspan=3)

        # Botão para cancelar a requisição
        bt_cancel = Button(root, text="Cancelar", bg="red", fg="white", width=10, pady=5, command=self.cancelBtnRequest)
        bt_cancel.grid(column=4, row=3, pady=5)

        # Botão para execução do algoritmo
        self.bt_exec = Button(root, text="Extrair Dados", bg="blue", fg="white", width=10, pady=5, command= self.requestData)
        self.bt_exec.grid(column = 5, row = 3, pady=15)

        # Label do texto inicial
        self.lb_log = scrolledtext.ScrolledText(root, bg="black", fg="white", font=("Arial Bold", 10), width = 70, height=14)
        self.lb_log.grid (column = 0, row = 5, columnspan = 10, padx=10)

        # Configuração das tags para as cores dos logs
        self.lb_log.tag_config('info', foreground='green')
        self.lb_log.tag_config('warning', foreground='orange')
        self.lb_log.tag_config('error', foreground='red')

        # Barra de progresso
        self.bar = Progressbar(root, length=510)
        self.bar.grid (column = 0, row = 6, columnspan = 10, padx=10)

    def cancelBtnRequest(self):
        """ Cancela a execução da extração e fecha as threads"""
        logger.log_info('------ Extração CANCELADA ------')
        threads.cancel_requested = True
        threads.closeThreadRequest()
        self.bar['value'] = 0 # Reseta barra de progresso
 
    def requestData(self):
        """ Inicia a execução das threads de request e log"""
        threads.cancel_requested = False
        threads.cancel_requested_logs = False
        insert_db = self.insert_db.get()

        self.bt_exec.config(state=DISABLED) # Desabilita botão a executar novamente
        self.lb_log.delete('1.0', END) # Limpa console de logs

        threads.createThreadRequest(self.root, self.input_date_init, self.input_date_end, insert_db, logger, dataFile, self.getProgressBar, self.lb_log, self.bt_exec)
        threads.createThreadLog(self.root, logger, self.lb_log)

    def getProgressBar(self, parcialEstacao, totalEstacao):
        """ Atualiza a barra de progresso da estração"""
        if threads.cancel_requested:  # Verifica se o cancelamento foi solicitado
            logger.log_info('Extração CANCELADA.')
            self.bar['value'] = 0

        value = (parcialEstacao/totalEstacao)*100

        #Incrementa a barra de progresso ou reseta ao final da extração
        if value == 100:
            time.sleep(0.5)
            self.bar['value'] = 0
        else:
            self.bar['value'] = value
            
class wConfig:
    """ Menu Configuração """
    def __init__(self, root, mainRoot):

        # Inputs
        self.entryEstacao = StringVar()
        self.entryHost = StringVar()
        self.entryUser = StringVar()
        self.entryPassword = StringVar()
        self.entryDataBase = StringVar()
        self.entryTabela = StringVar()

        # root window
        self.root = mainRoot

        # Label do texto inicial
        lb_title_cf = Label (root, text= "Dados de Configuração", font = ("Arial Bold", 20), fg='blue', pady=10, padx=125)
        lb_title_cf.grid (column = 0, row = 0, columnspan = 10)

        # Label do texto estacao
        lb_txt_estacao = Label (root, text = "Estações:", font = ("Arial Bold", 10))
        lb_txt_estacao.grid(column = 0, row = 2)

        # Input estação
        self.input_estacao = Entry(root, textvariable=self.entryEstacao, width=50)
        self.input_estacao.grid(column = 1, row = 2, columnspan=5)

        # Label do texto caminho
        lb_txt_paste = Label (root, text = "Path:", font = ("Arial Bold", 10), pady=5)
        lb_txt_paste.grid(column = 0, row = 3, padx=10)

        # Label do texto caminho do arquivo
        self.lb_path_paste = Label (root, text = "", font = ("Arial Bold", 10), width=40, bg="white")
        self.lb_path_paste.grid(column = 1, row = 3, columnspan=5, pady=5)

        # Botão de seleção de pasta
        bt_path = Button(root, text="Selecionar Pasta", command=self.select_paste, background="blue", fg="white")
        bt_path.grid(column = 6, row = 3, pady=10, padx=5)

        # -------------------- Frame borda ------------------------ #
        # Frame é um "caixa" para organizar melhor os itens graficos#
        borda_fr = Frame(root, relief=GROOVE, borderwidth=2, padx=40,pady=15)
        borda_fr.grid(row=6, column=0, columnspan=10, padx=10, pady=10)

        # Label do texto banco de dados
        lb_txt_db = Label (borda_fr, text = "Banco de dados", font = ("Arial Bold", 15), fg="blue")
        lb_txt_db.grid(column = 0, row = 0, columnspan=2, pady=10)

        # Label do texto host
        lb_txt_host = Label (borda_fr, text = "Host:", font = ("Arial Bold", 10), width=10)
        lb_txt_host.grid(column = 0, row = 1)

        #Input Host
        self.input_host = Entry(borda_fr, textvariable=self.entryHost, width=25)
        self.input_host.grid(column = 1,columnspan=2, row = 1)

        # Label do texto usuario
        lb_txt_user = Label (borda_fr, text = "User:", font = ("Arial Bold", 10), width=10)
        lb_txt_user.grid(column = 3, row = 1)

        # Input usuario
        self.input_user = Entry(borda_fr, textvariable=self.entryUser, width=25)
        self.input_user.grid(column = 4, columnspan=2, row = 1)

        # Label do texto senha
        lb_txt_password = Label (borda_fr, text = "Password:", font = ("Arial Bold", 10), width=10)
        lb_txt_password.grid(column = 0, row = 2)

        # Input senha
        self.input_password = Entry(borda_fr, textvariable=self.entryPassword, width=25)
        self.input_password.grid(column = 1, columnspan=2, row = 2)

        # Label do texto data base
        lb_txt_database = Label (borda_fr, text = "Database:", font = ("Arial Bold", 10), width=10)
        lb_txt_database.grid(column = 3, row = 2)

        # Input database
        self.input_database = Entry(borda_fr, textvariable=self.entryDataBase, width=25)
        self.input_database.grid(column = 4, columnspan=2, row = 2)

        # Label do texto tabela
        lb_txt_tabela = Label (borda_fr, text = "Tabela:", font = ("Arial Bold", 10), width=10)
        lb_txt_tabela.grid(column = 0, row = 3)

        # Input tabela
        self.input_tabela = Entry(borda_fr, textvariable=self.entryTabela, width=25)
        self.input_tabela.grid(column = 1, columnspan=2, row = 3)

        # Botão para testar conexão com o banco de dados
        bt_test_conn = Button(borda_fr, text="Testar Conexão", command=self.test_conn, pady=5, bg="green", fg="white")
        bt_test_conn.grid(column=4, row=3, pady=10)

        # Label do texto de mensagem de conexão com o banco de dados
        self.lb_txt_conn = Label (borda_fr, text = "", font = ("Arial Bold", 10))
        self.lb_txt_conn.grid(column = 0, row = 4, columnspan=10, pady=5)
        # -------------------- Frame borda (End) ------------------------- #

        # -------------------- Frame borda (Begin)------------------------ #
        button_fr = Frame(root, relief=GROOVE, padx=10,pady=5)
        button_fr.grid(row=7, column=0, columnspan=10)

        # Botão para Salvar as informações no arquivo JSON
        bt_save = Button(button_fr, text="Salvar", bg="green", fg="white", width=10, pady=5, command=self.save_data)
        bt_save.grid(column=0, row=0, padx=5)

        # Botão para Limpar as informações no arquivo JSON
        bt_reset = Button(button_fr, text="Redefinir", bg="red", fg="white", width=10, pady=5, command=self.reset_data)
        bt_reset.grid(column=1, row=0, padx=5)
        # -------------------- Frame borda (End) ------------------------- #

        self.load_data() # Carrega as informações salvas no JSON para Edição
    
    def test_conn(self):
        """ Testa conexão com o banco de dados"""
        
        # Pega as informações dentro do input de conexão
        dataHost = self.entryHost.get()
        dataUser = self.entryUser.get()
        dataPassword = self.entryPassword.get()
        dataDataBase = self.entryDataBase.get()

        # Instancia e cria a conexão com o banco de dados
        connect_instance = Connect(dataHost, dataUser, dataPassword, dataDataBase)
        connection = connect_instance.connectDatabase()

        if connection:
            logger.log_info('Conexão ao banco de dados está ativa.')
            self.lb_txt_conn.config(text="Conexão ao banco de dados está ativa.", fg="green")
        else:
            self.lb_txt_conn.config(text="Conexão ao banco de dados está inativa.", fg="red")

    def load_data(self):
        """ Pega as informações no Json e carrega nos inputs"""
        try:
            with open(pathFilesAdd('data.json'), "r") as file:

                data = json.load(file) # abre o arquivo data.json

                # Pega os valores do data.json
                dataEstacao = arr2str(data.get("estacoes", ""))
                dataPath = data.get("path", "")
                dataHost = data.get("host", "")
                dataUser = data.get("user", "")
                dataPassword = data.get("password", "")
                dataDataBase = data.get("database", "")
                dataTabela = data.get("tabela", "")

                # Seta os valores dentro dos inputs
                self.entryEstacao.set(dataEstacao)
                self.entryHost.set(dataHost)
                self.entryUser.set(dataUser)
                self.entryPassword.set(dataPassword)
                self.entryDataBase.set(dataDataBase)
                self.lb_path_paste.config(text=dataPath)
                self.entryTabela.set(dataTabela)
        
        except FileNotFoundError:
            pass

    def save_data(self):
        """ Salva as edições no arquivo JSON"""
        if messagebox.askokcancel("Fechar", "Tem certeza que deseja SALVAR as alterações?\nLembre-se de quando adicionar novos dados ou modificar salva-los!"):
            
            # Abrir o arquivo data.json para leitura
            with open(pathFilesAdd('data.json'), "r") as file:
                data = json.load(file)

            # Pega os valores do input de configuração
            data_update = {"requirements": data.get("requirements", ""),
                            "estacoes": str2arr(self.entryEstacao.get()),
                            "path": self.lb_path_paste.cget('text'),    
                            "host":    self.entryHost.get(),   
                            "user":     self.entryUser.get() ,    
                            "password": self.entryPassword.get(),    
                            "database": self.entryDataBase.get(),
                            "tabela": self.entryTabela.get()}
            
            # Atualiza o arquivo data.json
            with open(pathFilesAdd('data.json'), "w") as file:
                json.dump(data_update, file)

    def reset_data(self):
        """ Reseta e limpa as edições no arquivo JSON"""
        if messagebox.askokcancel("Fechar", "Tem certeza que deseja salvar as LIMPAR TODOS os campos?\nLembre-se de quando adicionar novos dados ou modificar salva-los!"):
            
            data = {"requirements": True,
                    "estacoes": "",
                    "path": "",    
                    "host": "",   
                    "user": "",    
                    "password": "",    
                    "database": "",
                    "tabela": ""}
            
            # Atualiza o arquivo data.json com os valores vazios
            with open(pathFilesAdd('data.json'), "w") as file:
                json.dump(data, file)

            # Limpa os inputs de configuração
            self.entryEstacao.set("")
            self.entryHost.set("")
            self.entryUser.set("")
            self.entryPassword.set("")
            self.entryDataBase.set("")
            self.entryTabela.set("")
            self.lb_path_paste.config(text="")

    def select_paste(self):
        """ Chama a função de criação das thread que ira incluir no label o caminho da pasta"""
        threads.createThreadPaste(self.lb_path_paste)
        

        

