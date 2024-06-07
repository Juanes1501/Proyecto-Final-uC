from machine import Pin, PWM, UART
from time import sleep
import array
import random
import json

class Matrix:
    def __init__(self, m, n, data=None):
        self.m = m
        self.n = n
        if data is None:
            self.data = array.array('f', [0.0] * (n * m))
        else:
            if len(data) != n * m:
                raise ValueError("Incorrect data length")
            self.data = array.array('f', data)

    def __getitem__(self, index):
        if isinstance(index, tuple):
            i, j = index
            if isinstance(i, int) and isinstance(j, int):
                if 0 <= i < self.m and 0 <= j < self.n:
                    return self.data[i * self.n + j]
                else:
                    raise IndexError("Matrix indices out of range")
            if isinstance(i, slice) and isinstance(j, slice):
                start_i, stop_i, step_i = i.indices(self.m)
                start_j, stop_j, step_j = j.indices(self.n)
                sliced_data = [self.data[r * self.n + c] for r in range(start_i, stop_i, step_i) for c in range(start_j, stop_j, step_j)]
                return Matrix(stop_i - start_i, stop_j - stop_j, sliced_data)
            else:
                raise IndexError("i,j indices are required")
        else:
            raise ValueError("i,j indices are required")

    def __setitem__(self, index, value):
        i, j = index
        if 0 <= i < self.m and 0 <= j < self.n:
            self.data[i * self.n + j] = value
        else:
            raise IndexError("Matrix indices out of range")

    def __add__(self, other):
        if isinstance(other, Matrix) and self.n == other.n and self.m == other.m:
            result = Matrix(self.m, self.n)
            for i in range(self.m):
                for j in range(self.n):
                    result[i, j] = self[i, j] + other[i, j]
            return result
        else:
            raise ValueError("Matrices of different dimensions cannot be added")

    def __sub__(self, other):
        if isinstance(other, Matrix) and self.n == other.n and self.m == other.m:
            result = Matrix(self.m, self.n)
            for i in range(self.m):
                for j in range(self.n):
                    result[i, j] = self[i, j] - other[i, j]
            return result
        else:
            raise ValueError("Matrices of different dimensions cannot be subtracted")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = Matrix(self.m, self.n)
            for i in range(self.m):
                for j in range(self.n):
                    result[i, j] = self[i, j] * other
            return result
        elif isinstance(other, Matrix):
            if self.n != other.m:
                raise ValueError("Number of columns of first matrix must be equal to number of rows of second matrix")
            result = Matrix(self.m, other.n)
            for i in range(self.m):
                for j in range(other.n):
                    for k in range(self.n):
                        result[i, j] += self[i, k] * other[k, j]
            return result
        else:
            raise ValueError("Multiplication not defined for these data types")

    def T(self):
        transposed_data = array.array('f', [0.0] * (self.n * self.m))
        for i in range(self.m):
            for j in range(self.n):
                transposed_data[j * self.m + i] = self.data[i * self.n + j]
        return Matrix(self.n, self.m, transposed_data)
    
    def __or__(self, other):
        if isinstance(other, Matrix) and self.n == other.n:
            return Matrix(self.m + other.m, self.n, self.data + other.data)
        else:
            raise ValueError("Matrices of different dimensions cannot be added")

    def __and__(self, other):
        if self.m != other.m:
            raise ValueError("Matrices must have the same number of rows to concatenate horizontally")
        
        concatenated_data = []
        for i in range(self.m):
            concatenated_data.extend(self.data[i*self.n : (i+1)*self.n])
            concatenated_data.extend(other.data[i*other.n : (i+1)*other.n])

        return Matrix(self.m, self.n + other.n, concatenated_data)

    def __str__(self):
        output = ""
        for i in range(self.m):
            row_str = " ".join(str(self[i, j]) for j in range(self.n))
            output += row_str + "\n"
        return output

class Perceptron:
    def __init__(self, input_size, output_size):
        self.weights = Matrix(input_size, output_size, [random.random() for _ in range(input_size * output_size)])
        self.bias = Matrix(1, output_size, [random.random() for _ in range(output_size)])

    def predict(self, inputs):
        result = inputs * self.weights + self.bias
        return result

    def train(self, inputs, labels, learning_rate=0.1, epochs=1):
        for epoch in range(epochs):
            predictions = self.predict(inputs)
            error = labels - predictions
            self.weights += inputs.T() * error * learning_rate
            self.bias += error * learning_rate

    def save(self, filename):
        with open(filename, 'w') as f:
            data = {
                'weights': self.weights.data.tolist(),
                'bias': self.bias.data.tolist(),
                'input_size': self.weights.m,
                'output_size': self.weights.n
            }
            json.dump(data, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.weights = Matrix(data['input_size'], data['output_size'], data['weights'])
            self.bias = Matrix(1, data['output_size'], data['bias'])

# Configuración de los pines del motor
Motor_A_Adelante = Pin(18, Pin.OUT)
Motor_A_Atras = Pin(19, Pin.OUT)
Motor_B_Adelante = Pin(21, Pin.OUT)
Motor_B_Atras = Pin(20, Pin.OUT)

PWM_A_Adelante = PWM(Motor_A_Adelante)
PWM_A_Atras = PWM(Motor_A_Atras)
PWM_B_Adelante = PWM(Motor_B_Adelante)
PWM_B_Atras = PWM(Motor_B_Atras)

pwm_frequency = 1000

PWM_A_Adelante.freq(pwm_frequency)
PWM_A_Atras.freq(pwm_frequency)
PWM_B_Adelante.freq(pwm_frequency)
PWM_B_Atras.freq(pwm_frequency)

def ajustar_velocidad(pwm_pin, velocidad):
    velocidad = max(0, min(velocidad, 1023))
    pwm_pin.duty_u16(int(velocidad * 64))

def ajustar_motores(perceptron, desviacion):
    entrada = Matrix(1, 1, [desviacion])
    salida = perceptron.predict(entrada)
    velocidad_a = 511 + salida[0, 0]
    velocidad_b = 511 - salida[0, 0]
    ajustar_velocidad(PWM_A_Adelante, velocidad_a)
    ajustar_velocidad(PWM_B_Adelante, velocidad_b)
    return velocidad_a, velocidad_b

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

perceptron = Perceptron(1, 1)
try:
    perceptron.load('perceptron_params.json')
    print("Parámetros cargados exitosamente.")
except FileNotFoundError:
    print("Archivo de parámetros no encontrado. Usando parámetros aleatorios.")

inputs = Matrix(0, 1)  # Inicialmente vacío
labels = Matrix(0, 2)  # Inicialmente vacío

while True:
    if uart.any():
        comando = uart.read().decode('utf-8').strip()
        try:
            desviacion = float(comando)
            print(f"Comando recibido: {desviacion}")
            velocidad_a, velocidad_b = ajustar_motores(perceptron, desviacion)
            
            # Agregar datos de entrenamiento
            inputs = inputs | Matrix(1, 1, [desviacion])
            labels = labels | Matrix(1, 2, [velocidad_a, velocidad_b])
            
            # Entrenar el perceptrón
            perceptron.train(inputs, labels, learning_rate=0.01, epochs=1)
            
            # Guardar parámetros entrenados
            perceptron.save('perceptron_params.json')
        except ValueError:
            print(f"Comando inválido recibido: {comando}")
    sleep(0.1)
