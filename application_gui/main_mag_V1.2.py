#Main Magnético V1.2 -  25/07/2022


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

import serial.tools.list_ports   #Bibliote de conecção serial
import time                      #Biblioteca para delay
import csv                       #Biblioteca salvar dados em arquivo csv
import numpy as np               #Biblioteca de array FUTURO RETIRAR
from datetime import datetime, timedelta    #Biblioteca do tempo da maquina
import os

#Escrita e Leitura serial com grbl
from cnc_controle import controle_cnc
from analisador_controle import controle_analisador
from gerador_controle import controle_gerador

class main_window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13  # tamanho da tabela
    rows_disp = 9.90  # numero de linhas apresentado
    cols_disp = 7.7 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop = False, False
    flag_grade, flag_grade_y, flag_grade_xy = True, True, True
    flag_anotacao, flag_anotacao_y, flag_anotacao_xy = True, True, True
    flag_auto_maxmin, flag_auto_maxmin_y,flag_auto_maxmin_xy= True, True, True
    tempo_entre_medidas=1 #em segundos
    max_medido_x, min_medido_x = -99, 99
    max_medido_y, min_medido_y = -99, 99
    
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
        self.visa_analisador = None
        self.visa_gerador = None
        
    def initUI(self):
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
        self.master.title('Controle Auto Scan - Magnético')#futuro nome?
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
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
        btn_refresh.place(x=353,y=1,width=75,height=53)
        btn_refresh['command'] = self.lista_serial
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.place(x=5,y=30,width=90,height=20)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.place(x=73,y=29,width=185,height=23)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.place(x=267,y=28,width=80,height=25)
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
#         lbl_06.place(x=10,y=120,width=415,height=170)
#                 
        self.txt_log = scrolledtext.ScrolledText(lbl_06, width=48, height=9)
#         self.txt_log.place(x=1,y=1)
#          
#         lbl_07 = Label(frm_ctrls, text='Comando:')
#         lbl_07.place(x=10,y=295,width=60,height=20)
#          
#         self.ent_cmd = Entry(frm_ctrls, width=25)
#         self.ent_cmd.place(x=80,y=295,width=294,height=20)       
#         self.ent_cmd.bind('<Return>', self.comp_s)
#          
#         self.btn_send_cmd = Button(frm_ctrls, text='Enviar')
#         self.btn_send_cmd.place(x=376,y=294,width=50,height=22)  
#         self.btn_send_cmd['command'] = self.envia_cmd_cnc

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
        frm_param.rowconfigure(7, pad=3)
        
        lbl_par_1 = Label(frm_param, text='Possição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Possição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (cm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (cm):')
        lbl_par_9 = Label(frm_param, text='Maior valor medido em X:')
        lbl_par_10 = Label(frm_param, text='Menor valor medido em X:')
        lbl_par_11 = Label(frm_param, text='Maior valor medido em Y:')
        lbl_par_12 = Label(frm_param, text='Menor valor medido em Y:')
        self.lbl_par_5 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_6 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        self.lbl_par_13 = Label(frm_param, text='-00,00')
        self.lbl_par_14 = Label(frm_param, text='-00,00')
        self.lbl_par_15 = Label(frm_param, text='-00,00')
        self.lbl_par_16 = Label(frm_param, text='-00,00')
        
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
        lbl_par_11.grid(row=6, column=0, sticky=W)
        lbl_par_12.grid(row=7, column=0, sticky=W)
        self.lbl_par_13.grid(row=4, column=1, sticky=E)
        self.lbl_par_14.grid(row=5, column=1, sticky=E)
        self.lbl_par_15.grid(row=6, column=1, sticky=E)
        self.lbl_par_16.grid(row=7, column=1, sticky=E)
        
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
        
        self.str_save = Entry(frm_04, width=38)
        self.str_save.grid(row=0, column=1)
        
        lbl_12 = Label(frm_04, text=' EIXO_dd-mm-yyyy_HH-MM.csv ')
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
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.place(x=72,y=27,width=132,height=25)
        self.btn_freq_refresh['command'] = self.janela_configuracao
        
        #---Frame do gerador----------------
        frm_gerador = Labelframe(self.frm_notebook1, text='Gerador')
        frm_gerador.place(x=10, y=350,width=440,height=90)
        
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
        
        btn_att_ger = Button(frm_gerador, text='Atualizar')
        btn_att_ger.place(x=235, y=17, width=75, height=30)
        btn_att_ger['command'] = self.att_ger        
        
        #-Botões de atuação medição
        btn_stop = Button(self.frm_notebook1, text='Abortar Medição')
        btn_stop.place(x=305,y=310,width=145,height=40)
        btn_stop['command'] = self.stop_meas
        
        self.btn_pause = Button(self.frm_notebook1, text='Iniciar Medição Y')
        self.btn_pause.place(x=157,y=310,width=145,height=40)
        self.btn_pause['command'] = lambda sentido=True: self.medicao(sentido)
        
        btn_start = Button(self.frm_notebook1, text='Iniciar Medição X')
        btn_start.place(x=10,y=310,width=145,height=40)
        btn_start['command'] = lambda sentido=False: self.medicao(sentido)
        
        #-Notebook de plotagem
        self.frm_notebook2 = Frame(notebook)
        self.frm_notebook2.pack(fill=BOTH, expand=True)
        notebook.add(self.frm_notebook2, text='      Mapa de calor X     ')
        
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
        
        lbl_22 = Label(frm_plot_maxmin, text='MIN. :')
        lbl_22.place(x=110,y=5,width=60,height=20)
        self.var_plot_min=Entry(frm_plot_maxmin, width=8)
        self.var_plot_min.insert(END, '%d' % -80)
        self.var_plot_min.place(x=145,y=3,width=57,height=20)
        
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
        frm_plot_grid = Labelframe(frm_plot, text='Anotação eixos')
        frm_plot_grid.place(x=123,y=281,width=107,height=67)
        
        self.btn_plt_anotacao = Button(frm_plot_grid, text='   Anotação\nHABILITADO')
        self.btn_plt_anotacao.place(x=5,y=1,width=93,height=40)
        self.btn_plt_anotacao['command'] = self.plot_anotacao
        
        
        #---Qual dado ser plotado
        frm_plot_dado = Labelframe(frm_plot, text='Dado plot')
        frm_plot_dado.place(x=5,y=350,width=225,height=200)
        
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
        btn_plt_salvar.place(x=5,y=555,width=225,height=40)
        btn_plt_salvar['command'] = self.plot_salva
        
        #--Apresentação do mapa de calor
        self.frm_heatmap = Labelframe(self.frm_notebook2, text='Mapa de calor X')
        self.frm_heatmap.place(x=260,y=5,width=805,height=680)
        
        self.frm_notebook_y = Frame(notebook)
        self.frm_notebook_y.pack(fill=BOTH, expand=True)
        notebook.add(self.frm_notebook_y, text='      Mapa de calor Y     ')
        
        #--Parametros de plotagem
        frm_plot_y = Labelframe(self.frm_notebook_y, text='Escolhas para plot')
        frm_plot_y.place(x=10,y=5,width=240,height=680)  
        
        #---Label frame da barra de cor
        frm_plot_parametro_y = Labelframe(frm_plot_y, text='Barra de cor')
        frm_plot_parametro_y.place(x=5,y=1,width=225,height=150)
        
        #----Definição de parametros da barra de cor
        frm_plot_maxmin_y = Labelframe(frm_plot_parametro_y, text='Entrada manual:')
        frm_plot_maxmin_y.place(x=5,y=0,width=212,height=47)
        
        lbl_21_y = Label(frm_plot_maxmin_y, text='MAX. :')
        lbl_21_y.place(x=5,y=5,width=60,height=20)
        self.var_plot_max_y=Entry(frm_plot_maxmin_y, width=8)
        self.var_plot_max_y.insert(END, '%d' % 10)
        self.var_plot_max_y.place(x=45,y=3,width=57,height=20)
        
        lbl_22_y = Label(frm_plot_maxmin_y, text='MIN. :')
        lbl_22_y.place(x=110,y=5,width=60,height=20)
        self.var_plot_min_y=Entry(frm_plot_maxmin_y, width=8)
        self.var_plot_min_y.insert(END, '%d' % -80)
        self.var_plot_min_y.place(x=145,y=3,width=57,height=20)
        
        lbl_ou_y = Label(frm_plot_parametro_y, text=' OU')
        lbl_ou_y.place(x=95,y=47,width=30,height=15)
        
        self.btn_plt_maxmin_y = Button(frm_plot_parametro_y, text='MAX/MIN automático HABILITADO')
        self.btn_plt_maxmin_y.place(x=5,y=65,width=213,height=34)
        self.btn_plt_maxmin_y['command'] = self.plot_auto_maxmin_y
        
        #----Combo box escolha de cor
        lbl_21_y = Label(frm_plot_parametro_y, text='Tabela de COR: ')
        lbl_21_y.place(x=5,y=105,width=85,height=20)
        self.cmb_plot_cor_y = Combobox(frm_plot_parametro_y, width=5)# Janela de seleção do tamanho de passo
        self.cmb_plot_cor_y.place(x=94,y=105,width=123,height=20)
        self.cmb_plot_cor_y['values'] = ['inferno','viridis','gist_heat','hot']
        self.cmb_plot_cor_y.current(0) 
        
        
        #---Titulo do plot
        frm_plot_titulo_y = Labelframe(frm_plot_y, text='Título')
        frm_plot_titulo_y.place(x=5,y=153,width=225,height=72)
        
        lbl_22_y = Label(frm_plot_titulo_y, text=' Título do plot :')
        lbl_22_y.grid(row=0, column=0, padx= 3)
        self.var_plot_titulo_y=Entry(frm_plot_titulo_y, width=80)
        self.var_plot_titulo_y.insert(END, 'nome_exemplo')
        self.var_plot_titulo_y.place(x=5,y=25,width=210,height=20)
        
        #---Filtro no plot
        frm_plot_interpolacao_y = Labelframe(frm_plot_y, text='Filtro')
        frm_plot_interpolacao_y.place(x=5,y=230,width=225,height=49)
        
        lbl_24_y = Label(frm_plot_interpolacao_y, text=' Interpolação :')
        lbl_24_y.place(x=5,y=5,width=78,height=20)
        
        self.cmb_plot_interpolacao_y = Combobox(frm_plot_interpolacao_y, width=17)#janela de escolha interpolacao
        self.cmb_plot_interpolacao_y.place(x=90,y=2,width=125,height=23)
        self.cmb_plot_interpolacao_y['values'] = ['none','spline16','catrom','gaussian','sinc']
        self.cmb_plot_interpolacao_y.current(3)
        
        #---Habilitar grid
        frm_plot_grid_y = Labelframe(frm_plot_y, text='Grade')
        frm_plot_grid_y.place(x=5,y=281,width=107,height=67)
        
        self.btn_plt_grade_y = Button(frm_plot_grid_y, text='      Grade\nHABILITADO')
        self.btn_plt_grade_y.place(x=5,y=1,width=93,height=40)
        self.btn_plt_grade_y['command'] = self.plot_grade_y
        
        #---Habilitar label
        frm_plot_grid_y = Labelframe(frm_plot_y, text='Anotação eixos')
        frm_plot_grid_y.place(x=123,y=281,width=107,height=67)
        
        self.btn_plt_anotacao_y = Button(frm_plot_grid_y, text='   Anotação\nHABILITADO')
        self.btn_plt_anotacao_y.place(x=5,y=1,width=93,height=40)
        self.btn_plt_anotacao_y['command'] = self.plot_anotacao_y
        
        
        #---Qual dado ser plotado
        frm_plot_dado_y = Labelframe(frm_plot_y, text='Dado plot')
        frm_plot_dado_y.place(x=5,y=350,width=225,height=200)
        
        #----Botões de escolha de dados
        lbl_23_y = Label(frm_plot_dado_y, text='Escolha qual dos dados :')
        lbl_23_y.place(x=5,y=1,width=200,height=20)
        
        btn_plt_dado_atual_y = Button(frm_plot_dado_y, text='Dados da medida\n         ATUAL')
        btn_plt_dado_atual_y.place(x=5,y=25,width=210,height=40)
        btn_plt_dado_atual_y['command'] = self.plot_dadoatual_y
        
        lbl_23_y = Label(frm_plot_dado_y, text='OU')
        lbl_23_y.place(x=97,y=67,width=20,height=16)
        
        lbl_24_y = Labelframe(frm_plot_dado_y)
        lbl_24_y.place(x=5,y=81,width=210,height=92)
        
        btn_plt_dado_arquivo_y = Button(lbl_24_y, text='Dados do arquivo\n           CSV')
        btn_plt_dado_arquivo_y.place(x=5,y=1,width=195,height=40)
        btn_plt_dado_arquivo_y['command'] = self.plot_arquivo_csv_y
        
        lbl_25_y = Label(lbl_24_y, text='Tamanho(cm) X:')
        lbl_25_y.place(x=5,y=45,width=91,height=20)
        self.var_plot_tamanho_x_y=Entry(lbl_24_y, width=80)
        self.var_plot_tamanho_x_y.insert(END, 12)
        self.var_plot_tamanho_x_y.place(x=99,y=45,width=40,height=20)
        
        lbl_26_y = Label(lbl_24_y, text='Y:')
        lbl_26_y.place(x=143,y=45,width=30,height=20)
        self.var_plot_tamanho_y_y=Entry(lbl_24_y, width=80)
        self.var_plot_tamanho_y_y.insert(END, 12)
        self.var_plot_tamanho_y_y.place(x=159,y=45,width=40,height=20)
        
        btn_plt_salvar_y = Button(frm_plot_y, text=' Salvar último\nMapa de Calor')
        btn_plt_salvar_y.place(x=5,y=555,width=225,height=40)
        btn_plt_salvar_y['command'] = self.plot_salva_y
        
        #--Apresentação do mapa de calor
        self.frm_heatmap_y = Labelframe(self.frm_notebook_y, text='Mapa de calor Y')
        self.frm_heatmap_y.place(x=260,y=5,width=805,height=680)
        
        self.frm_notebook_xy = Frame(notebook)
        self.frm_notebook_xy.pack(fill=BOTH, expand=True)
        notebook.add(self.frm_notebook_xy, text='      Mapa de calor XY     ')
        
        #--Parametros de plotagem
        frm_plot_xy = Labelframe(self.frm_notebook_xy, text='Escolhas para plot')
        frm_plot_xy.place(x=10,y=5,width=240,height=680)  
        
        #---Label frame da barra de cor
        frm_plot_parametro_xy = Labelframe(frm_plot_xy, text='Barra de cor')
        frm_plot_parametro_xy.place(x=5,y=1,width=225,height=150)
        
        #----Definição de parametros da barra de cor
        frm_plot_maxmin_xy = Labelframe(frm_plot_parametro_xy, text='Entrada manual:')
        frm_plot_maxmin_xy.place(x=5,y=0,width=212,height=47)
        
        lbl_21_xy = Label(frm_plot_maxmin_xy, text='MAX. :')
        lbl_21_xy.place(x=5,y=5,width=60,height=20)
        self.var_plot_max_xy=Entry(frm_plot_maxmin_xy, width=8)
        self.var_plot_max_xy.insert(END, '%d' % 10)
        self.var_plot_max_xy.place(x=45,y=3,width=57,height=20)
        
        lbl_22_xy = Label(frm_plot_maxmin_xy, text='MIN. :')
        lbl_22_xy.place(x=110,y=5,width=60,height=20)
        self.var_plot_min_xy=Entry(frm_plot_maxmin_xy, width=8)
        self.var_plot_min_xy.insert(END, '%d' % -80)
        self.var_plot_min_xy.place(x=145,y=3,width=57,height=20)
        
        lbl_ou_xy = Label(frm_plot_parametro_xy, text=' OU')
        lbl_ou_xy.place(x=95,y=47,width=30,height=15)
        
        self.btn_plt_maxmin_xy = Button(frm_plot_parametro_xy, text='MAX/MIN automático HABILITADO')
        self.btn_plt_maxmin_xy.place(x=5,y=65,width=213,height=34)
        self.btn_plt_maxmin_xy['command'] = self.plot_auto_maxmin_xy
        
        #----Combo box escolha de cor
        lbl_21_xy = Label(frm_plot_parametro_xy, text='Tabela de COR: ')
        lbl_21_xy.place(x=5,y=105,width=85,height=20)
        self.cmb_plot_cor_xy = Combobox(frm_plot_parametro_xy, width=5)# Janela de seleção do tamanho de passo
        self.cmb_plot_cor_xy.place(x=94,y=105,width=123,height=20)
        self.cmb_plot_cor_xy['values'] = ['inferno','viridis','gist_heat','hot']
        self.cmb_plot_cor_xy.current(0) 
        
        
        #---Titulo do plot
        frm_plot_titulo_xy = Labelframe(frm_plot_xy, text='Título')
        frm_plot_titulo_xy.place(x=5,y=153,width=225,height=72)
        
        lbl_22_xy = Label(frm_plot_titulo_xy, text=' Título do plot :')
        lbl_22_xy.grid(row=0, column=0, padx= 3)
        self.var_plot_titulo_xy=Entry(frm_plot_titulo_xy, width=80)
        self.var_plot_titulo_xy.insert(END, 'nome_exemplo')
        self.var_plot_titulo_xy.place(x=5,y=25,width=210,height=20)
        
        #---Filtro no plot
        frm_plot_interpolacao_xy = Labelframe(frm_plot_xy, text='Filtro')
        frm_plot_interpolacao_xy.place(x=5,y=230,width=225,height=49)
        
        lbl_24_xy = Label(frm_plot_interpolacao_xy, text=' Interpolação :')
        lbl_24_xy.place(x=5,y=5,width=78,height=20)
        
        self.cmb_plot_interpolacao_xy = Combobox(frm_plot_interpolacao_xy, width=17)#janela de escolha interpolacao
        self.cmb_plot_interpolacao_xy.place(x=90,y=2,width=125,height=23)
        self.cmb_plot_interpolacao_xy['values'] = ['none','spline16','catrom','gaussian','sinc']
        self.cmb_plot_interpolacao_xy.current(3)
        
        #---Habilitar grid
        frm_plot_grid_xy = Labelframe(frm_plot_xy, text='Grade')
        frm_plot_grid_xy.place(x=5,y=281,width=107,height=67)
        
        self.btn_plt_grade_xy = Button(frm_plot_grid_xy, text='      Grade\nHABILITADO')
        self.btn_plt_grade_xy.place(x=5,y=1,width=93,height=40)
        self.btn_plt_grade_xy['command'] = self.plot_grade_xy
        
        #---Habilitar label
        frm_plot_grid_xy = Labelframe(frm_plot_xy, text='Anotação eixos')
        frm_plot_grid_xy.place(x=123,y=281,width=107,height=67)
        
        self.btn_plt_anotacao_xy = Button(frm_plot_grid_xy, text='   Anotação\nHABILITADO')
        self.btn_plt_anotacao_xy.place(x=5,y=1,width=93,height=40)
        self.btn_plt_anotacao_xy['command'] = self.plot_anotacao_xy
        
        
        #---Qual dado ser plotado
        frm_plot_dado_xy = Labelframe(frm_plot_xy, text='Dado plot')
        frm_plot_dado_xy.place(x=5,y=350,width=225,height=200)
        
        #----Botões de escolha de dados
        lbl_23_xy = Label(frm_plot_dado_xy, text='Escolha qual dos dados :')
        lbl_23_xy.place(x=5,y=1,width=200,height=20)
        
        btn_plt_dado_atual_xy = Button(frm_plot_dado_xy, text='Dados da medida\n         ATUAL')
        btn_plt_dado_atual_xy.place(x=5,y=25,width=210,height=40)
        btn_plt_dado_atual_xy['command'] = self.plot_dadoatual_xy
        
        lbl_23_xy = Label(frm_plot_dado_xy, text='OU')
        lbl_23_xy.place(x=97,y=67,width=20,height=16)
        
        lbl_24_xy = Labelframe(frm_plot_dado_xy)
        lbl_24_xy.place(x=5,y=81,width=210,height=92)
        
        btn_plt_dado_arquivo_xy = Button(lbl_24_xy, text='Dados do arquivo\n           CSV')
        btn_plt_dado_arquivo_xy.place(x=5,y=1,width=195,height=40)
        btn_plt_dado_arquivo_xy['command'] = self.plot_arquivo_csv_xy
        
        lbl_25_xy = Label(lbl_24_xy, text='Tamanho(cm) X:')
        lbl_25_xy.place(x=5,y=45,width=91,height=20)
        self.var_plot_tamanho_x_xy=Entry(lbl_24_xy, width=80)
        self.var_plot_tamanho_x_xy.insert(END, 12)
        self.var_plot_tamanho_x_xy.place(x=99,y=45,width=40,height=20)
        
        lbl_26_xy = Label(lbl_24_xy, text='Y:')
        lbl_26_xy.place(x=143,y=45,width=30,height=20)
        self.var_plot_tamanho_y_xy=Entry(lbl_24_xy, width=80)
        self.var_plot_tamanho_y_xy.insert(END, 12)
        self.var_plot_tamanho_y_xy.place(x=159,y=45,width=40,height=20)
        
        btn_plt_salvar_xy = Button(frm_plot_xy, text=' Salvar último\nMapa de Calor')
        btn_plt_salvar_xy.place(x=5,y=555,width=225,height=40)
        btn_plt_salvar_xy['command'] = self.plot_salva
        
        #--Apresentação do mapa de calor
        self.frm_heatmap_xy = Labelframe(self.frm_notebook_xy, text='Mapa de calor Normalizada')
        self.frm_heatmap_xy.place(x=260,y=5,width=805,height=680)

        
        #Constantes e inicializações
        self.lista_serial()
        self.att_matriz()
        
        
    #Função para atualizar lista das portas COM
    def lista_serial(self):        
        portas=controle_cnc.list_serial()
        
        self.cmb_analisador['values'] = portas
        self.cmb_analisador.set('Escolha...')
        
        self.cmb_cnc['values'] = portas
        self.cmb_cnc.set('Escolha...')
        
        self.cmb_gerador['values'] = portas
        self.cmb_gerador.set('Escolha...')

    #Função para iniciar comunicação com analisador
    def abrir_visa_analisador(self):
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_analisador.get()
        self.visa_analisador = controle_analisador.open_visa_analisador(com_port, self.visa_analisador)
        
        if(self.visa_analisador==None):
            self.btn_open_analisador['text'] = 'Abrir'
        else:
            self.btn_open_analisador['text'] = 'Fechar'
        self.att_freq()
    
    #Função leitura amplitude do analisador
    def leitura_amplitude(self):
        return controle_analisador.receiver_amplitude(self.visa_analisador)
        
    #Função para abrir porta serial da CNC
    def abrir_serial_cnc(self):
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
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', self.cmb_step.get())
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
            
    #Função de motivmento durante medição        
    def meas_movimento_cnc(self, direcao, step):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', str(step))
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de envio comandos para serial CNC
    def envia_cmd_cnc(self):
        if (self.serial_cnc != None):
            str_comando=self.ent_cmd.get()
            
            str_resposta=controle_cnc.send_cmd(str_comando, self.serial_cnc)
            
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de evento de "ENTER"       
    def comp_s(self, event):
        self.envia_cmd_cnc()
    
    #Função para verificar se está medindo     
    def verifica_medicao(self):
        #Caso esteja medindo acusa erro e retorna true para if de break
        if (self.flag_medindo):
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função\ndurante a medição")
            return True
        else:
            return False
        
    def janela_configuracao(self):
        # Funcao para abrir pop up window
        top= Toplevel()
        top.geometry("250x300")
        top.title("Configuração")
        
        lbl_top_01 = Label(top, text='Frequência:')
        lbl_top_01.place(x=5,y=3,width=90,height=20)
        
        self.var_freq=Entry(top)
        self.var_freq.insert(END, '%d' % 25)
        self.var_freq.place(x=73,y=3,width=63,height=20)
        
        self.cmb_freq = Combobox(top)
        self.cmb_freq.place(x=143,y=3,width=60,height=20)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(top, text='Atualizar')
        self.btn_freq_refresh.place(x=72,y=27,width=132,height=25)
        self.btn_freq_refresh['command'] = self.att_freq
        
        lbl_top_02 = Label(top, text='Frequência\ndo Gerador:')
        lbl_top_02.place(x=5,y=53,width=150,height=50)
        
        self.var_freq_ger=Entry(top)
        self.var_freq_ger.insert(END, '%d' % 25)
        self.var_freq_ger.place(x=73,y=58,width=63,height=20)
        
        self.cmb_freq_ger = Combobox(top)
        self.cmb_freq_ger.place(x=143,y=58,width=60,height=20)
        self.cmb_freq_ger['values'] = ['GHz','MHz','KHz']
        self.cmb_freq_ger.current(1)
        
        self.btn_freq_ger_refresh = Button(top, text='Atualizar')
        self.btn_freq_ger_refresh.place(x=72,y=82,width=132,height=25)
        self.btn_freq_ger_refresh['command'] = self.att_freq
 
        lbl_top_03 = Label(top, text='Impedancia:')
        lbl_top_03.place(x=5,y=115,width=90,height=20)
        
        self.var_imped=Entry(top)
        self.var_imped.insert(END, '%d' % 25)
        self.var_imped.place(x=73,y=113,width=63,height=20)
        
        self.cmb_imped = Combobox(top)
        self.cmb_imped.place(x=143,y=113,width=60,height=20)
        self.cmb_imped['values'] = ['GHz','MHz','KHz']
        self.cmb_imped.current(1)
        
        self.btn_imped_refresh = Button(top, text='Atualizar')
        self.btn_imped_refresh.place(x=72,y=137,width=132,height=25)
        self.btn_imped_refresh['command'] = self.att_freq
        
        lbl_top_04 = Label(top, text='Amplitude:')
        lbl_top_04.place(x=5,y=165,width=90,height=20)
        
        self.var_amplit=Entry(top)
        self.var_amplit.insert(END, '%d' % 25)
        self.var_amplit.place(x=73,y=168,width=63,height=20)
        
        self.cmb_amplit = Combobox(top)
        self.cmb_amplit.place(x=143,y=168,width=60,height=20)
        self.cmb_amplit['values'] = ['GHz','MHz','KHz']
        self.cmb_amplit.current(1)
        
        self.btn_amplit_refresh = Button(top, text='Atualizar')
        self.btn_amplit_refresh.place(x=72,y=192,width=132,height=25)
        self.btn_amplit_refresh['command'] = self.att_freq

        self.btn_output_refresh = Button(top, text='Ligar Saída')
        self.btn_output_refresh.place(x=72,y=247,width=132,height=30)
        self.btn_output_refresh['command'] = self.att_freq
        
    #Função se string contem somente numero e maior que zero     
    def verifica_string(self, string, mensagem):
        #Caso string contem somente numero
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
        #Caso numero comece com sinal negativo
        if(string[0]=='-'):
            string=string.replace('-','0',1)
        if not(string.isdigit()):#verifica se é somente digito
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal'))
            return True
        return False
       
    
    #Função de definição de ponto 1
    def start_point(self):
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x, self.start_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Funções de definição de ponto 2
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x, self.end_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Função para atualiza passo entre medidas
    def atualiza_passo(self):
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
        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            self.flag_medindo=False
    
    """Possivelmente não sendo mais usada"""
#     #Função de ativação flag de pausa medição
#     def pause_meas(self):
#         if(self.flag_medindo):
#             if not (self.flag_stop):
#                 #envia para o arduino parar
#                 self.flag_stop=True
#             else :
#                 self.btn_pause.config(text=('Continuar'))
#                 pass # AQUI ENTRA CONTINUAÇÃO DA MEDIÇÃO
    
    #Função para atualziar tamanho da matriz
    def att_matriz(self):
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
            self.frame2_x.destroy()
            self.canvas_x.destroy()
            self.buttons_frame_x.destroy()
            self.frame2_y.destroy()
            self.canvas_y.destroy()
            self.buttons_frame_y.destroy()
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    self.button_matriz_x[i][j].destroy()
                    self.button_matriz_y[i][j].destroy()
                    
        #//////////////////////////////////////////////////////////////////////////////////
        
        self.frm_tabela = Frame(self.frm_notebook1)
        self.frm_tabela.place(x=460,y=55,width=608,height=590)
        
        notebook = Notebook(self.frm_tabela)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook_x = Frame(notebook)
        self.frm_notebook_y = Frame(notebook)
        self.frm_notebook_x.pack(fill=BOTH, expand=True)
        self.frm_notebook_y.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook_x, text='      X      ')
        notebook.add(self.frm_notebook_y, text='      Y      ')   
        
        # Cria o frame para area dos botões e scrollbar
        self.frame2_x = Frame(self.frm_notebook_x)
        self.frame2_x.grid(row=3, column=0, sticky=NW)
        self.frame2_y = Frame(self.frm_notebook_y)
        self.frame2_y.grid(row=3, column=0, sticky=NW)
        
        # Cria area dos botões
        self.canvas_x = Canvas(self.frame2_x)
        self.canvas_x.grid(row=0, column=0)
        self.canvas_y = Canvas(self.frame2_y)
        self.canvas_y.grid(row=0, column=0)
        
        # Cria scrollbar vertical e anexa a area de botões
        vsbar_x = Scrollbar(self.frame2_x, orient=VERTICAL, command=self.canvas_x.yview)
        vsbar_x.grid(row=0, column=1, sticky=NS)
        self.canvas_x.configure(yscrollcommand=vsbar_x.set)
        vsbar_y = Scrollbar(self.frame2_y, orient=VERTICAL, command=self.canvas_y.yview)
        vsbar_y.grid(row=0, column=1, sticky=NS)
        self.canvas_y.configure(yscrollcommand=vsbar_y.set)
        
        # Cria scrollbar horizontal e anexa a area de botões
        hsbar_x = Scrollbar(self.frame2_x, orient=HORIZONTAL, command=self.canvas_x.xview)
        hsbar_x.grid(row=1, column=0, sticky=EW)
        self.canvas_x.configure(xscrollcommand=hsbar_x.set)
        hsbar_y = Scrollbar(self.frame2_y, orient=HORIZONTAL, command=self.canvas_y.xview)
        hsbar_y.grid(row=1, column=0, sticky=EW)
        self.canvas_y.configure(xscrollcommand=hsbar_y.set)

        # Cria frame que contem os botões
        self.buttons_frame_x = Frame(self.canvas_x)
        self.buttons_frame_y = Frame(self.canvas_y)
        
        # Cria matriz de botões
        self.button_matriz_x = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        self.button_matriz_y = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        
        # Adiciona botões no frame
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz_x[i][j] = Button(self.buttons_frame_x, text="mX[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz_x[i][j].grid(row=i, column=j)
                self.button_matriz_x[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2,False)
                self.button_matriz_y[i][j] = Button(self.buttons_frame_y, text="mY[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz_y[i][j].grid(row=i, column=j)
                self.button_matriz_y[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2,True)
        
        # Cria janela para os botões
        self.canvas_x.create_window((0,0), window=self.buttons_frame_x, anchor=NW)
        self.canvas_y.create_window((0,0), window=self.buttons_frame_y, anchor=NW)

        self.buttons_frame_x.update_idletasks()  # Needed to make bbox info available.
        bbox_x = self.canvas_x.bbox(ALL)  # Get bounding box of canvas with Buttons.
        self.buttons_frame_y.update_idletasks()  # Needed to make bbox info available.
        bbox_y = self.canvas_y.bbox(ALL)  # Get bounding box of canvas with Buttons.

        # Define the scrollable region as entire canvas with only the desired
        # number of rows and columns displayed.
        w_x, h_x = bbox_x[2]-bbox_x[1], bbox_x[3]-bbox_x[1]
        dw_x, dh_x = int((w_x/int(valor_x)) * self.cols_disp), int((h_x/int(valor_y)) * self.rows_disp)
        self.canvas_x.configure(scrollregion=bbox_x, width=dw_x, height=dh_x)
        w_y, h_y = bbox_y[2]-bbox_y[1], bbox_y[3]-bbox_y[1]
        dw_y, dh_y = int((w_y/int(valor_x)) * self.cols_disp), int((h_y/int(valor_y)) * self.rows_disp)
        self.canvas_y.configure(scrollregion=bbox_y, width=dw_y, height=dh_y)
        
        #//////////////////////////////////////////////////////////////////////////////////
                
        self.cols=int(valor_x)
        self.rows=int(valor_y)
        self.matrix_meas_y = np.full((self.rows, self.cols), -5)
        self.matrix_meas_x = np.full((self.rows,self.cols), 5)
        self.atualiza_passo()
        
    
    #Função de re medição de ponto
    def medir_ponto(self,row,col,sentido):
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
            time.sleep(1) #colocar delay
            
        y=y-(self.var_step_y*row)-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            time.sleep(1) #colocar delay
        
        if(sentido):
            self.matrix_meas_x[row][col]=self.leitura_amplitude()
            self.button_matriz_x[row][col].config(text="\nx="+str(self.matrix_meas_x[row][col])+" dBm\n")
            if(self.matrix_meas_x[i][j] > self.max_medido_x):
                self.max_medido_x = self.matrix_meas_x[i][j]
                self.lbl_par_13['text'] = str(self.max_medido_x)
            if(self.matrix_meas_x[i][j] < self.min_medido_x):
                self.min_medido_x = self.matrix_meas_x[i][j]
                self.lbl_par_14['text'] = str(self.min_medido_x)                        
        else:
            self.matrix_meas_y[row][col]=self.leitura_amplitude()
            self.button_matriz_y[row][col].config(text="\ny="+str(self.matrix_meas_y[row][col])+" dBm\n")
            if(self.matrix_meas_y[i][j] > self.max_medido_y):
                self.max_medido_y = self.matrix_meas_y[i][j]
                self.lbl_par_13['text'] = str(self.max_medido_y)
            if(self.matrix_meas_y[i][j] < self.min_medido_y):
                self.min_medido_y = self.matrix_meas_y[i][j]
                self.lbl_par_14['text'] = str(self.min_medido_y)
        self.flag_medindo=False
        
    #Função comunicação com analisador para definição
    #frequencia de medição
    def att_freq(self):
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
    def medicao(self,sentido):
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
        self.meas_time = 0
        self.meas_time = datetime.now()
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
                time.sleep(0.125)
            
        y=y-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                time.sleep(0.125)
                
        if not(sentido):
            #self.matrix_meas_y = [[-80 for _ in range(self.cols)] for _ in range(self.rows)]
            print('Criando matriz x')
            self.max_medido_y, self.min_medido_y = -99, 0
            print('zero y')
            self.lbl_par_13['text'] = str(self.max_medido_y)
            self.lbl_par_14['text'] = str(self.min_medido_y)
            
        else:
            #self.matrix_meas_x = [[-80 for _ in range(self.cols)] for _ in range(self.rows)]
            print('Criando matriz y')
            self.max_medido_x, self.min_medido_x = -99, 0
            print('zero x')
            self.lbl_par_15['text'] = str(self.max_medido_x)
            self.lbl_par_16['text'] = str(self.min_medido_x)
            
        var_progressbar=0
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
                    if not(sentido):
                        self.matrix_meas_x[i][j]=self.leitura_amplitude()
                        if(self.matrix_meas_x[i][j] > self.max_medido_x):
                            self.max_medido_x = self.matrix_meas_x[i][j]
                            self.lbl_par_13['text'] = str(self.max_medido_x)
                        if(self.matrix_meas_x[i][j] < self.min_medido_x):
                            self.min_medido_x = self.matrix_meas_x[i][j]
                            self.lbl_par_14['text'] = str(self.min_medido_x)                        
                        self.button_matriz_x[i][j].config(text="\n"+str(self.matrix_meas_x[i][j])+" dBm\n")
                    else:
                        self.matrix_meas_y[i][j]=self.leitura_amplitude()
                        if(self.matrix_meas_y[i][j] > self.max_medido_y):
                            self.max_medido_y = self.matrix_meas_y[i][j]
                            self.lbl_par_15['text'] = str(self.max_medido_y)
                        if(self.matrix_meas_y[i][j] < self.min_medido_y):
                            self.min_medido_y = self.matrix_meas_y[i][j]
                            self.lbl_par_16['text'] = str(self.min_medido_y)
                        self.button_matriz_y[i][j].config(text="\n"+str(self.matrix_meas_y[i][j])+" dBm\n")
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
                        #time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['right'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
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
                    if not(sentido):
                        self.matrix_meas_x[i][j]=self.leitura_amplitude()
                        if(self.matrix_meas_x[i][j] > self.max_medido_x):
                            self.max_medido_x = self.matrix_meas_x[i][j]
                            self.lbl_par_13['text'] = str(self.max_medido_x)
                        if(self.matrix_meas_x[i][j] < self.min_medido_x):
                            self.min_medido_x = self.matrix_meas_x[i][j]
                            self.lbl_par_14['text'] = str(self.min_medido_x)
                        self.button_matriz_x[i][j].config(text="\n"+str(self.matrix_meas_x[i][j])+" dBm\n")
                    else:
                        self.matrix_meas_y[i][j]=self.leitura_amplitude()
                        if(self.matrix_meas_y[i][j] > self.max_medido_y):
                            self.max_medido_y = self.matrix_meas_y[i][j]
                            self.lbl_par_15['text'] = str(self.max_medido_y)
                        if(self.matrix_meas_y[i][j] < self.min_medido_y):
                            self.min_medido_y = self.matrix_meas_y[i][j]
                            self.lbl_par_16['text'] = str(self.min_medido_y)
                        self.button_matriz_y[i][j].config(text="\n"+str(self.matrix_meas_y[i][j])+" dBm\n")
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
                        #time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['left'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                            time.sleep(0.125)
                flag_ordem=True
            if(i+1<self.rows):
                #time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                self.meas_movimento_cnc(self.dict_jog['down'], self.var_step_y)
                while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                    time.sleep(0.125)
         
        """Calcula determinante das matrizes x e y"""
        detx = np.linalg.det(self.matrix_meas_x) # Calcula determinante da matriz x
        dety = np.linalg.det(self.matrix_meas_y) # Calcula determinante da matriz y

        """Coloca as matrizes em variaveis globais"""
        if (detx != 0):
            self.matrix_realx = self.matrix_meas_x            
        if (dety != 0):
            self.matrix_realy = self.matrix_meas_y
            
        if (sentido):
            messagebox.showwarning(title="Mudar Eixo",
                message="Posicione o eixo da antena para a posição X")
        else:
            messagebox.showwarning(title="Mudar Eixo",
                message="Posicione o eixo da antena para a posição Y")
        self.flag_medindo=False
    
    #Função para salvar arquivo com extensão csv
    def save(self):
        try:
            self.meas_time.strftime
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+
                       self.meas_time.strftime("_X_%d-%m-%Y_%H-%M")+".csv")
            
            #Abrir arquivo csv mode "write"
            file = open(file_path, 'w', newline ='') 

            #Escreve resultado da medida no arquivo csv
            with file:
                write = csv.writer(file, delimiter=';') 
                write.writerows(self.matrix_meas_x)
            
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+
                       self.meas_time.strftime("_Y_%d-%m-%Y_%H-%M")+".csv")
            
            #Abrir arquivo csv mode "write"
            file = open(file_path, 'w', newline ='') 

            #Escreve resultado da medida no arquivo csv
            with file:
                write = csv.writer(file, delimiter=';') 
                write.writerows(self.matrix_meas_y)
            
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Medida não realizada", message="Nenhuma informação para salvar ")
    
    #Função de homing
    def vai_origem(self):
        if(self.verifica_medicao()):
            return
        controle_cnc.cnc_jog('$H',self.serial_cnc)
        time.sleep(5)
        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
            time.sleep(0.05)
        
    #Função de alteração da flag de plot da grade (Aba mapa de calor X)
    def plot_grade(self):
        if(self.flag_grade):
            self.btn_plt_grade.config(text='        Grade\nDESABILITADO')
            self.flag_grade=False
        else:
            self.btn_plt_grade.config(text='      Grade\nHABILITADO')
            self.flag_grade=True

    #Função de alteração da flag de plot da grade (Aba mapa de calor XY)
    def plot_grade_y(self):
        if(self.flag_grade_y):
            self.btn_plt_grade_y.config(text='        Grade\nDESABILITADO')
            self.flag_grade_y=False
        else:
            self.btn_plt_grade_y.config(text='      Grade\nHABILITADO')
            self.flag_grade_y=True
            
    #Função de alteração da flag de plot da grade (Aba mapa de calor XY)
    def plot_grade_xy(self):
        if(self.flag_grade_xy):
            self.btn_plt_grade_xy.config(text='        Grade\nDESABILITADO')
            self.flag_grade_xy=False
        else:
            self.btn_plt_grade_xy.config(text='      Grade\nHABILITADO')
            self.flag_grade_xy=True
    
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_anotacao(self):     
        if(self.flag_anotacao):
            self.btn_plt_anotacao.config(text='     Anotação\nDESABILITADO')
            self.flag_anotacao=False
        else:
            self.btn_plt_anotacao.config(text='   Anotação\nHABILITADO')
            self.flag_anotacao=True
            
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_anotacao_y(self):     
        if(self.flag_anotacao_y):
            self.btn_plt_anotacao_y.config(text='     Anotação\nDESABILITADO')
            self.flag_anotacao_y=False
        else:
            self.btn_plt_anotacao_y.config(text='   Anotação\nHABILITADO')
            self.flag_anotacao_y=True
            
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_anotacao_xy(self):     
        if(self.flag_anotacao_xy):
            self.btn_plt_anotacao_xy.config(text='     Anotação\nDESABILITADO')
            self.flag_anotacao_xy=False
        else:
            self.btn_plt_anotacao_xy.config(text='   Anotação\nHABILITADO')
            self.flag_anotacao_xy=True
            
    #Função de alteração da flag de plot das anotações nos eixos (Aba do mapa de calor X)
    def plot_auto_maxmin(self):     
        if(self.flag_auto_maxmin):
            self.btn_plt_maxmin.config(text='MAX/MIN automático DESABILITADO')
            self.flag_auto_maxmin=False
        else:
            self.btn_plt_maxmin.config(text='MAX/MIN automático HABILITADO')
            self.flag_auto_maxmin=True
            
    #Função de alteração da flag de plot das anotações nos eixos (Aba do mapa de calor y)
    def plot_auto_maxmin_y(self):     
        if(self.flag_auto_maxmin_y):
            self.btn_plt_maxmin_y.config(text='MAX/MIN automático DESABILITADO')
            self.flag_auto_maxmin_y=False
        else:
            self.btn_plt_maxmin_y.config(text='MAX/MIN automático HABILITADO')
            self.flag_auto_maxmin_y=True
            
    #Função de alteração da flag de plot das anotações nos eixos (Aba do mapa de calor xy)
    def plot_auto_maxmin_xy(self):     
        if(self.flag_auto_maxmin_xy):
            self.btn_plt_maxmin_xy.config(text='MAX/MIN automático DESABILITADO')
            self.flag_auto_maxmin_xy=False
        else:
            self.btn_plt_maxmin_xy.config(text='MAX/MIN automático HABILITADO')
            self.flag_auto_maxmin_xy=True
            
    #Função de apresentação do mapa de calor para o dado medida realizada
    def plot_dadoatual(self):
     
        #função que verifica se é numero
        if not(self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        try:
            
            det_measx = np.linalg.det(self.matrix_meas_x)
#             if (det_measx == 0):
#                 messagebox.showwarning(title="Erro Ação impossivel",
#                 message="Não é possivel realizar está função\nsem a medição")
#                 return
            data=self.matrix_meas_x

        except:
            #erro no dado atual
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(map(max,data))
            vmin=min(map(min,data))
        else:
            vmax=int(self.var_plot_max.get())
            vmin=int(self.var_plot_min.get())
        step=[self.var_step_x, self.var_step_y]
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
        flag_norm = True
        
        #plot com streamplot
        y=[]
        x=[]
        temp=[]
        x_tamanho, y_tamanho = 0, 0

        for temp in data:
            y_tamanho = y_tamanho + 1
            for celula in temp:
                celula = pow(10, celula/20)
                x.append(celula)
                y.append(0)
                x_tamanho = x_tamanho + 1
        x_tamanho = int(x_tamanho/y_tamanho)
      
        
        X = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                X.append(j)

        Y = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                Y.append(i)
        
        #plot com quiver
        norm = []
        for j in range(len(x)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux)
            
        # Variaveis que serão usada para a criação do grafico normalizado
        self.x_x = x
        self.x_X = X
        self.x_xtamanho = x_tamanho
        self.x_xmax = vmax
        self.x_xmin = vmin
        self.x_data = data
 
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm)

        
        
    def plot_arquivo_csv(self):
        
        x=[]
        y=[]
        data=[]
        x_tamanho, y_tamanho = 0, 0
        flag_norm = True
        plt.clf() # limpa plot passado
        
        #função que verifica se é numero
        if not(self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        
        data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))

        with open(data_caminho, 'r') as file:
            reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
            for row in reader: # each row is a list
                y_tamanho = y_tamanho + 1
                data.append(row)
                for celula in row:
                    x_tamanho = x_tamanho + 1
                    if(flag_norm):
                        celula = pow(10, celula/20)
                    x.append(celula)
                    y.append(0)  # 0 porque o mapa gerado será apenas para x
        x_tamanho = int(x_tamanho/y_tamanho)
        
        if(self.flag_auto_maxmin):
            vmax=max(map(max,data))
            vmin=min(map(min,data))

        else:
            vmax=int(self.var_plot_max_y.get())
            vmin=int(self.var_plot_min_y.get())
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor_y.get(), self.var_plot_titulo_y.get(),
                  self.cmb_plot_interpolacao_y.get()]
        flag=[self.flag_anotacao_y, self.flag_grade_y, False]
        destino_save=None
        
        X = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                X.append(j)

        Y = []
        for i in range(y_tamanho): #reversed(range(y_tamanho)): funcao original(apagar caso não necessário)
            for j in range(x_tamanho):
                Y.append(i)

        #plot com quiver
        norm = []        
        for j in range(len(x)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux)
        
            
        # Variaveis que serão usada para a criação do grafico normalizado
        self.x_x = x
        self.x_X = X
        self.x_xtamanho = x_tamanho
        self.x_xmax = vmax
        self.x_xmin = vmin
        self.x_data = data
            
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm)
                         
        
    def plot_salva(self):
        files = [('Portable Graphics Format(PNG)', '*.png'),
                 ('All Files', '*.*')] 
        destino = filedialog.asksaveasfilename(filetypes = files, defaultextension = ".png")
        
        plt.savefig(destino,bbox_inches="tight")
        
    def mapa_de_calor(self, data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm):
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
        fig, ax = plt.subplots(2)
        
        #cor cinza de background
        if not(flag[2]):
            fig.patch.set_facecolor('#F0F0F0')
        
        #Gera mapa de calor
        im = ax[0].imshow(data, interpolation=escolhas[2], cmap=escolhas[0], vmax=vmax, vmin=vmin) 
        im2 = ax[1].imshow(data, alpha=0, vmax=vmax, vmin=vmin) #origin = 'lower' (apagar caso não necessário)
        ax[1].set_facecolor('#D3D3D3')
        plt.tight_layout() 

        
        quiveropts = dict( headlength=0, pivot='middle', headwidth=1) # common options
        plt.quiver(X,Y,x,y, norm, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fcm' % float(i*step[1]))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fcm' % float(i*step[0]))
            
        #Configuração de apresentação das anotações
        if(flag[0]):
            ax[0].set_xticks(np.arange(len(anotacao_x)))
            ax[0].set_yticks(np.arange(len(anotacao_y)))
            ax[0].set_xticklabels(anotacao_x)
            ax[0].set_yticklabels(anotacao_y)
            plt.setp(ax[0].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")
            ax[1].set_xticks(np.arange(len(anotacao_x)))
            ax[1].set_yticks(np.arange(len(anotacao_y)))
            ax[1].set_xticklabels(anotacao_x)
            ax[1].set_yticklabels(anotacao_y)
            plt.setp(ax[1].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")

        #Titulo do mapa de calor
        ax[0].set_title(escolhas[1])

        #Adiciona barra de cor
        if(len(data)>len(data[0])):
            plt.colorbar(im, shrink=1, ax=ax)
        else:
            plt.colorbar(im, shrink=0.8, ax=ax)
                    
        #Grade
        if(flag[1]):
            ax[0].grid(color='w', which='major', alpha=0.5)

        
        self.canvas2 = FigureCanvasTkAgg(fig, master = self.frm_heatmap)
        self.canvas2.draw()
        if(len(data)>=len(data[0])):
            self.canvas2.get_tk_widget().place(x=5,y=2,height=640)
        else:
            self.canvas2.get_tk_widget().place(x=5,y=2,width=790)
            
    def plot_dadoatual_y(self):
         
        #função que verifica se é numero
        if not(self.flag_auto_maxmin_y):
            if(self.verifica_numero(self.var_plot_max_y.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min_y.get(), 'MAX e MIN do plot')):
                return
        try:
            det_measy = np.linalg.det(self.matrix_meas_y)
#             if (det_measy == 0):
#                 messagebox.showwarning(title="Erro Ação impossivel",
#                 message="Não é possivel realizar está função\nsem a medição")
#                 return
            data=self.matrix_meas_y

        except:
            #erro no dado atual
            return
        
        if(self.flag_auto_maxmin_y):
            vmax=max(map(max,data))
            vmin=min(map(min,data))
        else:
            vmax=int(self.var_plot_max_y.get())
            vmin=int(self.var_plot_min_y.get())
        step=[self.var_step_x, self.var_step_y]
        escolhas=[self.cmb_plot_cor_y.get(), self.var_plot_titulo_y.get(),
                  self.cmb_plot_interpolacao_y.get()]
        flag=[self.flag_anotacao_y, self.flag_grade_y, False]
        destino_save=None
        flag_norm = True
        
        #plot com streamplot
        y=[]
        x=[]
        x_tamanho, y_tamanho = 0, 0

        for temp in data:
            y_tamanho = y_tamanho + 1
            for celula in temp:
                celula = pow(10, celula/20)
                y.append(celula)
                x.append(0)
                x_tamanho = x_tamanho + 1
        x_tamanho = int(x_tamanho/y_tamanho)
        
        
        X = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                X.append(j)

        Y = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                Y.append(i)

        #plot com quiver
        norm = []
        for j in range(len(y)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux)
                    
        # Variaveis que serão usada para a criação do grafico normalizado
        self.y_y = y
        self.y_Y = Y
        self.y_ytamanho = y_tamanho
        self.y_ymax = vmax
        self.y_ymin = vmin
        self.y_data = data
 
        self.mapa_de_calor_y(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm)

            
    def plot_arquivo_csv_y(self):
        
        x=[]
        y=[]
        data=[]
        x_tamanho, y_tamanho = 0, 0
        flag_norm = True
        plt.clf()
        
        #função que verifica se é numero
        if not(self.flag_auto_maxmin_y):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))

        with open(data_caminho, 'r') as file:
            reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
            for row in reader: # each row is a list
                y_tamanho = y_tamanho + 1
                data.append(row)
                for celula in row:
                    x_tamanho = x_tamanho + 1
                    if(flag_norm):
                        celula = pow(10, celula/20)
                    x.append(0)
                    y.append(celula)  
        x_tamanho = int(x_tamanho/y_tamanho)  
        
        if(self.flag_auto_maxmin_y):
            vmax=max(map(max,data))
            vmin=min(map(min,data))

        else:
            vmax=int(self.var_plot_max_y.get())
            vmin=int(self.var_plot_min_y.get())
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor_y.get(), self.var_plot_titulo_y.get(),
                  self.cmb_plot_interpolacao_y.get()]
        flag=[self.flag_anotacao_y, self.flag_grade_y, False]
        destino_save=None
        
        X = []
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                X.append(j)

        Y = [] # ORIGINAL reversed(range(y_tamanho))
        for i in range(y_tamanho):
            for j in range(x_tamanho):
                Y.append(i)
                
        norm = []        
        for j in range(len(x)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux)
          
            
        # Variaveis que serão usada para a criação do grafico normalizado
        self.y_y = y
        self.y_Y = Y
        self.y_ytamanho = y_tamanho
        self.y_ymax = vmax
        self.y_ymin = vmin
        self.y_data = data
        
            
        self.mapa_de_calor_y(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm)
      
    
    def plot_salva_y(self):
        files = [('Portable Graphics Format(PNG)', '*.png'),
                 ('All Files', '*.*')] 
        destino = filedialog.asksaveasfilename(filetypes = files, defaultextension = ".png")
        
        plt.savefig(destino,bbox_inches="tight")
        
    def mapa_de_calor_y(self, data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm):
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
        fig, ax = plt.subplots(2)
        
        #cor cinza de background
        if not(flag[2]):
            fig.patch.set_facecolor('#F0F0F0')
        
        #Gera mapa de calor
        im = ax[0].imshow(data, interpolation=escolhas[2], cmap=escolhas[0], vmax=vmax, vmin=vmin) 
        im2 = ax[1].imshow(data, alpha=0, vmax=vmax, vmin=vmin)
        ax[1].set_facecolor('#D3D3D3')
        plt.tight_layout() 

        
        quiveropts = dict( headlength=0, pivot='middle', headwidth=1) # common options
        plt.quiver(X,Y,x,y, norm, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fcm' % float(i*step[1]))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fcm' % float(i*step[0]))
            
        #Configuração de apresentação das anotações
        if(flag[0]):
            ax[0].set_xticks(np.arange(len(anotacao_x)))
            ax[0].set_yticks(np.arange(len(anotacao_y)))
            ax[0].set_xticklabels(anotacao_x)
            ax[0].set_yticklabels(anotacao_y)
            plt.setp(ax[0].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")
            ax[1].set_xticks(np.arange(len(anotacao_x)))
            ax[1].set_yticks(np.arange(len(anotacao_y)))
            ax[1].set_xticklabels(anotacao_x)
            ax[1].set_yticklabels(anotacao_y)
            plt.setp(ax[1].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")

        #Titulo do mapa de calor
        ax[0].set_title(escolhas[1])

        #Adiciona barra de cor
        if(len(data)>len(data[0])):
            plt.colorbar(im, shrink=1, ax=ax)
        else:
            plt.colorbar(im, shrink=0.8, ax=ax)
            
        
        #Grade
        if(flag[1]):
            ax[0].grid(color='w', which='major', alpha=0.5)

        
        self.canvas2 = FigureCanvasTkAgg(fig, master = self.frm_heatmap_y)
        self.canvas2.draw()
        if(len(data)>=len(data[0])):
            self.canvas2.get_tk_widget().place(x=5,y=2,height=640)
        else:
            self.canvas2.get_tk_widget().place(x=5,y=2,width=790)
    
    def plot_dadoatual_xy(self):
        
        #função que verifica se é numero
        if not(self.flag_auto_maxmin_xy):
            if(self.verifica_numero(self.var_plot_max_xy.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min_xy.get(), 'MAX e MIN do plot')):
                return
            
        # Varíaveis resgatadas dos eixos x e y       
        x= self.x_x
        y= self.y_y
        x_tamanho = self.x_xtamanho
        y_tamanho = self.y_ytamanho
        X = self.x_X
        Y = self.y_Y
        xmax = self.x_xmax
        xmin = self.x_xmin
        ymax = self.y_ymax
        ymin = self.y_ymin
        data = self.x_data
        flag_norm = True
        plt.clf()        
        norm = []
        data_norm = []
        

        for j in range(len(x)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux) # passa os valores para norm para ser usado no mapa de setas
        
        data_norm = np.array_split(norm,len(data))

        if(self.flag_auto_maxmin_xy):
            vmax=max(norm)
            vmin=min(norm)

        else:
            vmax=int(self.var_plot_max_xy.get())
            vmin=int(self.var_plot_min_xy.get())
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor_xy.get(), self.var_plot_titulo_xy.get(),
                  self.cmb_plot_interpolacao_xy.get()]
        flag=[self.flag_anotacao_xy, self.flag_grade_xy, False]
        destino_save=None
        
            
        self.mapa_de_calor_xy(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm, data_norm)
        
    def plot_arquivo_csv_xy(self):
        
        # Varíaveis resgatadas dos eixos x e y       
        x= self.x_x
        y= self.y_y
        x_tamanho = self.x_xtamanho
        y_tamanho = self.y_ytamanho
        X = self.x_X
        Y = self.y_Y
        xmax = self.x_xmax
        xmin = self.x_xmin
        ymax = self.y_ymax
        ymin = self.y_ymin
        data = self.x_data
        flag_norm = True
        plt.clf()
        norm = []
        data_norm = []
        
        #função que verifica se é numero
        if not(self.flag_auto_maxmin_xy):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return

        for j in range(len(x)):
            if(flag_norm):
                aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
            if not(flag_norm):
                aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
            norm.append(aux) # passa os valores para norm para ser usado no mapa de setas
        
        data_norm = np.array_split(norm,self.rows) # Original np.array_split(norm, 13)
        
        print(data)
        print(norm)
        print(len(data_norm))

        if(self.flag_auto_maxmin_xy):
            vmax=max(norm)
            vmin=min(norm)

        else:
            vmax=int(self.var_plot_max_y.get())
            vmin=int(self.var_plot_min_y.get())
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor_xy.get(), self.var_plot_titulo_xy.get(),
                  self.cmb_plot_interpolacao_xy.get()]
        flag=[self.flag_anotacao_xy, self.flag_grade_xy, False]
        destino_save=None
        
            
        self.mapa_de_calor_xy(data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm, data_norm)
        

            
        
    def mapa_de_calor_xy(self, data, vmax, vmin, step, flag, escolhas, destino_save, x , X, y ,Y, norm, data_norm):
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
        fig, ax = plt.subplots(2)
        
        #cor cinza de background
        if not(flag[2]):
            fig.patch.set_facecolor('#F0F0F0')
        
        #Gera mapa de calor
        im = ax[0].imshow(data_norm, interpolation=escolhas[2], cmap=escolhas[0], vmax=vmax, vmin=vmin) 
        im2 = ax[1].imshow(data, alpha=0, vmax=vmax, vmin=vmin)
        ax[1].set_facecolor('#D3D3D3')
        plt.tight_layout() 
        
        quiveropts = dict( headlength=0, pivot='middle', headwidth=1) # common options
        plt.quiver(X,Y,x,y, norm, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fcm' % float(i*step[1]))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fcm' % float(i*step[0]))
            
        #Configuração de apresentação das anotações
        if(flag[0]):
            ax[0].set_xticks(np.arange(len(anotacao_x)))
            ax[0].set_yticks(np.arange(len(anotacao_y)))
            ax[0].set_xticklabels(anotacao_x)
            ax[0].set_yticklabels(anotacao_y)
            plt.setp(ax[0].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")
            ax[1].set_xticks(np.arange(len(anotacao_x)))
            ax[1].set_yticks(np.arange(len(anotacao_y)))
            ax[1].set_xticklabels(anotacao_x)
            ax[1].set_yticklabels(anotacao_y)
            plt.setp(ax[1].get_xticklabels(), rotation=30, ha="right",
                     rotation_mode="anchor")

        #Titulo do mapa de calor
        ax[0].set_title(escolhas[1])

        #Adiciona barra de cor
        if(len(data)>len(data[0])):
            plt.colorbar(im, shrink=1, ax=ax)
        else:
            plt.colorbar(im, shrink=0.8, ax=ax)
            

        
        #Grade
        if(flag[1]):
            ax[0].grid(color='w', which='major', alpha=0.5)

        
        self.canvas2 = FigureCanvasTkAgg(fig, master = self.frm_heatmap_xy)
        self.canvas2.draw()
        if(len(data)>=len(data[0])):
            self.canvas2.get_tk_widget().place(x=5,y=2,height=640)
        else:
            self.canvas2.get_tk_widget().place(x=5,y=2,width=790)
            
    
            
    def all_children (self, wid) :
        widget_list = wid.winfo_children()
        for item in widget_list :
            if item.winfo_children() :
                widget_list.extend(item.winfo_children())
        for item in widget_list :
            item.destroy()
        
def resize(event):
    print("Novo tamanho é: {}x{}".format(event.width, event.height))

def main():
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
    except:
        pass
    #-------------------------------------
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()


