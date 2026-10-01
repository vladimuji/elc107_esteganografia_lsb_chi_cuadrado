import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from claseEstego.AnalizadorChiCuadrado import AnalizadorChiCuadrado
from claseEstego.ClaseFoto import Foto
from claseEstego.GeneradorInforme import GeneradorInforme


class InterfazEstego:
    def __init__(self, root):
        self.root = root
        self.root.title("Esteganografía LSB")
        self.root.geometry("900x680")
        self.root.minsize(720, 580)

        self.codificador = None
        self.extractor = None
        self.imagen_analisis = None
        self.ruta_analisis = None
        self.resultados_analisis = None
        self.referencias_imagen = {}
        self.analizador = AnalizadorChiCuadrado()

        titulo = ttk.Label(root, text="Esteganografía LSB", font=("Segoe UI", 18, "bold"))
        titulo.pack(anchor="w", padx=20, pady=(16, 8))

        self.pestanas = ttk.Notebook(root)
        self.pestanas.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.pestana_ocultar = ttk.Frame(self.pestanas, padding=16)
        self.pestana_extraer = ttk.Frame(self.pestanas, padding=16)
        self.pestana_analizar = ttk.Frame(self.pestanas, padding=16)
        self.pestanas.add(self.pestana_ocultar, text="Ocultar mensaje")
        self.pestanas.add(self.pestana_extraer, text="Extraer mensaje")
        self.pestanas.add(self.pestana_analizar, text="Analizar imagen")

        self._crear_pestana_ocultar()
        self._crear_pestana_extraer()
        self._crear_pestana_analizar()

        self.tabla_insercion_txt = None
        self.tabla_extraccion_txt = None

    @staticmethod
    def _cargar_foto(ruta):
        imagen = Image.open(ruta).convert("RGB")
        foto = Foto()
        foto.img = imagen
        foto.img_original = imagen.copy()
        foto.lista_pixeles = list(imagen.tobytes())
        return foto

    def _mostrar_vista_previa(self, etiqueta, imagen):
        vista = imagen.copy()
        vista.thumbnail((420, 280))
        referencia = ImageTk.PhotoImage(vista)
        etiqueta.configure(image=referencia, text="")
        etiqueta.image = referencia
        self.referencias_imagen[etiqueta] = referencia

    def _crear_pestana_ocultar(self):
        panel = self.pestana_ocultar
        panel.columnconfigure(0, weight=1)

        ttk.Button(panel, text="Seleccionar imagen BMP o PNG", command=self._seleccionar_para_ocultar).grid(
            row=0, column=0, sticky="w"
        )
        self.ruta_ocultar = ttk.Label(panel, text="Ninguna imagen seleccionada")
        self.ruta_ocultar.grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.vista_ocultar = ttk.Label(panel, text="Vista previa", anchor="center")
        self.vista_ocultar.grid(row=2, column=0, sticky="nsew", pady=(0, 12))

        ttk.Label(panel, text="Mensaje").grid(row=3, column=0, sticky="w")
        self.entrada_mensaje = ttk.Entry(panel)
        self.entrada_mensaje.grid(row=4, column=0, sticky="ew", pady=(4, 12))

        acciones = ttk.Frame(panel)
        acciones.grid(row=5, column=0, sticky="w")
        self.boton_insertar = ttk.Button(
            acciones, text="Insertar mensaje", command=self._insertar_mensaje, state="disabled"
        )
        self.boton_insertar.pack(side="left", padx=(0, 8))
        self.boton_guardar = ttk.Button(
            acciones, text="Guardar imagen", command=self._guardar_imagen, state="disabled"
        )
        self.boton_guardar.pack(side="left", padx=(0, 8))
        self.boton_tabla_ocultar = ttk.Button(
            acciones, text="Descargar tabla de bytes comparativos",
            command=lambda: self._guardar_tabla(self.tabla_insercion_txt, "tabla_insercion.txt"),
            state="disabled",
        )
        self.boton_tabla_ocultar.pack(side="left")
        self.estado_ocultar = ttk.Label(panel, text="")
        self.estado_ocultar.grid(row=6, column=0, sticky="w", pady=(10, 0))

    def _crear_pestana_extraer(self):
        panel = self.pestana_extraer
        panel.columnconfigure(0, weight=1)

        ttk.Button(panel, text="Seleccionar imagen BMP o PNG", command=self._seleccionar_para_extraer).grid(
            row=0, column=0, sticky="w"
        )
        self.ruta_extraer = ttk.Label(panel, text="Ninguna imagen seleccionada")
        self.ruta_extraer.grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.vista_extraer = ttk.Label(panel, text="Vista previa", anchor="center")
        self.vista_extraer.grid(row=2, column=0, sticky="nsew", pady=(0, 12))

        ttk.Label(
            panel,
            text="La extracción reconoce mensajes creados por esta aplicación y terminados en un byte nulo.",
            wraplength=680,
        ).grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Button(panel, text="Extraer mensaje", command=self._extraer_mensaje).grid(
            row=4, column=0, sticky="w"
        )
        self.resultado_extraer = tk.Text(panel, height=5, wrap="word", state="disabled")
        self.resultado_extraer.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        panel.rowconfigure(5, weight=1)

    def _crear_pestana_analizar(self):
        panel = self.pestana_analizar
        panel.columnconfigure(0, weight=1)

        ttk.Button(panel, text="Seleccionar imagen BMP o PNG", command=self._seleccionar_para_analizar).grid(
            row=0, column=0, sticky="w"
        )
        self.ruta_analizar = ttk.Label(panel, text="Ninguna imagen seleccionada")
        self.ruta_analizar.grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.vista_analizar = ttk.Label(panel, text="Vista previa", anchor="center")
        self.vista_analizar.grid(row=2, column=0, sticky="nsew", pady=(0, 12))

        acciones = ttk.Frame(panel)
        acciones.grid(row=3, column=0, sticky="w")
        ttk.Button(acciones, text="Ejecutar análisis Chi-cuadrado", command=self._analizar_imagen).pack(
            side="left", padx=(0, 8)
        )
        self.boton_pdf = ttk.Button(
            acciones, text="Guardar informe PDF", command=self._guardar_pdf, state="disabled"
        )
        self.boton_pdf.pack(side="left", padx=(0, 8))
        self.boton_resumen = ttk.Button(
            acciones, text="Exportar resumen TXT", command=self._exportar_resumen, state="disabled"
        )
        self.boton_resumen.pack(side="left")
        self.resultado_analisis = ttk.Label(panel, text="", justify="left", wraplength=700)
        self.resultado_analisis.grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Label(
            panel,
            text="El resultado es un indicio estadístico; no confirma por sí solo la existencia de un mensaje.",
            wraplength=700,
        ).grid(row=5, column=0, sticky="w", pady=(12, 0))

    def _seleccionar_para_ocultar(self):
        ruta = self._pedir_ruta_imagen()
        if not ruta:
            return
        try:
            self.codificador = self._cargar_foto(ruta)
            self.ruta_ocultar.configure(text=ruta)
            self._mostrar_vista_previa(self.vista_ocultar, self.codificador.img)
            self.estado_ocultar.configure(
                text=f"{self.codificador.img.width} x {self.codificador.img.height} píxeles"
            )
            self.boton_insertar.configure(state="normal")
            self.boton_guardar.configure(state="disabled")
            self.boton_tabla_ocultar.configure(state="disabled")
        except Exception as error:
            messagebox.showerror("No se pudo abrir la imagen", str(error), parent=self.root)

    def _seleccionar_para_extraer(self):
        ruta = self._pedir_ruta_imagen()
        if not ruta:
            return
        try:
            self.extractor = self._cargar_foto(ruta)
            self.ruta_extraer.configure(text=ruta)
            self._mostrar_vista_previa(self.vista_extraer, self.extractor.img)
            self.boton_tabla_extraer.configure(state="disabled")
        except Exception as error:
            messagebox.showerror("No se pudo abrir la imagen", str(error), parent=self.root)

    def _seleccionar_para_analizar(self):
        ruta = self._pedir_ruta_imagen()
        if not ruta:
            return
        try:
            self.imagen_analisis = Image.open(ruta).convert("RGB")
            self.ruta_analisis = ruta
            self.resultados_analisis = None
            self.ruta_analizar.configure(text=ruta)
            self._mostrar_vista_previa(self.vista_analizar, self.imagen_analisis)
            self.resultado_analisis.configure(text="")
            self.boton_pdf.configure(state="disabled")
            self.boton_resumen.configure(state="disabled")
        except Exception as error:
            messagebox.showerror("No se pudo abrir la imagen", str(error), parent=self.root)

    def _pedir_ruta_imagen(self):
        return filedialog.askopenfilename(
            parent=self.root,
            title="Seleccionar imagen",
            filetypes=[("Imágenes PNG", "*.png"), ("Imágenes BMP", "*.bmp"), ("Todos los archivos", "*.*")],
        )

    def _insertar_mensaje(self):
        if self.codificador is None:
            return
        mensaje = self.entrada_mensaje.get()
        if not mensaje:
            messagebox.showwarning("Mensaje vacío", "Escribe el mensaje que quieres ocultar.", parent=self.root)
            return
        if any(ord(caracter) > 255 for caracter in mensaje):
            messagebox.showerror(
                "Caracter no compatible",
                "Por ahora solo se admiten caracteres de un byte, incluidos los caracteres latinos.",
                parent=self.root,
            )
            return

        # bits = self.codificador.texto_a_bits(mensaje + "\x00")
        # if len(bits) > len(self.codificador.lista_pixeles):
        #     messagebox.showerror("Mensaje demasiado largo", "El mensaje no cabe en esta imagen.", parent=self.root)
        #     return

        # originales = self.codificador.lista_pixeles[:8] 
        # self.codificador.encriptar(bits)
        # modificados = self.codificador.lista_pixeles[:8]
        # print("Byte | Original (dec / bin) | Bit | Modificado (dec / bin)")
        # for i in range(8):
        #     o, m = originales[i], modificados[i]
        #     print(f"{i+1:>4} | {o:>3} / {o:08b}      |  {bits[i]}  | {m:>3} / {m:08b}")

        # self._mostrar_vista_previa(self.vista_ocultar, self.codificador.img)
        # self.estado_ocultar.configure(text="Mensaje insertado. Guarda la imagen para conservar el resultado.")
        # self.boton_guardar.configure(state="normal")

        texto = mensaje + "\x00"
        bits = self.codificador.texto_a_bits(texto)
        if len(bits) > len(self.codificador.lista_pixeles):
            messagebox.showerror("Mensaje demasiado largo", "El mensaje no cabe en esta imagen.", parent=self.root)
            return

        self.codificador.encriptar(bits)
        n = len(bits)
        originales = list(self.codificador.img_original.tobytes()[:n])
        modificados = self.codificador.lista_pixeles[:n]
        self.tabla_insercion_txt = GeneradorInforme.tabla_insercion(
            originales, modificados, texto, self.ruta_ocultar.cget("text")
        )
        self.boton_tabla_ocultar.configure(state="normal")

        self._mostrar_vista_previa(self.vista_ocultar, self.codificador.img)
        self.estado_ocultar.configure(text="Mensaje insertado. Guarda la imagen para conservar el resultado.")
        self.boton_guardar.configure(state="normal")


    def _guardar_imagen(self):
        if self.codificador is None:
            return
        ruta = filedialog.asksaveasfilename(
            parent=self.root,
            title="Guardar imagen con mensaje",
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png"), ("Imagen BMP", "*.bmp")],
        )
        if not ruta:
            return
        try:
            self.codificador.img.save(ruta)
            self.estado_ocultar.configure(text=f"Imagen guardada: {ruta}")
        except Exception as error:
            messagebox.showerror("No se pudo guardar la imagen", str(error), parent=self.root)

    def _extraer_mensaje(self):
        if self.extractor is None:
            messagebox.showwarning("Falta una imagen", "Selecciona una imagen primero.", parent=self.root)
            return
        mensaje = self.extractor.desencriptar()
        self.resultado_extraer.configure(state="normal")
        self.resultado_extraer.delete("1.0", "end")
        self.resultado_extraer.insert("1.0", mensaje)
        self.resultado_extraer.configure(state="disabled")
        self.tabla_extraccion_txt = GeneradorInforme.tabla_extraccion(
            self.extractor.lista_pixeles, mensaje, self.ruta_extraer.cget("text")
        )
        self.boton_tabla_extraer.configure(state="normal")

    def _analizar_imagen(self):
        if self.imagen_analisis is None:
            messagebox.showwarning("Falta una imagen", "Selecciona una imagen primero.", parent=self.root)
            return
        self.resultados_analisis, _ = self.analizador.analizar_progresivo(self.imagen_analisis)
        self.resultados_analisis["imagen"] = self.ruta_analisis
        self.resultado_analisis.configure(
            text=(
                f"Chi-cuadrado: {self.resultados_analisis['chi_cuadrado']:.4f}\n"
                f"Grados de libertad: {self.resultados_analisis['grados_libertad']}\n"
                f"Bytes analizados: {self.resultados_analisis['bytes_analizados']} "
                f"de {self.resultados_analisis['bytes_totales']} (ventana con mayor p-valor)\n"
                f"p-valor: {self.analizador.formatear_p_valor(self.resultados_analisis['p_valor'])}\n\n"
                f"{self.resultados_analisis['interpretacion']}"
            )
        )
        self.boton_pdf.configure(state="normal")
        self.boton_resumen.configure(state="normal")

    def _generar_informe(self, formato):
        if self.resultados_analisis is None:
            return
        extension = ".pdf" if formato == "pdf" else ".txt"
        ruta = filedialog.asksaveasfilename(
            parent=self.root,
            title="Guardar informe" if formato == "pdf" else "Exportar resumen",
            defaultextension=extension,
            filetypes=[("Documento PDF", "*.pdf")] if formato == "pdf" else [("Texto", "*.txt")],
        )
        if not ruta:
            return
        try:
            generador = GeneradorInforme(self.resultados_analisis, ruta)
            if formato == "pdf":
                generador.generate_pdf()
            else:
                generador.export_summary()
            messagebox.showinfo("Informe generado", f"Archivo guardado en:\n{ruta}", parent=self.root)
        except Exception as error:
            messagebox.showerror("No se pudo generar el informe", str(error), parent=self.root)

    def _guardar_pdf(self):
        self._generar_informe("pdf")

    def _guardar_tabla(self, texto, nombre_sugerido):
        if not texto:
            return
        ruta = filedialog.asksaveasfilename(
            parent=self.root, title="Guardar tabla de bytes",
            defaultextension=".txt", initialfile=nombre_sugerido,
            filetypes=[("Texto", "*.txt")],
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
            messagebox.showinfo("Tabla guardada", f"Archivo guardado en:\n{ruta}", parent=self.root)
        except Exception as error:
            messagebox.showerror("No se pudo guardar la tabla", str(error), parent=self.root)

    def _exportar_resumen(self):
        self._generar_informe("txt")


def iniciar_aplicacion():
    root = tk.Tk()
    InterfazEstego(root)
    root.mainloop()