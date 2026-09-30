from claseBitwise.ClaseBitwise import Bitwise
from PIL import Image
import tkinter as tk
from tkinter import filedialog


class Foto:
    def __init__(self):
        self.img = None
        self.img_original = None
        self.lista_pixeles = []

    def pedir_guardar_imagen(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        ruta = filedialog.askopenfilename(
            title="SELECCIONA UNA IMAGEN",
            filetypes=[("Archivos de Imagen", "*.png"),
                ("Todos los archivos", "*.*")]
        )
        root.destroy()
        if ruta:
            try:
                self.img = Image.open(ruta).convert("RGB")
                self.img_original = self.img.copy()
                self.lista_pixeles = list(self.img.tobytes())
                print(f"IMAGEN CARGADA")
                print(f"TAMAÑO: {self.img.size} pixeles")
            except Exception as e:
                print(f"ERROR::NO SE PUDO ABRIR EL ARCHIVO: {e}")
        else:
            print("ERROR::NO SE SELECCIONO NINGUNA IMAGEN.")
    def texto_a_bits(self, frase):
        cad = ""
        for char in frase:
            cad = cad + f"{ord(char):08b}"
        return cad

    def encriptar(self, cad_bits):
        if not self.lista_pixeles:
            print("ERROR::NO HAY NINGUNA IMAGEN CARGADA.")
            return
        bits_mensaje = len(cad_bits)
        if bits_mensaje > len(self.lista_pixeles):
            print("ERROR::EL MENSAJE NO ENTRA.")
            return
        #insertando mensaje
        for i in range(bits_mensaje):
            bit_encriptar = cad_bits[i]
            byte_actual = self.lista_pixeles[i]
            # de byte a bin
            byte_a_bits = f"{int(byte_actual):08b}"
            bitwise_pixel = Bitwise(byte_a_bits)
            if bit_encriptar == '1':
                bitwise_pixel.set_bit1(1)
            else:
                bitwise_pixel.set_bit0(1)
            self.lista_pixeles[i] = bitwise_pixel.bit_a_numero()
        #reconstruccion
        bytes_modificados = bytes(self.lista_pixeles)
        self.img = Image.frombytes("RGB", self.img.size, bytes_modificados)

    def desencriptar(self):
        if not self.lista_pixeles:
            return "ERROR"
        bits_acumulados = ""
        mensaje = ""

        for i in range(len(self.lista_pixeles)):
            byte_actual = self.lista_pixeles[i]
            byte_a_bits = f"{int(byte_actual):08b}"
            bitwise_pixel = Bitwise(byte_a_bits)
            bit = bitwise_pixel.get_bit(1)
            bits_acumulados += str(bit)
            if len(bits_acumulados) == 8:
                cambiar_ascii = int(bits_acumulados,2)
                letra = chr(cambiar_ascii)
                if letra == "\x00":
                    break
                mensaje += letra
                bits_acumulados = ""
        return mensaje

    def mostrar_imagen(self):
        if self.img is not None:
            self.img.show()
        else:
            print("ERROR::NO HAY NINGUNA IMAGEN CARGADA")

    def comparacion(self):
        if self.img is None or self.img_original is None:
            print("ERROR:: NO HAY IMAGEN CARGADA O NO SE ENCRIPTO NADA.")
            return
        ancho, alto = self.img.size
        comparar = Image.new("RGB", (ancho * 2, alto))
        comparar.paste(self.img_original,(0,0))
        comparar.paste(self.img,(ancho,0))
        comparar.show()