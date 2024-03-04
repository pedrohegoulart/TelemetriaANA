# Biblioteca
import logging

class Logger:
    """ Class para controle e geração de log da aplicação"""

    _instance = None # vai permitir criar somente uma instancia

    def __new__(cls, filename):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._filename = filename
            cls._instance._logger = logging.getLogger(__name__)
            cls._instance._logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Definindo um handler para escrever em um arquivo
            file_handler = logging.FileHandler(filename)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            # Adicionando o handler ao logger
            cls._instance._logger.addHandler(file_handler)
        return cls._instance

    def get_logs(self):
        # Retorna os logs do arquivo
        with open(self.filename, 'r') as f:
            return f.readlines()

    def log_info(self, msg):
        """ Seta logs do tipo INFO"""
        self._logger.info(msg)

    def log_warning(self, msg):
        """ Seta logs do tipo WARNING"""
        self._logger.warning(msg)

    def log_error(self, msg):
        """ Seta logs do tipo ERROR"""
        self._logger.error(msg)

    @property
    def filename(self):
        return self._filename
