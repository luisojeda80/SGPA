# C:/SGPA/app/utils/rs232.py
import serial
import time
import random

def leer_peso_bascula(puerto='COM1', baudrate=9600, timeout=2, en_produccion=False):
    """
    Lee el peso de una báscula electrónica a través del puerto RS232.
    Si 'en_produccion' es False, simula la lectura para desarrollo.
    """
    if not en_produccion:
        print(f"MODO SIMULACIÓN: Leyendo peso de báscula en puerto {puerto}...")
        time.sleep(1)  # Simular retardo de la comunicación
        peso_simulado = round(random.uniform(18000.0, 32000.0), 2)
        print(f"Peso simulado obtenido: {peso_simulado} kg")
        return peso_simulado

    try:
        with serial.Serial(puerto, baudrate, timeout=timeout) as ser:
            # El comando a enviar depende del protocolo de la báscula.
            # Por ejemplo, podría ser un simple carácter como 'P' para 'Pedir Peso'.
            # ser.write(b'P\r\n') 
            
            # Esperar la respuesta
            linea_de_datos = ser.readline().decode('ascii').strip()
            
            # Procesar la línea de datos para extraer el peso.
            # Esto también depende del formato de respuesta de la báscula.
            # Ejemplo: "ST,GS,+002515.5 kg" -> Extraer '2515.5'
            if linea_de_datos:
                partes = linea_de_datos.replace(' ', '').split(',')
                for parte in partes:
                    if 'kg' in parte:
                        peso_str = parte.replace('kg', '').replace('+', '')
                        return float(peso_str)
            return None

    except serial.SerialException as e:
        print(f"Error de comunicación serial en {puerto}: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"Error al procesar los datos de la báscula: {e}")
        return None
