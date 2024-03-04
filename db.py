# Bibliotecas
import mysql.connector

# Funções externas
from convert import *
from logger import *

# Import Logs
logger = Logger('logfile.log')

class Connect:
    """ Classe para manipular dados no banco de dados """
    _instance = None # vai permitir criar somente uma instancia
    
    def __new__(cls, host, user, password, database):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        # Permite os parametos serem alterados sem criar outra instancia
        cls._instance.host = host
        cls._instance.user = user
        cls._instance.password = password
        cls._instance.database = database
        return cls._instance

    def connectDatabase(self):
        """ Estabelece conexão com o banco  de dados"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin='mysql_native_password'
            )
            return self.connection 
        
        except mysql.connector.Error as error:
            logger.log_error(f"Erro:{error}")
            return None
        
    def disconnectDatabase(self):  
        """ Encerra a conexão com o bancp"""
        self.connection.close()

    def Insert(self, table, data, codEstacao):
        """ Realiza o insert de dados além de verificar se a tabela na qual irá inserir existe"""
        cursor = self.connection.cursor()
        try:
            # Verifica se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()

            # Verifica se a tabela existe senão existir, cria a tabela e insere os dados
            if result:
                lastDataTime = self.getLastTime(table, codEstacao)
                query = formatQuery(data, table, lastDataTime) # Montando a query de inserção completa
                if query is not None:
                    cursor.execute(query)
                    self.connection.commit()
                    logger.log_info(f"Estação: {codEstacao} inserida no Banco de dados.")
            else:
                # Se a tabela não existir, cria a tabela e insere os dados
                self.createTable(table)
                self.Insert(table, data, codEstacao)
        except mysql.connector.Error as error:
            logger.log_error(f"Erro ao inserir da estação {codEstacao} dados: {error}")
            self.connection.rollback()

    def createTable(self, table):
        """ Cria a tabela conforme os dados já estabelecidos"""
        cursor = self.connection.cursor()
        try:
            query = f"CREATE TABLE IF NOT EXISTS  {table} (CodEstacao VARCHAR(30), DataHora DATETIME, Vazao DOUBLE, Nivel DOUBLE, Chuva DOUBLE, PRIMARY KEY (CodEstacao, DataHora))"
            cursor.execute(query)
            logger.log_info(f"Tabela {table} criada com sucesso.")
        except mysql.connector.Error as error:
            logger.log_info(f"Erro ao criar tabela {table}: {error}")

    def getLastTime(self, table, codEstacao):
        """ Obtém o horário do último registro no banco de dados para uma estação específica """
        cursor = self.connection.cursor()
        try:
            sql = f"SELECT MAX(DataHora) FROM {table} WHERE CodEstacao = {codEstacao.strip('"')}"
            cursor.execute(sql)
            result = cursor.fetchone()
            last_record_time = str(result[0]) if result[0] else None
            return last_record_time
        except mysql.connector.Error as error:
            logger.log_error(f"Erro ao obter o último registro para a estação {codEstacao}: {error}")
            return None
