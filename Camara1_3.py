import sys
import time
import digitalio
import busio
import board
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
)

# Configuración de la cámara
cam_bus = busio.I2C(board.GP21, board.GP20)

cam = OV7670(
    cam_bus,
    data_pins=[
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
    ],
    clock=board.GP8,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP9,
    shutdown=board.GP15,
    reset=board.GP14,
)
cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True

print(cam.width, cam.height)

buf = bytearray(2 * cam.width * cam.height)
print('##################################')
cam.capture(buf)
print(len(list(buf)))

chars = b" .:-=+*#%@"

width = cam.width
row = bytearray(2 * width)

# Configuración del UART
uart = busio.UART(board.GP16, board.GP17, baudrate=115200)  # Ajusta los pines y la velocidad según sea necesario

# Valores mínimos y máximos para normalización
desviacion_min = -195
desviacion_max = 195

while True:
    cam.capture(buf)
    for j in range(cam.height):
        for i in range(cam.width):
            # Asegurar que el valor sea válido en el rango de un byte
            value = max(0, min(255, 225 - buf[2 * (width * j + i)]))
            row[i * 2] = row[i * 2 + 1] = value
        #print(list(row[0:40]))
        
    mul = []

    for x in range(40):
        y = row[x] * (x + 1)
        mul.append(y)
    
    sum_mul = sum(mul)
    sum_cam = sum(row[0:40])
    
    print("sum_mul", sum_mul)
    print(sum_cam)
    
    if sum_cam != 0:
        p_medio = sum_mul / sum_cam
        print(p_medio)
        
        desviacion = (20.5 - p_medio) * 10
        print("desviacion", desviacion)
        
        # Normalizar la desviación
        desviacion_normalizada = ((desviacion - desviacion_min) / (desviacion_max - desviacion_min)) * 200 - 100
        unu = int (desviacion_normalizada)
        print("desviacion_normalizada", unu)
        
        # Enviar la desviación normalizada por UART
        uart.write(f"{unu:.2f}\n".encode('utf-8'))
    else:
        # Enviar un valor de error o una desviación neutra si sum_cam es 0
        uart.write("0.00\n".encode('utf-8'))
    
    print()
    #time.sleep(2)
