class Bitwise:

    def __init__(self,cadena_bits):
        valor = int(cadena_bits, 2)
        self.valor8 = valor

    def set_bit1(self, pos):
        if pos <= 8:  
            mask = 1
            mask = mask << pos - 1
            self.valor8 = self.valor8 | mask

    def set_bit0(self, pos):
        if pos <= 8:
            mask = 1
            mask = mask << (pos - 1)
            mask = ~mask
            self.valor8 = self.valor8 & mask

    def get_bit(self, pos):
        mask = 1
        mask = mask << (pos - 1)
        mask = mask & self.valor8
        mask = mask >> pos - 1
        return mask

    def mostrar(self):
        s = "X = "
        for i in range(8,0,-1):
            s = s + "" + str(self.get_bit(i))
        return s

    def bit_a_numero(self):
        numero = 0
        for i in range(1,9):
            bit = self.get_bit(i)
            if bit == 1:
                numero = numero + (2**(i-1))
        return numero

if __name__ == "__main__":
    cadena_bits_bin = "10011101"
    mi_byte = Bitwise(cadena_bits_bin)
    print(mi_byte.mostrar())
    mi_byte.set_bit0(1)
    print(mi_byte.mostrar())