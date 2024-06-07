from machine import Pin, PWM, UART
from time import sleep

# Configuración de los pines del motor
Motor_A_Adelante = Pin(18, Pin.OUT)
Motor_A_Atras = Pin(19, Pin.OUT)
Motor_B_Adelante = Pin(20, Pin.OUT)
Motor_B_Atras = Pin(21, Pin.OUT)

# Configuración PWM para los motores
PWM_A_Adelante = PWM(Motor_A_Adelante)
PWM_A_Atras = PWM(Motor_A_Atras)
PWM_B_Adelante = PWM(Motor_B_Adelante)
PWM_B_Atras = PWM(Motor_B_Atras)

# Definir frecuencia PWM
pwm_frequency = 20000
PWM_A_Adelante.freq(pwm_frequency)
PWM_A_Atras.freq(pwm_frequency)
PWM_B_Adelante.freq(pwm_frequency)
PWM_B_Atras.freq(pwm_frequency)

# Velocidad base
velocidad_base = 360

# Configuración del UART
uart = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))


def ajustar_velocidad(pwm_pin, velocidad):
    velocidad = max(0, min(int(velocidad), 1023))  # Convertir a entero para pwm.duty_u16
    pwm_pin.duty_u16(velocidad * 64)
    print("Ajustar velocidad:", pwm_pin, "a", velocidad)
    
def detener_motores():
    # Detener ambos motores
    PWM_A_Adelante.duty_u16(0)
    PWM_A_Atras.duty_u16(0)
    PWM_B_Adelante.duty_u16(0)
    PWM_B_Atras.duty_u16(0)
    print("Motores detenidos")

def ajustar_motores(desviacion):
    # Calcula la velocidad ajustada para cada motor basado en la desviación
    velocidad_a = velocidad_base - (desviacion * 2.5)
    velocidad_b = velocidad_base + (desviacion * 2.5)
    
    # Ajusta las velocidades dentro del rango permitido
    velocidad_a = max(320, min(velocidad_a, 1023))
    velocidad_b = max(320, min(velocidad_b, 1023))
    
    ajustar_velocidad(PWM_A_Adelante, velocidad_a)
    ajustar_velocidad(PWM_B_Adelante, velocidad_b)
    
    print(f"Desviación: {desviacion}, Velocidad A: {velocidad_a}, Velocidad B: {velocidad_b}")

while True:
    if uart.any():
        try:
            # Leer una línea completa del buffer UART
            comando = uart.readline().decode('utf-8').strip()
            print(f"Comando recibido: {comando}")
            
            # Intentar convertir el comando a un número de punto flotante
            desviacion = float(comando)
            ajustar_motores(desviacion)
            
            # Esperar un breve instante
            sleep(0.1)  # Tiempo de pausa, ajusta según tus necesidades
            
            # Detener los motores
            detener_motores()
            
            
        except ValueError:
            print("Comando inválido recibido:", comando)
    
    #sleep(0.09)
    
    
    