from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from claseEstego.AnalizadorChiCuadrado import AnalizadorChiCuadrado


class GeneradorInforme:
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