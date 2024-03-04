# Bibliotecas
from tkinter import *
import sys
import locale

# Funções externas
from path_utils import pathFilesAdd
from graph import window

# Ajusta horario
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# Funções externas
#from install_requirements import *
#from debug import *


root = Tk()
window(root) # Cria a janela principal
root.mainloop()
# debug_info()
sys.exit() 
