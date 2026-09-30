import math


class AnalizadorChiCuadrado:
    """Analiza el equilibrio de pares de valores que puede producir LSB."""

    @staticmethod
    def formatear_p_valor(p_valor):
        if p_valor != p_valor:
            return "no calculable"
        if p_valor == 0.0:
            return "< 5e-324 (bajo el limite numerico)"
        return f"{p_valor:.3e}"

    @staticmethod
    def _gamma_q(a, x):
        """Calcula la gamma incompleta regularizada Q(a, x)."""
        if x == 0:
            return 1.0

        factor = math.exp(-x + a * math.log(x) - math.lgamma(a))
        epsilon = 1e-14
        limite = 1000

        if x < a + 1:
            termino = suma = 1.0 / a
            parametro = a
            for _ in range(limite):
                parametro += 1
                termino *= x / parametro
                suma += termino
                if abs(termino) < abs(suma) * epsilon:
                    break
            return min(1.0, max(0.0, 1.0 - suma * factor))

        minimo = 1e-300
        b = x + 1 - a
        c = 1.0 / minimo
        d = 1.0 / b
        fraccion = d
        for indice in range(1, limite + 1):
            coeficiente = -indice * (indice - a)
            b += 2
            d = coeficiente * d + b
            if abs(d) < minimo:
                d = minimo
            c = b + coeficiente / c
            if abs(c) < minimo:
                c = minimo
            d = 1.0 / d
            cambio = d * c
            fraccion *= cambio
            if abs(cambio - 1.0) < epsilon:
                break
        return min(1.0, max(0.0, factor * fraccion))

    @staticmethod
    def _tamanos_ventana(total, minimo=256):
        """Ventanas crecientes (dobla cada vez) desde el inicio de los bytes."""
        tamanos = []
        t = minimo
        while t < total:
            tamanos.append(t)
            t *= 2
        tamanos.append(total)
        return tamanos

    def _evaluar(self, frecuencias, bytes_analizados, bytes_totales):
        """Chi-cuadrado de Westfeld-Pfitzmann sobre un histograma de bytes."""
        estadistico = 0.0
        pares_usados = 0
        for v in range(0, 256, 2):
            n0, n1 = frecuencias[v], frecuencias[v + 1]
            total = n0 + n1
            if total / 2 >= 5:  # esperado >= 5
                estadistico += (n0 - n1) ** 2 / (2 * total)
                pares_usados += 1

        grados_libertad = pares_usados - 1
        if grados_libertad < 1:
            return {
                "chi_cuadrado": estadistico,
                "grados_libertad": max(grados_libertad, 0),
                "p_valor": float("nan"),
                "bytes_analizados": bytes_analizados,
                "bytes_totales": bytes_totales,
                "interpretacion": "Datos insuficientes para aplicar el test en esta ventana.",
            }

        p_valor = self._gamma_q(grados_libertad / 2, estadistico / 2)
        if p_valor >= 0.95:
            interpretacion = (
                "Equilibrio por pares muy alto, compatible con reemplazo LSB; "
                "no confirma por sí solo que exista un mensaje."
            )
        elif p_valor < 0.05:
            interpretacion = (
                "Las frecuencias no muestran el equilibrio esperado para reemplazo LSB. "
                "Esto no descarta mensajes parciales ni otros métodos o canales."
            )
        else:
            interpretacion = (
                "Resultado inconcluso: este análisis no aporta evidencia suficiente "
                "para clasificar la imagen."
            )
        return {
            "chi_cuadrado": estadistico,
            "grados_libertad": grados_libertad,
            "p_valor": p_valor,
            "bytes_analizados": bytes_analizados,
            "bytes_totales": bytes_totales,
            "interpretacion": interpretacion,
        }

    def analizar(self, imagen, limite_bytes=None):
        """Chi-cuadrado sobre los primeros `limite_bytes` bytes (todos si es None)."""
        datos = imagen.convert("RGB").tobytes()
        total = len(datos)
        if limite_bytes:
            datos = datos[:limite_bytes]
        frecuencias = [0] * 256
        for b in datos:
            frecuencias[b] += 1
        return self._evaluar(frecuencias, len(datos), total)

    def analizar_progresivo(self, imagen):
        """Analiza ventanas crecientes desde el inicio.

        Devuelve (mejor, ventanas): `mejor` es la ventana con mayor p-valor
        (la más compatible con LSB) y `ventanas` la lista completa.
        """
        datos = imagen.convert("RGB").tobytes()
        total = len(datos)
        frecuencias = [0] * 256
        ventanas = []
        inicio = 0
        for fin in self._tamanos_ventana(total):
            for b in datos[inicio:fin]:
                frecuencias[b] += 1
            inicio = fin
            ventanas.append(self._evaluar(frecuencias, fin, total))
        validas = [v for v in ventanas if v["p_valor"] == v["p_valor"]]
        mejor = max(validas, key=lambda v: v["p_valor"]) if validas else ventanas[-1]
        return mejor, ventanas
