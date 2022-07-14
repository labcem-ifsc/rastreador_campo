import pyvisa
import serial

class controle_gerador:      
    def open_visa_gerador(com_port, visa_gerador):
        if (visa_gerador == None):
            #retirar numero da COM 
            for i in range (len(com_port)):
                if com_port[i].isnumeric():
                    break
            com_port = com_port[i:int(com_port.find(' -'))]
            #Inicialização da COM
            rm = pyvisa.ResourceManager()
            #Se não tiver uma porta COM compativel instrumento retorna False
            #para apresentação de erro,  falta de drive
            if not any(str(com_port) in i for i in rm.list_resources()):
                return False
            else:
                try:
                    my_instrument = rm.open_resource('ASRL'+str(com_port)+'::INSTR')
                except Exception as e:
                    print(e)
                    my_instrument.close()
                    return None
                #inicialização do instrumento
                my_instrument.write('OUTPut1:IMPedance 470')
                my_instrument.write('OUTPut1:STATe OFF')
                my_instrument.write('SOURce1:FREQuency:FIXed 25MHz')
                my_instrument.write('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 18')
                
                return my_instrument
        else:
            visa_gerador.close()
            return None
    
    def imp(imp_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('OUTPut1:IMPedance {}'.format(int(imp_gerador)))
        gerador.write('OUTPut1:STATe On')

    def frequencia(freq_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('SOURce1:FREQuency:FIXed {}'.format(freq_gerador))
    
    def vamp(vamp_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {}'.format(vamp_gerador))
    

        
        