# Telemetria ANA.GOV.BR

Este projeto tem como base simplificar a captação e tratamento de dados das Estações de Monitoramento da Agência Nacional de Águas e Saneamento Básico (ANA). É um código em Python que faz a requisição de dados via GET no [http://telemetriaws1.ana.gov.br/](http://telemetriaws1.ana.gov.br/) e realiza o tratamento, além de armazenar os dados em planilhas em Excel e no banco de dados MySQL.

## Instalação

Para executar o projeto, siga estas instruções de instalação:

1. **Instalar Python**:
   Certifique-se de ter o Python instalado em seu sistema. Você pode baixar a versão estável mais recente do Python [aqui](https://www.python.org/downloads/).

2. **Instalar o gerenciador de pacotes PIP**:
   O PIP é o gerenciador de pacotes padrão do Python. Execute o seguinte comando em seu terminal ou prompt de comando:

   ```bash
   python get-pip.py
   ```

3. **Instalar bibliotecas necessárias**:
Execute o seguinte comando para instalar as bibliotecas necessárias:

    ```bash
    pip install datetime numpy pandas mysql-connector-python tkcalendar logging pyinstaller
    ```

    Este comando instalará as seguintes bibliotecas:
    - datetime
    - numpy
    - pandas
    - mysql-connector-python
    - tkcalendar
    - logging
    - pyinstaller

    Estas bibliotecas são essenciais para:
    - Manipulação de dados
    - Conexão com banco de dados
    - Criação de interfaces gráficas
    - Geração de logs no projeto

    Certifique-se de que todas as bibliotecas estejam corretamente instaladas antes de executar o código.


4. **Criação de Executavel:**:
Execute os seguintes comandos para criar o executável em python:

Configuração de formato de data e localidade:

    ```bash
    set PYTHONIOENCODING=utf-8
    set LC_TIME=pt_BR.UTF-8
    ```
Criar executavel apartir da biblioteca PyInstaller:
    
    ```bash
    pyinstaller.exe --onefile --add-data "C:\Users\pedro\OneDrive\Documentos\GIT\TelemetriaANA\data.json;." --add-data "C:\Users\pedro\OneDrive\Documentos\GIT\TelemetriaANA\logfile.log;." --add-data "C:\Users\pedro\OneDrive\Documentos\GIT\TelemetriaANA\img/favicon.ico;img" --hidden-import babel.numbers --hidden-import tkcalendar --noconsole main.py
    ```

Substitua C:/O/Caminho/da/seu/Projeto/ pelo caminho onde estão localizados seus arquivos.