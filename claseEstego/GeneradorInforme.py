from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from claseEstego.AnalizadorChiCuadrado import AnalizadorChiCuadrado


class GeneradorInforme:


    MAX_BYTES_TABLA = 8000

    def __init__(self, resultados, output_file=None):
        self.results = resultados
        self.output_file = output_file

    def _lineas_resumen(self):
        p_valor = AnalizadorChiCuadrado.formatear_p_valor(self.results["p_valor"])
        return [
            "Informe de analisis Chi-cuadrado LSB",
            f"Imagen analizada: {self.results.get('imagen', 'No especificada')}",
            f"Estadistico Chi-cuadrado: {self.results['chi_cuadrado']:.6f}",
            f"Grados de libertad: {self.results['grados_libertad']}",
            f"Bytes analizados: {self.results.get('bytes_analizados', 'N/D')} de {self.results.get('bytes_totales', 'N/D')}",
            f"p-valor: {p_valor}",
            f"Interpretacion: {self.results['interpretacion']}",
            "",
            "El resultado es un indicio estadistico y no confirma por si solo la existencia de un mensaje.",
        ]

    def export_summary(self, output_file=None):
        destino = Path(output_file or self.output_file)
        destino.write_text("\n".join(self._lineas_resumen()) + "\n", encoding="utf-8")
        return destino

    def generate_pdf(self, output_file=None):
        destino = Path(output_file or self.output_file)
        documento = canvas.Canvas(str(destino), pagesize=letter)
        ancho, alto = letter
        documento.setTitle("Informe Chi-cuadrado LSB")
        y = alto - 54

        for indice, linea in enumerate(self._lineas_resumen()):
            for fragmento in wrap(linea, width=86) or [""]:
                if y < 54:
                    documento.showPage()
                    y = alto - 54
                documento.setFont("Helvetica-Bold" if indice == 0 else "Helvetica", 11 if indice == 0 else 10)
                documento.drawString(48, y, fragmento)
                y -= 20 if indice == 0 else 16

        documento.save()
        return destino

    @staticmethod
    def _etiqueta_caracter(c):
        return "\\x00 (marca de fin)" if c == "\x00" else repr(c)

    @staticmethod
    def tabla_insercion(originales, modificados, texto_insertado, imagen="No especificada"):
        """Tabla original vs modificado. texto_insertado incluye el \\x00 final."""
        canales = "RGB"
        bits = "".join(f"{ord(c):08b}" for c in texto_insertado)
        n = min(len(bits), GeneradorInforme.MAX_BYTES_TABLA)
        cambiados, dif_max = 0, 0
        l = [
            "TABLA DE BYTES COMPARATIVOS - INSERCION LSB",
            f"Imagen: {imagen}",
            f"Mensaje: {texto_insertado.rstrip(chr(0))!r} ({len(texto_insertado)} caracteres con marca de fin)",
            f"Bytes modificados en la tabla: {n} ({n // 8} caracteres, 1 bit por byte)",
            "",
            "Byte | Pix/Canal | Original (dec / bin) | Bit | Modificado (dec / bin) | Resultado",
            "-" * 80,
        ]
        for i in range(n):
            if i % 8 == 0:
                k = i // 8
                c = texto_insertado[k]
                l.append(f">> Caracter {k + 1}: {GeneradorInforme._etiqueta_caracter(c)}"
                         f" | ASCII {ord(c)} | bits {ord(c):08b}")
            o, m = originales[i], modificados[i]
            cambiados += o != m
            dif_max = max(dif_max, abs(o - m))
            res = "Coincidia" if o == m else "Cambio"
            l.append(f"{i + 1:>4} | {i // 3 + 1:>6}/{canales[i % 3]}  | {o:>3} / {o:08b}"
                     f"      |  {bits[i]}  | {m:>3} / {m:08b}         | {res}")
            if i % 8 == 7:
                l.append("-" * 80)
        l += ["", f"Bytes que cambiaron: {cambiados} de {n}",
              f"Bytes que ya coincidian: {n - cambiados} de {n}",
              f"Diferencia maxima en un byte: {dif_max}"]
        if len(bits) > n:
            l.append(f"(Tabla truncada a {n} bytes de {len(bits)})")
        return "\n".join(l) + "\n"

    @staticmethod
    def tabla_extraccion(datos, mensaje, imagen="No especificada"):
        """Tabla con el LSB leido de cada byte. Cubre el mensaje y su marca de fin."""
        canales = "RGB"
        n = min(8 * (len(mensaje) + 1), len(datos), GeneradorInforme.MAX_BYTES_TABLA)
        l = [
            "TABLA DE BYTES - EXTRACCION LSB",
            f"Imagen: {imagen}",
            f"Mensaje recuperado: {mensaje!r} ({len(mensaje)} caracteres + marca de fin)",
            f"Bytes leidos en la tabla: {n}",
            "",
            "Byte | Pix/Canal | Valor (dec / bin) | LSB extraido",
            "-" * 60,
        ]
        acum = ""
        for i in range(n):
            b = datos[i]
            bit = b & 1
            acum += str(bit)
            l.append(f"{i + 1:>4} | {i // 3 + 1:>6}/{canales[i % 3]}  | {b:>3} / {b:08b}"
                     f"   |      {bit}")
            if len(acum) == 8:
                v = int(acum, 2)
                l.append(f">> {acum} = {v} = {GeneradorInforme._etiqueta_caracter(chr(v))}")
                l.append("-" * 60)
                acum = ""
        if 8 * (len(mensaje) + 1) > n:
            l.append(f"(Tabla truncada a {n} bytes)")
        return "\n".join(l) + "\n"