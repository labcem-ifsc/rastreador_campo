# VERSÃO 1.2 - Última Atualização 25/07/2022
#

## @package Bibliotecas
# tkinter: biblioteca da interface do programa.\n
# matplotlib: biblioteca usada para a plotagem do mapa de calor.\n\n
# serial.tools.list_port: biblioteca usada para conexão serial.\n\n
# time: biblioteca usada para as funções delay.\n\n
# csv: biblioteca para salvar dados em arquivo csv.\n\n
# numpy: biblioteca usada para array.\n\n
# datetime: biblioteca que resgata o tempo da máquina.\n\n
# os: biblioteca que utiliza funcionalidades dependendo do sistema operacional.\n\n
# cnc_controle e analisador_controle: bibliotecas para escrita e leitura serial com grbl.
#

#Biblioteca de interface
from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
#from ttkthemes import ThemedStyle

#Biblioteca do mapa de calor
import matplotlib
import matplotlib.pyplot as plt
#from matplotlib.colors import LinearSegmentedColormap
#from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import serial.tools.list_ports   #Biblioteca de conecção serial
import time                      #Biblioteca para delay
import csv                       #Biblioteca salvar dados em arquivo csv
import numpy as np               #Biblioteca de array
from datetime import datetime, timedelta    #Biblioteca do tempo da maquina
import os


#Escrita e Leitura serial com grbl
from cnc_controle import controle_cnc
from analisador_controle import controle_analisador
from gerador_controle import controle_gerador

class main_window(Frame):
    ## @package Variáveis_de_Inicialização
    # rows,cols: Tamanho da tabela que inicia no tamanho 13-13.\n
    # rows_disp: Número de linhas apresentado na interface começando em 10.35.\n\n
    # cols_disp: Número de colunas apresentado na interface começando em 7.72.\n\n
    # var_step_x,var_step_y: São os passos do movimento para cada eixo ambos começando em 1,1.\n\n
    # flag_medindo, flag_stop: Variáveis utilizadas para mostrar se o rastreador está medindo, ou se deve ser parado.\n\n
    # flag_grade, flag_anotacao, flag_auto_maxmin: Variáveis usadas na plotagem do mapa de calor.\n\n
    # max_medido, min_medido: Variáveis que armazenam o valor máximo medido e minimo medido.
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13
    rows_disp = 10.35  # numero de linhas apresentado
    cols_disp = 7.75 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop = False, False
    flag_grade, flag_anotacao, flag_auto_maxmin= True, True, True
    max_medido, min_medido = -99, 99
    
    def __init__(self):
        """Função método chamado como um construtor na terminologia orientada a objetos
        esse método e chamado quando um objeto é criado a partir de uma classe.
        __init__(self) quando uma instância de uma subclasse é criada, o python chamará automaticamente o __init__ da classe base.
        self.serial_cnc e self.visa_analisador são definidas como None ao abrir o programa."""
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
        self.visa_analisador = None
        self.visa_gerador = None
        
    def initUI(self):
        """ Função que atribui as configurações da 'janela' do programa.
        def_font = Define a fonte usada na interface e seu tamanho.
        
        self.master.title = Nome da aba inicial da interface.
        self.frm_notebook1 = Define a aba/janela , nesse caso
        o nome da aba é "Controle Auto Scan"
        frm01 = Frame da interface que contém o menu Serial do programa.
        frm_ctrls = Frame da interface que contém os botões de movimentação
        do rastreador.
        frm_inic = Frame da interface que contém o espaço para definição
        do tamanho da matriz.
        frm_param = Frame da interface que contém os parametros das
        medidas.
        Progressbar = É a barra de progresso localizada no canto
        inferior direito da interface.
        frm_04 = Frame da interface onde está localizado o botão
        para salvar a matriz como um arquivo csv.
        frm_pont = Frame da interface onde está localizado os botões
        para marcação dos pontos 1 e 2 da matriz.
        
        self.frm_notebook2 = Define a aba/janela , nesse caso
        o nome da aba é "Mapa de Calor".
        frm_plot = Frame da interface que contém as escolhas de plot.
        frm_plot_parametro = Frame da interface que contém as escolhas
        dos possíveis tipo usados para a barra de cor.
        frm_plot_maxmin = Frame da interface que possuí as definições
        dos parametros da barra de cor.
        frm_plot_titulo = Frame da interface para definição de um
        título para o plot.
        frm_plot_interpolacao = Frame da interface que contém as
        opções de filtros para o plot.
        frm_plot_grid = Frame da interface que para definição
        do uso de grade e/ou unidade para os eixos.
        frm_plot_espelhamento = Frame da interface para definição
        do espelhamento do plot.
        frm_plot_dado = Frame da interface que possuí as opções
        de plot para o mapa de calor  
        """
        #-Altera tema da janela
        #style = ThemedStyle(self)
        #style.set_theme("black")
        #style=Style()
        #print(style.theme_names())
        #style.theme_use("black")
        
        #-Altera todas as fontes
        def_font = font.nametofont("TkDefaultFont")
        def_font.config(size=9)
        
        #---nome da janela---------------------
        self.master.title('Controle Auto Scan')#futuro nome?
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
        #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
                #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
        frm_01 = Labelframe(self.frm_notebook1, text='Serial')
        frm_01.place(x=10,y=1,width=440,height=95)
        
        #---configuração da linha/coluna------
        frm_01.columnconfigure(0, pad=3)
        frm_01.columnconfigure(1, pad=3)
        frm_01.rowconfigure(0, pad=3)
        frm_01.rowconfigure(1, pad=3)
        frm_01.rowconfigure(2, pad=3)
        frm_01.rowconfigure(3, pad=3)
        frm_01.rowconfigure(4, pad=3)
        
        #---configuração linha analisador-----
        lbl_01 = Label(frm_01, text='Analisador:')
        lbl_01.place(x=5,y=3,width=90,height=20)
        
        self.cmb_analisador = Combobox(frm_01)
        self.cmb_analisador.place(x=73,y=2,width=185,height=23)
        
        self.btn_open_analisador = Button(frm_01, text='Abrir')
        self.btn_open_analisador.place(x=267,y=1,width=80,height=25)
        self.btn_open_analisador['command'] = self.abrir_visa_analisador
        
        #---Atualização de ports-----------
        btn_refresh = Button(frm_01, text='Atualizar')
        btn_refresh.place(x=353,y=12,width=75,height=53)
        btn_refresh['command'] = self.lista_serial
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.place(x=5,y=30,width=90,height=20)

        self.cmb_cnc = Combobox(frm_01, width=27)
        #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
        frm_01 = Labelframe(self.frm_notebook1, text='Serial')
        frm_01.place(x=10,y=1,width=440,height=95)
        
        #---configuração da linha/coluna------
        frm_01.columnconfigure(0, pad=3)
        frm_01.columnconfigure(1, pad=3)
        frm_01.rowconfigure(0, pad=3)
        frm_01.rowconfigure(1, pad=3)
        frm_01.rowconfigure(2, pad=3)
        frm_01.rowconfigure(3, pad=3)
        frm_01.rowconfigure(4, pad=3)
        
        #---configuração linha analisador-----
        lbl_01 = Label(frm_01, text='Analisador:')
        lbl_01.place(x=5,y=3,width=90,height=20)
        
        self.cmb_analisador = Combobox(frm_01)
        self.cmb_analisador.place(x=73,y=2,width=185,height=23)
        
        self.btn_open_analisador = Button(frm_01, text='Abrir')
        self.btn_open_analisador.place(x=267,y=1,width=80,height=25)
        self.btn_open_analisador['command'] = self.abrir_visa_analisador
        
        #---Atualização de ports-----------
        btn_refresh = Button(frm_01, text='Atualizar')
        btn_refresh.place(x=353,y=12,width=75,height=53)
        btn_refresh['command'] = self.lista_serial
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.place(x=5,y=30,width=90,height=20)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.place(x=73,y=29,width=185,height=23)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.place(x=267,y=27,width=80,height=25)
        self.btn_open_cnc['command'] = self.abrir_serial_cnc
        
        #---Configuração linha gerador-----
        lbl_03 = Label(frm_01, text='Gerador:')
        lbl_03.place(x=5,y=55,width=90,height=20)

        self.cmb_cnc.place(x=73,y=29,width=185,height=23)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.place(x=267,y=27,width=80,height=25)
        self.btn_open_cnc['command'] = self.abrir_serial_cnc
        
        #---Configuração linha gerador-----
        lbl_03 = Label(frm_01, text='Gerador:')
        lbl_03.place(x=5,y=55,width=90,height=20)

        self.cmb_gerador = Combobox(frm_01, width=27)
        self.cmb_gerador.place(x=73,y=55,width=185,height=20)
        
        self.btn_open_gerador = Button(frm_01, text='Abrir')
        self.btn_open_gerador.place(x=267,y=52,width=80,height=24)
        self.btn_open_gerador['command'] = self.abrir_visa_gerador
    
        
        #---nome do frame---------------------
        frm_ctrls = Labelframe(self.frm_notebook1, text='Controle')
        frm_ctrls.place(x=10,y=445,width=440,height=240)
        
        #---configuração da linha/coluna------
        frm_ctrls.columnconfigure(0, pad=3)
        frm_ctrls.columnconfigure(1, pad=3)
        frm_ctrls.columnconfigure(2, pad=3)
        frm_ctrls.columnconfigure(3, pad=3)
        frm_ctrls.columnconfigure(4, pad=3)
        
        frm_ctrls.rowconfigure(0, pad=3)
        frm_ctrls.rowconfigure(1, pad=3)
        frm_ctrls.rowconfigure(2, pad=3)
        frm_ctrls.rowconfigure(3, pad=3)
        frm_ctrls.rowconfigure(3, pad=7)
        frm_ctrls.rowconfigure(4, pad=7)
        
        #---escrita XYZ---------------------
        lbl_03 = Label(frm_ctrls, text='Y:')
        lbl_03.grid(row=0, column=2)
        
        lbl_04 = Label(frm_ctrls, text='   X:')
        lbl_04.grid(row=2, column=0)
        
        lbl_05 = Label(frm_ctrls, text='Z:')
        lbl_05.grid(row=0, column=4)
        
        #---botão de home------------------
        btn_home = Button(frm_ctrls, text= 'Origem')
        btn_home.place(x=343,y=23,width=70,height=83)
        btn_home['command'] = self.vai_origem
        
        #---configuração linhas------------   
        # Primeira linha
        btn_dig_no = Button(frm_ctrls, text=u'\u25F8')
        btn_dig_no.grid(row=1, column=1)
        
        btn_up = Button(frm_ctrls, text= u'\u25B2')
        btn_up.grid(row=1, column=2)
        btn_up['command'] = lambda direcao=self.dict_jog['up'] : self.ctrl_movimento_cnc(direcao)      
        
        btn_dig_ne = Button(frm_ctrls, text=u'\u25F9')
        btn_dig_ne.grid(row=1, column=3)
        
        btn_z_up_btn = Button(frm_ctrls, text= u'\u25B2')
        btn_z_up_btn.grid(row=1, column=4)
        btn_z_up_btn['command'] = lambda direcao=self.dict_jog['z_up'] : self.ctrl_movimento_cnc(direcao)
        
        # Segunda linha
        btn_left_btn = Button(frm_ctrls, text=u'\u25C0')
        btn_left_btn.grid(row=2, column=1)
        btn_left_btn['command'] = lambda direcao=self.dict_jog['left'] : self.ctrl_movimento_cnc(direcao)
        
        btn_home_btn = Button(frm_ctrls, text=u'\u25EF')
        btn_home_btn.grid(row=2, column=2)
        
        btn_right_btn = Button(frm_ctrls, text=u'\u25B6')
        btn_right_btn.grid(row=2, column=3)
        btn_right_btn['command'] = lambda direcao=self.dict_jog['right'] : self.ctrl_movimento_cnc(direcao)
        
        # Terceira linha       
        btn_diag_so = Button(frm_ctrls, text=u'\u25FA')
        btn_diag_so.place(x=27,y=81,width=75,height=26)
        
        btn_down = Button(frm_ctrls, text=u'\u25BC')
        btn_down.place(x=106,y=81,width=75,height=26)
        btn_down['command'] = lambda direcao=self.dict_jog['down'] : self.ctrl_movimento_cnc(direcao)
        
        btn_diag_se = Button(frm_ctrls, text=u'\u25FF')
        btn_diag_se.place(x=185,y=81,width=75,height=26)
                
        btn_z_down = Button(frm_ctrls, text=u'\u25BC')
        btn_z_down.place(x=264,y=81,width=75,height=26)
        btn_z_down['command'] = lambda direcao=self.dict_jog['z_down'] : self.ctrl_movimento_cnc(direcao)

        self.cmb_step = Combobox(frm_ctrls, width=5)# Janela de seleção do tamanho de passo
        self.cmb_step.grid(row=2, column=4)
        self.cmb_step['values'] = ['2','1','0.5','0.1']
        self.cmb_step.current(1)       
        
        ################# LOG DESATIVADO #################
        
        lbl_06 = Labelframe(frm_ctrls, text='Log:')
#       lbl_06.place(x=10,y=120,width=415,height=50)
                
        self.txt_log = scrolledtext.ScrolledText(lbl_06, width=48, height=9)
#        self.txt_log.place(x=1,y=1)
        
#        lbl_07 = Label(frm_ctrls, text='Comando:')
#        lbl_07.place(x=10,y=195,width=60,height=20)
         
#        self.ent_cmd = Entry(frm_ctrls, width=25)
#        self.ent_cmd.place(x=80,y=195,width=294,height=20)       
#        self.ent_cmd.bind('<Return>', self.comp_s)
         
#        self.btn_send_cmd = Button(frm_ctrls, text='Enviar')
#        self.btn_send_cmd.place(x=376,y=195,width=50,height=22)  
#        self.btn_send_cmd['command'] = self.envia_cmd_cnc
        
        ################# LOG DESATIVADO #################
        #---nome do frame---------------------
        frm_inic = Labelframe(self.frm_notebook1, text='Tamanho Matriz')
        frm_inic.place(x=10,y=95,width=215,height=75)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        frm_inic.rowconfigure(1, pad=3)
        
        #---valores da matriz-----------------
        lbl_08 = Label(frm_inic, text='X :')
        lbl_08.grid(row=0, column=0)
        
        self.var_matriz_x=Entry(frm_inic, width=12)
        self.var_matriz_x.insert(END, '%d' % self.rows)
        self.var_matriz_x.grid(row=0, column=1)
        
        lbl_9 = Label(frm_inic, text='Y :')
        lbl_9.grid(row=0, column=2)
        
        self.var_matriz_y=Entry(frm_inic, width=12)
        self.var_matriz_y.insert(END, '%d' % self.cols)
        self.var_matriz_y.grid(row=0, column=3)
        
        #---botão de atualizar----------------
        btn_matriz_refresh = Button(frm_inic, text='Atualizar')
        btn_matriz_refresh.place(x=20,y=25,width=181,height=25)
        btn_matriz_refresh['command'] = self.att_matriz
        
        #---nome do frame---------------------
        frm_param = Labelframe(self.frm_notebook1, text='Parametros')
        frm_param.place(x=235,y=95,width=215,height=215)
        
        frm_param.columnconfigure(0, pad=3)
        frm_param.columnconfigure(1, pad=3)
        
        frm_param.rowconfigure(0, pad=3)
        frm_param.rowconfigure(1, pad=3)
        frm_param.rowconfigure(2, pad=3)
        frm_param.rowconfigure(3, pad=3)
        frm_param.rowconfigure(4, pad=3)
        frm_param.rowconfigure(5, pad=3)
        frm_param.rowconfigure(6, pad=3)
        
        lbl_par_1 = Label(frm_param, text='Posição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Posição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (cm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (cm):')
        lbl_par_9 = Label(frm_param, text='Maior valor medido:')
        lbl_par_10 = Label(frm_param, text='Menor valor medido:')
        lbl_par_15 = Label(frm_param, text='Abrir arquivo CSV:')
        self.lbl_par_5 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_6 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        self.lbl_par_11 = Label(frm_param, text='-99,00')
        self.lbl_par_12 = Label(frm_param, text='-99,00')
        
        lbl_par_1.grid(row=0, column=0, sticky=W)
        lbl_par_2.grid(row=1, column=0, sticky=W)
        lbl_par_3.grid(row=2, column=0, sticky=W)
        lbl_par_4.grid(row=3, column=0, sticky=W)
        self.lbl_par_5.grid(row=0, column=1, sticky=E)
        self.lbl_par_6.grid(row=1, column=1, sticky=E)
        self.lbl_par_7.grid(row=2, column=1, sticky=E)
        self.lbl_par_8.grid(row=3, column=1, sticky=E)
        lbl_par_9.grid(row=4, column=0, sticky=W)
        lbl_par_10.grid(row=5, column=0, sticky=W)
        lbl_par_15.grid(row=6, column=0, sticky=W) #Yuri
        self.lbl_par_11.grid(row=4, column=1, sticky=E)
        self.lbl_par_12.grid(row=5, column=1, sticky=E)
        
        #---botão de abrir arquivo CSV Yuri----------------
        btn_csv_abrir = Button(frm_param, text='Abrir')
        btn_csv_abrir.place(x=20,y=155,width=181,height=25)
        btn_csv_abrir['command'] = self.info_arquivocsv
        
        #---nome do frame---------------------
        frm_progress = Labelframe(self.frm_notebook1)
        frm_progress.place(x=460,y=640,width=608,height=45)
        
        #---tempo de progresso----------------
        self.lbl_10 = Label(frm_progress, text='Tempo estimado de '+'HH'+' : '+'MM'+' : '+'SS')
        self.lbl_10.place(x=10,y=0,width=300,height=20)
        
        #---barra de progresso----------------
        self.var_pb=DoubleVar()
        self.var_pb.set(1)
        
        pb=Progressbar(frm_progress,variable=self.var_pb,maximum=100)
        pb.place(x=200,y=0,width=397,height=20)
        
        #---nome do frame---------------------
        frm_04 = Labelframe(self.frm_notebook1, text='Arquivo')
        frm_04.place(x=460,y=1,width=608,height=47)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        
        lbl_11 = Label(frm_04, text='  Nome do Arquivo:  ')
        lbl_11.grid(row=0, column=0)
        
        self.str_save = Entry(frm_04, width=41)
        self.str_save.grid(row=0, column=1)
        
        lbl_12 = Label(frm_04, text=' _dd-mm-yyyy_HH-MM.csv ')
        lbl_12.grid(row=0, column=2)
        
        btn_save = Button(frm_04, text='Salvar')
        btn_save.grid(row=0,column=3)
        btn_save['command'] = self.save
        
        #---nome do frame---------------------
        frm_pont = Labelframe(self.frm_notebook1, text='Definição dos pontos')
        frm_pont.place(x=10,y=165,width=215,height=65)
        
        btn_pont_start = Button(frm_pont, text='Ponto 1')
        btn_pont_start.place(x=5,y=1,width=100,height=40)
        btn_pont_start['command'] = self.start_point
        
        btn_pont_end = Button(frm_pont, text='Ponto 2')
        btn_pont_end.place(x=110,y=1,width=95,height=40)
        btn_pont_end['command'] = self.end_point
        
        #---nome do frame---------------------
        frm_freq = Labelframe(self.frm_notebook1, text='Frequência')
        frm_freq.place(x=10,y=230,width=215,height=75)
        
        frm_freq.columnconfigure(0, pad=3)
        frm_freq.columnconfigure(1, pad=3)
        frm_freq.columnconfigure(2, pad=3)
        
        frm_freq.rowconfigure(0, pad=3)
        frm_freq.rowconfigure(1, pad=3)
            
        #---valores da matriz-----------------
        lbl_08 = Label(frm_freq, text='Frequência:')
        lbl_08.place(x=5,y=3,width=90,height=20)
        
        self.var_freq=Entry(frm_freq)
        self.var_freq.insert(END, '%d' % 25)
        self.var_freq.place(x=73,y=3,width=63,height=20)
        
        self.cmb_freq = Combobox(frm_freq)
        self.cmb_freq.place(x=143,y=3,width=60,height=20)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq['state'] = 'readonly'
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.place(x=72,y=27,width=132,height=25)
        self.btn_freq_refresh['command'] = self.att_freq
        
        
        
        #---Frame do gerador----------------
        frm_gerador = Labelframe(self.frm_notebook1, text='Gerador')
        frm_gerador.place(x=10, y=300,width=440,height=90)
        
        lbl_vamp = Label(frm_gerador, text='Amplitude :')
        lbl_vamp.grid(row=0, column=0)
                
        self.vamp=Entry(frm_gerador, width=12)
        self.vamp.insert(END, '%d' % 18)
        self.vamp.grid(row=0, column=1)
        
        self.vamp_gerador_mag = Combobox(frm_gerador)
        self.vamp_gerador_mag.place(x=160,y=0,width=60,height=21)
        self.vamp_gerador_mag['values'] = ['mV', 'V']
        self.vamp_gerador_mag['state'] = 'readonly'
        self.vamp_gerador_mag.current(1)
        
        
        lbl_freq = Label(frm_gerador, text='Frequência :')
        lbl_freq.grid(row=1, column=0)
        
        self.freq_gerador=Entry(frm_gerador, width=12)
        self.freq_gerador.insert(END, '%d' % 25)
        self.freq_gerador.grid(row=1, column=1)
        
        self.freq_gerador_mag = Combobox(frm_gerador)
        self.freq_gerador_mag.place(x=160,y=20,width=60,height=21)
        self.freq_gerador_mag['values'] = ['KHz','MHz']        
        self.freq_gerador_mag['state'] = 'readonly'
        self.freq_gerador_mag.current(1)
        
        
        lbl_imp = Label(frm_gerador, text='Impedância :')
        lbl_imp.grid(row=2, column=0)
        
        self.imp=Entry(frm_gerador, width=12)
        self.imp.insert(END, '%d' %470)
        self.imp.grid(row=2, column=1)

        self.imp_gerador = Combobox(frm_gerador)
        self.imp_gerador.place(x=160,y=40,width=60,height=23)
        self.imp_gerador['values'] = ['Ω', 'KΩ']
        self.imp_gerador['state'] = 'readonly'
        self.imp_gerador.current(0)
        
        
#         btn_channel = Button(frm_gerador, text='Ligar Canal')
#         btn_channel.place(x=235, y=0, width=75, height=30)
#         lbl_channel = Label(frm_gerador, text ='Canal desligado!')
#         lbl_channel.place(x=315, y=0, width=100, heigh=30)
        
                
        btn_att_ger = Button(frm_gerador, text='Atualizar')
        btn_att_ger.place(x=235, y=17, width=75, height=30)
        btn_att_ger['command'] = self.att_ger
        
        
        #-Botões de atuação medição
        btn_stop = Button(self.frm_notebook1, text='Abortar Medição')
        btn_stop.place(x=235,y=400,width=216,height=40)
        btn_stop['command'] = self.stop_meas
        
        btn_start = Button(self.frm_notebook1, text='Iniciar Medição')
        btn_start.place(x=10,y=400,width=217,height=40)
        btn_start['command'] = self.medicao
        
        #-Notebook ed plotagem
        self.frm_notebook2 = Frame(notebook)
        self.frm_notebook2.pack(fill=BOTH, expand=True)
        notebook.add(self.frm_notebook2, text='      Mapa de calor      ')
        
        #--Parametros de plotagem
        frm_plot = Labelframe(self.frm_notebook2, text='Escolhas para plot')
        frm_plot.place(x=10,y=5,width=240,height=680)  
        
        #---Label frame da barra de cor
        frm_plot_parametro = Labelframe(frm_plot, text='Barra de cor')
        frm_plot_parametro.place(x=5,y=1,width=225,height=150)
        
        #----Definição de parametros da barra de cor
        frm_plot_maxmin = Labelframe(frm_plot_parametro, text='Entrada manual:')
        frm_plot_maxmin.place(x=5,y=0,width=212,height=47)
        
        lbl_21 = Label(frm_plot_maxmin, text='MAX. :')
        lbl_21.place(x=5,y=5,width=60,height=20)
        self.var_plot_max=Entry(frm_plot_maxmin, width=8)
        self.var_plot_max.insert(END, '%d' % 10)
        self.var_plot_max.place(x=45,y=3,width=57,height=20)
        self.var_plot_max['state'] = 'disable'
        
        lbl_22 = Label(frm_plot_maxmin, text='MIN. :')
        lbl_22.place(x=110,y=5,width=60,height=20)
        self.var_plot_min=Entry(frm_plot_maxmin, width=8)
        self.var_plot_min.insert(END, '%d' % -80)
        self.var_plot_min.place(x=145,y=3,width=57,height=20)
        self.var_plot_min['state'] = 'disable'
        
        lbl_ou = Label(frm_plot_parametro, text=' OU')
        lbl_ou.place(x=95,y=47,width=30,height=15)
        
        self.btn_plt_maxmin = Button(frm_plot_parametro, text='MAX/MIN automático HABILITADO')
        self.btn_plt_maxmin.place(x=5,y=65,width=213,height=34)
        self.btn_plt_maxmin['command'] = self.plot_auto_maxmin
        
        #----Combo box escolha de cor
        lbl_21 = Label(frm_plot_parametro, text='Tabela de COR: ')
        lbl_21.place(x=5,y=105,width=85,height=20)
        self.cmb_plot_cor = Combobox(frm_plot_parametro, width=5)# Janela de seleção do tamanho de passo
        self.cmb_plot_cor.place(x=94,y=105,width=123,height=20)
        self.cmb_plot_cor['values'] = ['inferno','viridis','gist_heat','hot']
        self.cmb_plot_cor.current(0) 
        
        
        #---Titulo do plot
        frm_plot_titulo = Labelframe(frm_plot, text='Título')
        frm_plot_titulo.place(x=5,y=153,width=225,height=72)
        
        lbl_22 = Label(frm_plot_titulo, text=' Título do plot :')
        lbl_22.grid(row=0, column=0, padx= 3)
        self.var_plot_titulo=Entry(frm_plot_titulo, width=80)
        self.var_plot_titulo.insert(END, 'nome_exemplo')
        self.var_plot_titulo.place(x=5,y=25,width=210,height=20)
        
        #---Filtro no plot
        frm_plot_interpolacao = Labelframe(frm_plot, text='Filtro')
        frm_plot_interpolacao.place(x=5,y=230,width=225,height=49)
        
        lbl_24 = Label(frm_plot_interpolacao, text=' Interpolação :')
        lbl_24.place(x=5,y=5,width=78,height=20)
        
        self.cmb_plot_interpolacao = Combobox(frm_plot_interpolacao, width=17)#janela de escolha interpolacao
        self.cmb_plot_interpolacao.place(x=90,y=2,width=125,height=23)
        self.cmb_plot_interpolacao['values'] = ['none','spline16','catrom','gaussian','sinc']
        self.cmb_plot_interpolacao.current(3)
        
        #---Habilitar grid
        frm_plot_grid = Labelframe(frm_plot, text='Grade')
        frm_plot_grid.place(x=5,y=281,width=107,height=67)
        
        self.btn_plt_grade = Button(frm_plot_grid, text='      Grade\nHABILITADO')
        self.btn_plt_grade.place(x=5,y=1,width=93,height=40)
        self.btn_plt_grade['command'] = self.plot_grade
        
        #---Habilitar label
        frm_plot_grid = Labelframe(frm_plot, text='Unidade eixos')
        frm_plot_grid.place(x=123,y=281,width=107,height=67)
        
        self.btn_plt_anotacao = Button(frm_plot_grid, text='   Unidade\nHABILITADO')
        self.btn_plt_anotacao.place(x=5,y=1,width=93,height=40)
        self.btn_plt_anotacao['command'] = self.plot_anotacao
        
        frm_plot_espelhamento = Labelframe(frm_plot, text='Espelhamento dos eixos')
        frm_plot_espelhamento.place(x=5,y=350,width=225,height=55)
        
        self.var_espelhamento_x = IntVar(value = 0)
        self.chk_espelhamento_x = Checkbutton(frm_plot_espelhamento, text='Eixo X', var=self.var_espelhamento_x) 
        self.chk_espelhamento_x.place(x=45,y=5,width=70,height=25)
        
        self.var_espelhamento_y = IntVar(value = 0)
        self.chk_espelhamento_y = Checkbutton(frm_plot_espelhamento, text='Eixo Y', var=self.var_espelhamento_y)
        self.chk_espelhamento_y.place(x=120,y=5,width=70,height=25)
        
        #---Qual dado ser plotado
        frm_plot_dado = Labelframe(frm_plot, text='Dado plot')
        frm_plot_dado.place(x=5,y=407,width=225,height=200)
        
        #----Botões de escolha de dados
        lbl_23 = Label(frm_plot_dado, text='Escolha qual dos dados :')
        lbl_23.place(x=5,y=1,width=200,height=20)
        
        btn_plt_dado_atual = Button(frm_plot_dado, text='Dados da medida\n         ATUAL')
        btn_plt_dado_atual.place(x=5,y=25,width=210,height=40)
        btn_plt_dado_atual['command'] = self.plot_dadoatual
        
        lbl_23 = Label(frm_plot_dado, text='OU')
        lbl_23.place(x=97,y=67,width=20,height=16)
        
        lbl_24 = Labelframe(frm_plot_dado)
        lbl_24.place(x=5,y=81,width=210,height=92)
        
        btn_plt_dado_arquivo = Button(lbl_24, text='Dados do arquivo\n           CSV')
        btn_plt_dado_arquivo.place(x=5,y=1,width=195,height=40)
        btn_plt_dado_arquivo['command'] = self.plot_arquivo_csv
        
        lbl_25 = Label(lbl_24, text='Tamanho(cm) X:')
        lbl_25.place(x=5,y=45,width=91,height=20)
        self.var_plot_tamanho_x=Entry(lbl_24, width=80)
        self.var_plot_tamanho_x.insert(END, 12)
        self.var_plot_tamanho_x.place(x=99,y=45,width=40,height=20)
        
        lbl_26 = Label(lbl_24, text='Y:')
        lbl_26.place(x=143,y=45,width=30,height=20)
        self.var_plot_tamanho_y=Entry(lbl_24, width=80)
        self.var_plot_tamanho_y.insert(END, 12)
        self.var_plot_tamanho_y.place(x=159,y=45,width=40,height=20)
        
        btn_plt_salvar = Button(frm_plot, text=' Salvar último\nMapa de Calor')
        btn_plt_salvar.place(x=5,y=615,width=225,height=40)
        btn_plt_salvar['command'] = self.plot_salva
        
        #--Apresentação do mapa de calor
        self.frm_heatmap = Labelframe(self.frm_notebook2, text='Mapa de calor')
        self.frm_heatmap.place(x=260,y=5,width=805,height=680)
        
        #Constantes e inicializações
        self.lista_serial()
        self.att_matriz()

        
    #Função para atualizar lista das portas COM
    def lista_serial(self):
        """ Função utilizada para atualizar os aparelhos conectados via USB nas
        portas COM do computador.
        
        portas = Recebe a lista de portas conectadas ao computador
        self.cmb_analisador['values'] = Recebe as possíveis portas
        conectadas ao computador.
        self.cmb_analisador.set('Escolha...') = Por default escreve
        no campo em branco "Escolha". """
        portas=controle_cnc.list_serial()
        
        self.cmb_analisador['values'] = portas
        self.cmb_analisador.set('Escolha...')
        
        self.cmb_cnc['values'] = portas
        self.cmb_cnc.set('Escolha...')
        
        self.cmb_gerador['values'] = portas
        self.cmb_gerador.set('Escolha...')

    #Função para iniciar comunicação com analisador
    def abrir_visa_analisador(self):
        """Função que inicializa a comunicação com o analisador de espectro.
        if (self.verifica_medicao()) = Verifica se uma medição está ativa,
        se tiver a função para.
        com_port =  self.cmb_analisador.get() = Procura por uma conexão
        ao analisador
        self.visa_analisador=controle_analisador.open_visa_analisador(com_port, self.visa_analisador)
        Chama as funções relacionadas a comunicação entre o computador e o analisador.
        if(self.visa_analisador==None): = Se true vai escrever no botão da interface "abrir".
        se falso vai escrever "fechar".
        self.att_freq() = Chama a função de atualizar a frequência do analisador.
        """
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_analisador.get()
        self.visa_analisador=controle_analisador.open_visa_analisador(com_port, self.visa_analisador)
        
        if(self.visa_analisador==None):
            self.btn_open_analisador['text'] = 'Abrir'
        else:
            self.btn_open_analisador['text'] = 'Fechar'
        self.att_freq()
    
    #Função leitura amplitude do analisador
    def leitura_amplitude(self):
        """Função que retorna o valor lido da amplitude feita pelo analisador de espectro."""
        #futuro ... integração com o novo analisador
        return controle_analisador.receiver_amplitude(self.visa_analisador)
        
    #Função para abrir porta serial da CNC
    def abrir_serial_cnc(self):
        """Função que abre a porta serial da CNC para comunicação.
        Verifica se uma medição já está acontecendo, caso sim, não faz nada.
        com_port =  self.cmb_cnc.get() = Recebe a informação da porta do serial cnc.
        self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc) =
        Comando que estabelece a comunicação entre PC e o controler cnc.
        Muda o texto do botão para Abrir/Fechar.
        """
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_cnc.get()
        self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc)
        
        if(self.serial_cnc==None):
            self.btn_open_cnc['text'] = 'Abrir'
        else:
            self.btn_open_cnc['text'] = 'Fechar'
            
    #Função para abrir porta serial do gerador de funções
    def abrir_visa_gerador(self):
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_gerador.get()
        self.visa_gerador=controle_gerador.open_visa_gerador(com_port, self.visa_gerador)
        if(self.visa_gerador==None):
            self.btn_open_gerador['text'] = 'Abrir'
        else:
            self.btn_open_gerador['text'] = 'Fechar'
        self.att_ger()
            
    #Função de movimento através do botões de controle
    def ctrl_movimento_cnc(self, direcao):
        """Função para movimentação da antena apartir dos botões de controle na interface do programa.
            direcao = direcao.replace('%', self.cmb_step.get()) = Recebe o valor do passo para movimento.
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc) = Envia o comando para o controle cnc.
            self.txt_log.insert = Imprime texto na janela de log.
        """
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', self.cmb_step.get())
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
            
    #Função de movimento durante medição        
    def meas_movimento_cnc(self, direcao, step):
        """Função utilizada no movimento da antena durante a medição.
        direcao = direcao.replace('%', str(step)) = Utiliza o valor determinado
        na varíavel step para a movimentação.
        """
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', str(step))
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de envio comandos para serial CNC
    def envia_cmd_cnc(self):
        """Função que envia os comandos serial CNC.
        str_comando=self.ent_cmd.get() = Envia a linha de comando para serial cnc.
        str_resposta=controle_cnc.send_cmd(str_comando, self.serial_cnc) = Recebe a resposta
        do comando enviado.
        self.txt_log.insert = Imprime no log a resposta do comando.
        """
        if (self.serial_cnc != None):
            str_comando=self.ent_cmd.get()
            
            str_resposta=controle_cnc.send_cmd(str_comando, self.serial_cnc)
            
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de evento de "ENTER"       
    def comp_s(self, event):
        """Função usada ao pressionar "ENTER"."""
        self.envia_cmd_cnc()
    
    #Função para verificar se está medindo     
    def verifica_medicao(self):
        """Função que verifica se uma medição está sendo realizada."""
        #Caso esteja medindo aparece mensagem de erro.
        if (self.flag_medindo):
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função\ndurante a medição")
            return True
        else:
            return False
    

    
    #Função se string contem somente numero e maior que zero     
    def verifica_string(self, string, mensagem):
        """Função para verificar se a string contém somente números e se esses números são maior que zero."""
        #Caso número comece com sinal negativo substitui o sinal por '0'
        if not(string.isdigit()):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        
        if(int(string)==0):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        else:
            return False
        
    #Verifica se string é um numero decimal     
    def verifica_numero(self, string, mensagem):
        """Função para verificar se a string é um número decimal."""
        #Caso número comece com sinal negativo substitui o sinal por '0'
        if(string[0]=='-'):
            string=string.replace('-','0',1)
        if not(string.isdigit()):#verifica se é somente digito
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal'))
            return True
        return False
       
    
    #Função de definição de ponto 1
    def start_point(self):
        """Função que define o ponto 1 para a matriz.
        xyz=controle_cnc.current_pos(self.serial_cnc) = Guarda a posição atual do cnc na varíavel xyz.
        self.start_point_x = Armazena o ponto inicial de x.
        self.start_point_y = Armazena o ponto inicial de y.
        self.lbl_par_5.config(text... = Escreve na label 5 os valores dos pontos iniciais.
        """
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x, self.start_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Funções de definição de ponto 2
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end
        """Função que define o ponto 2 para a matriz.
        xyz=controle_cnc.current_pos(self.serial_cnc) = Guarda a posição atual do cnc na varíavel xyz.
        self.end_point_x = Armazena o ponto final de x.
        self.end_point_y = Armazena o ponto final de y.
        self.lbl_par_6.config(text... = Escreve na label 6 os valores dos pontos finais.
        """
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x, self.end_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Função para atualiza passo entre medidas
    def atualiza_passo(self):
        """Função que atualiza o passo para o eixo X e eixo Y.
        self.var_step_x = Recebe o calculo para o passo do movimento do eixo x,
        usando como variaveis o ponto incial e final do eixo x.
        self.lbl_part_7.config = Escreve na label 7 o valor do passo para o eixo x.
        self.var_step_y = Recebe o calculo para o passo do movimento do eixo y,
        usando como variaveis o ponto incial e final do eixo y.
        self.lbl_part_8.config = Escreve na label 8 o valor do passo para o eixo y.
        """
        if (self.verifica_medicao()):
            return
        try:
            #Para o passo do eixo X
            self.var_step_x=abs(self.start_point_x-self.end_point_x)/(int(self.cols)-1)
            self.lbl_par_7.config(text=(("%.4f" % (self.var_step_x)).replace('.',',')))
            #Para o passo do eixo Y
            self.var_step_y=abs(self.start_point_y-self.end_point_y)/(int(self.rows)-1)
            self.lbl_par_8.config(text=(("%.4f" % (self.var_step_y)).replace('.',',')))
        except AttributeError:
            return
    
    #Função de ativação flag de parar medição
    def stop_meas(self):
        """Função que ativa o flag para parar a medição."""
        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            self.flag_medindo=False
    
    #Função para atualziar tamanho da matriz
    def att_matriz(self):
        """Função para atualizar o tamanho de matriz de acordo com os valores escolhidos pelo usúario.
        Verifica se uma medição está acontecendo, caso sim, mostra uma mensagem de erro.
        valor_x = Recebe o tamanho do eixo x para a matriz.
        valor_y = Recebe o tamanho do eixo y para a matriz.
        Verifica se os valores digitados são números maiores que zero e não negativos para valor_x e valor_y.
        "Destroi"/Apaga tabela da matriz já existente e constroi uma nova com o tamanho desejado.
        self.frame2 = Frame(self.frm_tabela)  = Cria o frame para area dos botões e scrollbar.
        self.frame2.grid(row=3, column=0, sticky=NW) = Posiciona o frame da area dos botões.
        self.canvas = Canvas(self.frame2) = Cria a area onde ficam os botões
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview) = Cria scrollbar vertical e anexa a area de botões.
        self.canvas.configure(yscrollcommand=vsbar.set) = Anexa o scrollbar horizontal para a area dos botões.
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview) = Cria scrollbar horizontal e anexa a area de botões.
        self.canvas.configure(xscrollcommand=hsbar.set)= Anexa o scrollbar horizontal para a area dos botões.
        self.buttons_frame = Frame(self.canvas) = Cria frame que contem os botões
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))] = Cria matriz de botões
        self.button_matriz[i][j] = Button... = Adiciona botões no frame.
        self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2) = Envia um comando para
        realizar a função "medir_ponto" ao aperta um dos botões do frame.
        self.canvas.create_window((0,0), window=self.buttons_frame, anchor=NW) = Cria janela para os botões
        self.buttons_frame.update_idletasks() = Necessário para disponibilizar as informações do bbox.
        bbox = self.canvas.bbox(ALL)  # Obtem espaço delimitador de tela com botões.
        Define a região rolável do scrollbar como tela inteira com apenas o desejado número de linhas e colunas exibidas.
        self.cols=int(valor_x) = Define o tamanho de colunas pelo valor de x.
        self.cols=int(valor_y) = Define o tamanho de colunas pelo valor de y.
        self.atualiza_passo() = Atualiza o passo.        
        """
        if (self.flag_medindo):
            print("Botão pressionado y="+str(row)+" x="+str(col))
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função")
            return
        

        valor_x = self.var_matriz_x.get()
        valor_y = self.var_matriz_y.get()
        
        #tratamento do valor de entrada
        if (self.verifica_string(valor_x, 'X e Y') or self.verifica_string(valor_y, 'X e Y')):
            return
        
        if(int(valor_x)==0 or int(valor_y)==0):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
            return
        
        #destruir tabela existente
        try:
            self.frm_tabela.destroy()
        except AttributeError:
            pass
        else:
            self.frame2.destroy()
            self.canvas.destroy()
            self.buttons_frame.destroy()
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    self.button_matriz[i][j].destroy()
                    
        #//////////////////////////////////////////////////////////////////////////////////
        
        self.frm_tabela = Frame(self.frm_notebook1, relief=RIDGE)
        self.frm_tabela.place(x=460,y=55,width=608,height=590)
        
        # Cria o frame para area dos botões e scrollbar
        self.frame2 = Frame(self.frm_tabela)
        self.frame2.grid(row=3, column=0, sticky=NW)
        
        # Cria area dos botões
        self.canvas = Canvas(self.frame2)
        self.canvas.grid(row=0, column=0)
        
        # Cria scrollbar vertical e anexa a area de botões
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=vsbar.set)
        
        # Cria scrollbar horizontal e anexa a area de botões
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=EW)
        self.canvas.configure(xscrollcommand=hsbar.set)

        # Cria frame que contem os botões
        self.buttons_frame = Frame(self.canvas)
        
        # Cria matriz de botões
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        
        # Adiciona botões no frame
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j] = Button(self.buttons_frame, text="m[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz[i][j].grid(row=i, column=j)
                self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2)
        
        # Cria janela para os botões
        self.canvas.create_window((0,0), window=self.buttons_frame, anchor=NW)

        self.buttons_frame.update_idletasks()  # Needed to make bbox info available.
        bbox = self.canvas.bbox(ALL)  # Get bounding box of canvas with Buttons.

        # Define the scrollable region as entire canvas with only the desired
        # number of rows and columns displayed.
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/int(valor_x)) * self.cols_disp), int((h/int(valor_y)) * self.rows_disp)
        self.canvas.configure(scrollregion=bbox, width=dw, height=dh)
        
        #//////////////////////////////////////////////////////////////////////////////////
                
        self.cols=int(valor_x)
        self.rows=int(valor_y)
        self.atualiza_passo()
        
    #Função de re medição de ponto
    def medir_ponto(self,row,col):
        """Função para a medição do ponto selecionado manualmente.
        Verifica se uma medição está acontecendo, caso sim, para a função.
        if(self.start_point_x<self.end_point_x): x = float(self.start_point_x) =
        Verifica se ponto superior esquerdo foi definido e atribui as variaveis
        de coordenada.
        Variavel xyz = recebe a posição do cnc.
        x=x+(self.var_step_x*col)-float(xyz[0]) = Calcula a variavel de coordenada.
        direcao=self.dict_jog['right'] = Define o sentido em qual o cnc vai mover a antena(direita).
        direcao=self.dict_jog['left'] = Define o sentido em qual o cnc vai mover a antena(esquerda).
        self.meas_movimento_cnc(direcao, abs(x)) = Movimenta a antena de acordo com o sentido(direcao)
        e o tamanho do passo (x).
        self.matrix_meas[row][col]=self.leitura_amplitude() = Recebe o valor da amplitude para o ponto
        [row][col] atual da matriz.
        self.max_medido = np.max(self.matrix_meas) = Define o maior valor medido da matriz.
        self.lbl_par_11['text'] = str(self.max_medido) = Escreve na label 11 o maior valor medido.
        self.min_medido = np.min(self.matrix_meas) = Define o menor valor medido da matriz.
        self.lbl_par_12['text'] = str(self.min_medido) = Escreve na label 12 o menor valor medido.
        self.button_matriz[row][col].config(text="\n"+str(self.matrix_meas[row][col])+" dBm\n") =
        Escreve no frame dos botões.
        """
        if (self.verifica_medicao()):
            return
        
        #Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        #de coordenada
        try:
            if(self.start_point_x<self.end_point_x): x = float(self.start_point_x)
            else: x = float(self.end_point_x)
            if(self.start_point_y>self.end_point_y): y = float(self.start_point_y)
            else: y = float(self.end_point_y)
            print("ponto inicial= "+str(x)+' '+str(y))
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Limites não definidos",
                                   message="Pontos não definidos    ")
            return
        
        self.flag_medindo=True
        print("Medir ponto x="+str(col)+" y="+str(row))            
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x=x+(self.var_step_x*col)-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste7")
                time.sleep(0.125)
		
        y=y-(self.var_step_y*row)-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste6")
                time.sleep(0.125)
        
        self.matrix_meas[row][col]=self.leitura_amplitude()
        self.max_medido = np.max(self.matrix_meas)
        self.lbl_par_11['text'] = str(self.max_medido)
        self.min_medido = np.min(self.matrix_meas)
        self.lbl_par_12['text'] = str(self.min_medido)
        self.button_matriz[row][col].config(text="\n"+str(self.matrix_meas[row][col])+" dBm\n")
        
        self.flag_medindo=False
        
    #Função de comunicação com analisador para definição da frequencia de medição
    def att_freq(self):
        """Função que comunica com o analisador de espectro para sua atualização de frequência.
        freq = self.var_freq.get() = Recebe o valor da frequência digitada na interface.
        (self.verifica_string(freq, 'frequência') = Verifica se string contem somente numero e maior que zero.
        Calcula a frequência de acordo com a unidade.
        controle_analisador.receiver_frequencia(self.visa_analisador,freq) = Envia a variavel freq para o
        analisador.
        """
        if (self.verifica_medicao()):
            return
        
        freq = self.var_freq.get()
        
        #Verifica se string contem somente numero e maior que zero
        if (self.verifica_string(freq, 'frequência')):
            return
        
        if(self.cmb_freq.get()=="KHz"):
            freq=int(freq)*pow(10, 3)
        elif(self.cmb_freq.get()=="MHz"):
            freq=int(freq)*pow(10, 6)
        else:
            freq=int(freq)*pow(10, 9)
        controle_analisador.receiver_frequencia(self.visa_analisador,freq)
        
    def att_ger(self):

        #Configuração da impedância do canal
        imp_ger = self.imp.get()
        
        if(self.imp_gerador.get()=="KΩ"):
            imp_ger=int(imp_ger)*pow(10, 3)
        
        controle_gerador.imp(imp_ger)

        #Configuração de frequência 
        freq_ger = self.freq_gerador.get()
        
        if (self.verifica_string(freq_ger, 'frequência')):
            return
        if(self.freq_gerador_mag.get()=="KHz"):
            freq_ger=int(freq_ger)*pow(10, 3)
        elif(self.freq_gerador_mag.get()=="MHz"):
            freq_ger=int(freq_ger)*pow(10, 6)

        controle_gerador.frequencia(freq_ger)
        
        #Configuração da amplitude de tensão 
        vamp_ger = self.vamp.get()
        
        if(self.vamp_gerador_mag.get()=="mV"):
            vamp_ger=int(vamp_ger)/pow(10, 3)
        
        controle_gerador.vamp(vamp_ger)   
        
    #Função de medição
    def medicao(self):
        """Função que realiza a medição dos pontos, movimenta a antena,
        recebe os valores de amplitude.
        Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        de coordenada.
        self.var_pb.set(1) = Define a barra de progresso.
        self.matrix_meas = [[-80 for _ in range(self.cols)] for _ in range(self.rows)] = Define o tamanho
        da matriz de acordo com o valores dados para a quantidade de colunas e linhas.
        var_progressbar=0 = Barra de progresso começa em 0.
        self.max_medido, self.min_medido = -99, 0 = Define os valores de max e mín.
        step_progressbar=100/((self.rows)*(self.cols)) = Calcula o tamanho da barra de progesso.
        self.meas_time = datetime.now() = Salva o tempo antes de começar a medição.
        flag_ordem=True = True = direita para esquerda se false = esquerda para direita.
        if(self.matrix_meas[i][j] > self.max_medido) = Se o valor medido no ponto atual
        for maior que o valor máximo medido, self.max_medido é alterado para o novo valor.
        if(self.matrix_meas[i][j] < self.min_medido) = Se o valor medido no ponto atual
        for menor que o valor mínimo medido, self.min_medido é alterado para o novo valor.
        self.button_matriz[i][j].config...= Escreve o valor da amplitude medido no botão do ponto na tabela.
        self.var_pb.set(var_progressbar) = Incrementa a barra de progresso.
        Calcula o tempo total estimado no começo quando i=0 e j=0;
        delta_t = datetime.now() - self.meas_time = Calcula a diferença entre o tempo salvo no começo
        com o tempo atual.
        tempo_total = (self.rows)*(self.cols)*delta_t = Calcula o tempo total.
        tempo_total = timedelta(seconds=tempo_total.total_seconds()) = Guarda os valores de segundos.
        horas, sobra = divmod(tempo_total.seconds, 3600) = Guarda os valores de horas e a sobra.
        minutos, segundos = divmod(sobra, 60) = Guarda os valores de minutos.
        self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))
        Escreve na label 10 o tempo estimado no formato 00h:00m:00s.
        Repete os mesmos calculos para a medição do tempo conforme o progresso da medição.
        if(i+1<self.rows) = A antena vai mover para baixo.
        self.flag_medindo=False = Altera a flag de medição quando termina.    
        """
        if (self.verifica_medicao()):
            return
        #Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        #de coordenada
        try:
            if(self.start_point_x<self.end_point_x): x = float(self.start_point_x)
            else: x = float(self.end_point_x)
            if(self.start_point_y>self.end_point_y): y = float(self.start_point_y)
            else: y = float(self.end_point_y)
            print("ponto inicial= "+str(x)+' '+str(y))
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Limites não definidos",
                                   message="Pontos não definidos    ")
            return
        
        self.flag_medindo=True
        
        self.var_pb.set(1)
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x= x-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste1")
                time.sleep(0.125)
            
        y= y-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste2")
                time.sleep(0.125)
                
        self.matrix_meas = [[-80 for _ in range(self.cols)] for _ in range(self.rows)]
        
        var_progressbar=0
        self.max_medido, self.min_medido = -99, 0
        
        self.lbl_par_11['text'] = '-0.00'
        self.lbl_par_12['text'] = '-0.00'
        
        self.var_pb.set(var_progressbar)
        step_progressbar=100/((self.rows)*(self.cols))
        
        self.meas_time = datetime.now()
        flag_ordem=True #false=esquerda pra direita
        for i in range(0, self.rows):#linha
            if(self.flag_stop):
                self.flag_stop = False
                return
            if(flag_ordem):
                for j in range(0, self.cols):#coluna
                    if(self.flag_stop):
                        self.flag_stop = False
                        return
                    self.matrix_meas[i][j]=self.leitura_amplitude()                     
                    if(self.matrix_meas[i][j] > self.max_medido):
                        self.max_medido = self.matrix_meas[i][j]
                        self.lbl_par_11['text'] = str(self.max_medido)
                    if(self.matrix_meas[i][j] < self.min_medido):
                        self.min_medido = self.matrix_meas[i][j]
                        self.lbl_par_12['text'] = str(self.min_medido)
                    self.button_matriz[i][j].config(text="\n"+str(self.matrix_meas[i][j])+" dBm\n")
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    if (i > 0) or (j > 0): #define tempo entre dois pontos 
                        tempo_total = tempo_total - delta_t
                        tempo_total = timedelta(seconds=tempo_total.total_seconds())
                        horas, sobra = divmod(tempo_total.seconds, 3600)
                        minutos, segundos = divmod(sobra, 60)
                        self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))
                    self.master.update()
                    if(j+1<self.cols):
                        self.meas_movimento_cnc(self.dict_jog['right'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                            print("teste3")
                            time.sleep(0.125)
                        if (i == 0) and (j == 0): #define tempo entre dois pontos 
                            delta_t = datetime.now() - self.meas_time
                            tempo_total = (self.rows)*(self.cols)*delta_t
                            tempo_total = timedelta(seconds=tempo_total.total_seconds())
                            horas, sobra = divmod(tempo_total.seconds, 3600)
                            minutos, segundos = divmod(sobra, 60)
                            self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))

                flag_ordem=False
            else:
                for j in reversed(range(0,self.cols)):#coluna
                    if(self.flag_stop):
                        self.flag_stop = False
                        return
                    self.matrix_meas[i][j]=self.leitura_amplitude()
                    if(self.matrix_meas[i][j] > self.max_medido):
                        self.max_medido = self.matrix_meas[i][j]
                        self.lbl_par_11['text'] = str(self.max_medido)
                    elif(self.matrix_meas[i][j] < self.min_medido):
                        self.min_medido = self.matrix_meas[i][j]
                        self.lbl_par_12['text'] = str(self.min_medido)
                    self.button_matriz[i][j].config(text="\n"+str(self.matrix_meas[i][j])+" dBm\n")
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    if (i > 0) or (j > 0): #define tempo entre dois pontos 
                        tempo_total = tempo_total - delta_t
                        tempo_total = timedelta(seconds=tempo_total.total_seconds())
                        horas, sobra = divmod(tempo_total.seconds, 3600)
                        minutos, segundos = divmod(sobra, 60)
                        self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))
                    self.master.update()
                    if(j!=0):
                        self.meas_movimento_cnc(self.dict_jog['left'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                            print("teste4")
                            time.sleep(0.125)
                flag_ordem=True
            if(i+1<self.rows):
                self.meas_movimento_cnc(self.dict_jog['down'], self.var_step_y)
                while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                    print("teste5")
                    time.sleep(0.125)
       
        self.flag_medindo=False
    
    #Função para salvar arquivo com extensão csv
    def save(self):
        """Função que salva a matriz gerada como um arquivo com extensão csv.

        self.meas_time.strftime = Recebe o tempo em formato de string.
        
        file_path = Abre janela para escolher onde o arquivo csv será salvo.
        
        file = open(file_path, 'w', newline ='')  = Abre o arquivo csv como modo "write".
        
        write = csv.writer(file, delimiter=';')  = Escreve o resultado da medida no arquivo csv.
        
        write.writerows(self.matrix_meas) = Escreve todas as linhas da matriz no arquivo csv.
        
        messagebox.showwarning = Mensagem de error caso não tenha nenhuma informação para salvar.        
        """
        try:
            self.meas_time.strftime
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+
                       self.meas_time.strftime("_%d-%m-%Y_%H-%M")+".csv")
            
            #Abrir arquivo csv mode "write"
            file = open(file_path, 'w', newline ='') 

            #Escreve resultado da medida no arquivo csv
            with file:
                write = csv.writer(file, delimiter=';') 
                write.writerows(self.matrix_meas) 
            
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Medida não realizada", message="Nenhuma informação para salvar ")
    
    #Função de homing
    def vai_origem(self):
        """Função que posiciona a antena para o ponto inicial/origem da matriz."""
        if(self.verifica_medicao()):
            return
        controle_cnc.cnc_jog('$H',self.serial_cnc)
        time.sleep(5)
        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
            time.sleep(0.05)
        
    #Função de alteração da flag de plot da grade
    def plot_grade(self):
        """Função que altera se o plot do mapa de calor será com ou sem grade."""
        if(self.flag_grade):
            self.btn_plt_grade.config(text='        Grade\nDESABILITADO')
            self.flag_grade=False
        else:
            self.btn_plt_grade.config(text='      Grade\nHABILITADO')
            self.flag_grade=True
    
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_anotacao(self):
        """Função que altera se o plot do mapa de calor será com ou sem anotação."""
        if(self.flag_anotacao):
            self.btn_plt_anotacao.config(text='     Unidade\nDESABILITADO')
            self.var_plot_tamanho_x['state'] = 'disable'
            self.var_plot_tamanho_y['state'] = 'disable'
            self.flag_anotacao=False
        else:
            self.btn_plt_anotacao.config(text='Unidade\nHABILITADO')
            self.var_plot_tamanho_x['state'] = 'enable'
            self.var_plot_tamanho_y['state'] = 'enable'
            self.flag_anotacao=True
            
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_auto_maxmin(self):
        """Função que altera o max e min do plot do mapa de calor."""
        if(self.flag_auto_maxmin):
            self.btn_plt_maxmin.config(text='MAX/MIN automático DESABILITADO')
            self.var_plot_max['state'] = 'enable'
            self.var_plot_min['state'] = 'enable'
            self.flag_auto_maxmin=False
        else:
            self.btn_plt_maxmin.config(text='MAX/MIN automático HABILITADO')
            self.var_plot_max['state'] = 'disable'
            self.var_plot_min['state'] = 'disable'
            self.flag_auto_maxmin=True
            
    #Função de apresentação do mapa de calor para o dado medida realizada
    def plot_dadoatual(self):
        """Função que gera o mapa de calor de acordo com os dados obtidos pela medição realizada."""
        if not(self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        try:
            data=self.matrix_meas
        except:
            #erro no dado atual
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(map(max,data))
            vmin=min(map(min,data))
            print(vmax)
            print(vmin)
        else:
            vmax=int(self.var_plot_max.get())#função que verifica se é numero
            vmin=int(self.var_plot_min.get())#função que veririca se é numero
        step=[self.var_step_x, self.var_step_y]
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
        
        if(self.var_espelhamento_x.get()):#Se espelhamento no eixo X selecionado
            for aux in data:
                aux.reverse()
                
        if(self.var_espelhamento_y.get()):#Se espelhamento no eixo Y selecionado
            data.reverse()
        
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save)
        
    def plot_arquivo_csv(self):
        """Função que gera o mapa de calor de acordo com os dados obtidos
        pelo arquivo csv."""
        if not (self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        if(self.verifica_string(self.var_plot_tamanho_x.get(), 'Tamanho da placa')):
            return
        if(self.verifica_string(self.var_plot_tamanho_y.get(), 'Tamanho da placa')):
            return
        try:
            data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))
            data=[]
            with open(data_caminho, 'r') as file:
                reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
                for row in reader: # each row is a list
                    data.append(row)
        except:
            return
        if(len(data)<1)or(len(data[0])<1):
            #acusa erro de arquivo csv com problema na linha ou coluna
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(map(max,data))
            vmin=min(map(min,data))
            print(vmax)
            print(vmin)
        else:
            vmax=int(self.var_plot_max.get())#função que verifica se é numero
            vmin=int(self.var_plot_min.get())#função que veririca se é numero
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
        
        if(self.var_espelhamento_x.get()):#Se espelhamento no eixo X selecionado
            for aux in data:
                aux.reverse()
                
        if(self.var_espelhamento_y.get()):#Se espelhamento no eixo Y selecionado
            data.reverse()
        
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save)
    
    # Para o botão de abrir arquivo csv na aba principal do programa YURI
    def info_arquivocsv(self):
        """Função que obtem os dados de uma matriz salvos em um csv e
        atualiza esses valores na tabela da matriz."""
        if (self.verifica_medicao()):
            return          
        if not (self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                 return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        if(self.verifica_string(self.var_plot_tamanho_x.get(), 'Tamanho da placa')):
            return
        if(self.verifica_string(self.var_plot_tamanho_y.get(), 'Tamanho da placa')):
            return
        try:
            data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))
            data=[]
            with open(data_caminho, 'r') as file:
                reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
                for row in reader: # each row is a list
                    data.append(row)                    
        except:
            return
        if(len(data)<1)or(len(data[0])<1):
            #acusa erro de arquivo csv com problema na linha ou coluna
            return
    
        # Para testar se a função está lendo o tamanho do arquivo corretamente
#         print(len(data))
#         print(len(data[0]))
        
        vmax=max(map(max,data))
        vmin=min(map(min,data))
        self.max_medido = vmax
        self.min_medido = vmin
#         print(vmax)
#         print(vmin)
        self.lbl_par_11['text'] = str(self.max_medido)
        self.lbl_par_12['text'] = str(self.min_medido)        
        self.att_matriz
        
        valor_x = str(len(data[0]))
        valor_y = str(len(data))
#         print(valor_x)
        
        # A partir dessa linha o programa refaz a matriz de botões da janela principal de acordo com o tamanho
        # da matriz do arquivo csv
        
        #tratamento do valor de entrada
        if (self.verifica_string(valor_x, 'X e Y') or self.verifica_string(valor_y, 'X e Y')):
            return
        
        if(int(valor_x)==0 or int(valor_y)==0):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
            return
        
        #destruir tabela existente
        try:
            self.frm_tabela.destroy()
        except AttributeError:
            pass
        else:
            self.frame2.destroy()
            self.canvas.destroy()
            self.buttons_frame.destroy()
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    self.button_matriz[i][j].destroy()
                    
        #//////////////////////////////////////////////////////////////////////////////////
        
        self.frm_tabela = Frame(self.frm_notebook1, relief=RIDGE)
        self.frm_tabela.place(x=460,y=55,width=608,height=590)
        
        # Cria o frame para area dos botões e scrollbar
        self.frame2 = Frame(self.frm_tabela)
        self.frame2.grid(row=3, column=0, sticky=NW)
        
        # Cria area dos botões
        self.canvas = Canvas(self.frame2)
        self.canvas.grid(row=0, column=0)
        
        # Cria scrollbar vertical e anexa a area de botões
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=vsbar.set)
        
        # Cria scrollbar horizontal e anexa a area de botões
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=EW)
        self.canvas.configure(xscrollcommand=hsbar.set)

        # Cria frame que contem os botões
        self.buttons_frame = Frame(self.canvas)
        
        # Cria matriz de botões
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        
        # Adiciona botões no frame
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j] = Button(self.buttons_frame, text="m[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz[i][j].grid(row=i, column=j)
                self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2)
        
        # Cria janela para os botões
        self.canvas.create_window((0,0), window=self.buttons_frame, anchor=NW)

        self.buttons_frame.update_idletasks()  # Needed to make bbox info available.
        bbox = self.canvas.bbox(ALL)  # Get bounding box of canvas with Buttons.

        # Define the scrollable region as entire canvas with only the desired
        # number of rows and columns displayed.
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/int(valor_x)) * self.cols_disp), int((h/int(valor_y)) * self.rows_disp)
        self.canvas.configure(scrollregion=bbox, width=dw, height=dh)
        
        #//////////////////////////////////////////////////////////////////////////////////
                
        self.cols=int(valor_x)
        self.rows=int(valor_y)
        self.atualiza_passo()
        
        # Passando os valores do arquivo csv lido para a matriz na aba principal - Yuri
        self.matrix_meas=data
        i = 0
        j = 0
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j].config(text="\n"+str(self.matrix_meas[i][j])+" dBm\n")
                j = j + 1
            i = i + 1
    
    def plot_salva(self):
        """Função que salva o último plot criado pelo programa."""
        files = [('Portable Graphics Format(PNG)', '*.png'),
                 ('All Files', '*.*')] 
        destino= filedialog.asksaveasfilename(filetypes = files, defaultextension = ".png")
        
        plt.savefig(destino,bbox_inches="tight")
    
    def mapa_de_calor(self, data, vmax, vmin, step, flag, escolhas, destino_save):
        """Função que gera o plot do mapa de calor de acordo com os dados
        obtidos."""
        #flag[0] habilitação da anotação
        #flag[1] habilitação da grade
        #flag[2] escolha entre apresentação ou salvar
        #step[0] passo x
        #step[1] passo y
        #escolhas[0] cor do mapa de calor
        #escolhas[1] titulo do mapa de calor
        #escolhas[2] interpolação do mapa de calor
        
        try:
            self.canvas2.destroy()
            plt.close('all')
        except:
            pass
        
        #Gera figura de plotagem 
        fig, ax = plt.subplots()
        
        #cor cinza de background
        if not(flag[2]):
            fig.patch.set_facecolor('#F0F0F0')
        
        #Gera mapa de calor
        im = ax.imshow(data, interpolation=escolhas[2], cmap=escolhas[0], vmax=vmax, vmin=vmin)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fcm' % float(i*step[1]))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fcm' % float(i*step[0]))
            
        #Configuração de apresentação das anotações
        if(flag[0]):
            ax.set_xticks(np.arange(len(anotacao_x)))
            ax.set_yticks(np.arange(len(anotacao_y)))
            ax.set_xticklabels(anotacao_x)
            ax.set_yticklabels(anotacao_y)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

        #Titulo do mapa de calor
        ax.set_title(escolhas[1])

        #Adiciona barra de cor
        if(len(data)>len(data[0])):
            plt.colorbar(im, shrink=1)
        else:
            plt.colorbar(im, shrink=0.8)
        
        #Tamanho do mapa de calor
        plt.xlim(right=len(data[0])-0.5)
        plt.xlim(left=-0.5)
        plt.ylim(top=-0.5)
        plt.ylim(bottom=len(data)-0.5)
        
        #Grade
        if(flag[1]):
            plt.grid(color='w', which='major', alpha=0.5)
        
        self.canvas2 = FigureCanvasTkAgg(fig, master = self.frm_heatmap)
        self.canvas2.draw()
        if(len(data)>=len(data[0])):
            self.canvas2.get_tk_widget().place(x=5,y=5,height=650)
        else:
            self.canvas2.get_tk_widget().place(x=5,y=5,width=790)
            
    def all_children (self, wid) :
        """Função que organiza as ferramentas da interface tkinter."""
        widget_list = wid.winfo_children()
        for item in widget_list :
            if item.winfo_children() :
                widget_list.extend(item.winfo_children())
        for item in widget_list :
            item.destroy()
        
def resize(event):
    """Função que altera o tamanho da janela do programa."""
    print("Novo tamanho é: {}x{}".format(event.width, event.height))

def main():
    """Função que gera a janela da interface junto com suas características."""
    #---Gera janela-----------------------
    root = Tk()
    root.geometry('1080x720')
    
    #retorna tamanho da janela
    #root.bind("<Configure>", resize)
    
    #maximiza a janela
    #root.state('zoomed')
    
    #janela modo tela cheia
    #root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    
    #desabilita resize
    #root.resizable(0, 0)
    root.call('tk', 'scaling', 1.3)          #define escala (funciona porém quando fica muito alta continua problema
    #windll.shcore.SetProcessDpiAwareness(1) #altera dpi do sistema operacional (não funciona)
    #---icone da janela-------------------
    try:
        icone = PhotoImage(file = os.path.realpath(__file__).replace(os.path.basename(__file__),'')+'labcem_icone.png') 
        root.iconphoto(False, icone)
    except Exception as e:
        print(e)
    #-------------------------------------
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()
