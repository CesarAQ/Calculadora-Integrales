"""
gui.py

Interfaz gráfica de la Calculadora de Integrales.

El usuario ingresa:
  - La función f(x) (por ejemplo: x**3 + 2*x + 1, sin(x), exp(-x**2))
  - El límite inferior y superior de integración
  - El número de subintervalos (n)
  - El método a utilizar: Trapecio, Simpson 1/3 o Simpson 3/8

El programa muestra:
  - El resultado numérico de la integral
  - El error relativo frente al valor "exacto" (calculado con sympy)
  - Una gráfica de la función junto con la representación geométrica
    del método aplicado (trapecios o segmentos de parábola)

Los cálculos de la integral usan las implementaciones PROPIAS del
archivo metodos_numericos.py (no funciones de librerías que resuelvan
la integral directamente). numpy/sympy/matplotlib se usan solo como
apoyo (evaluación, interpretación simbólica y graficación).
"""

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sympy as sp
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from metodos_numericos import trapecio, simpson13, simpson38, error_relativo


class CalculadoraIntegrales(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Integrales - Métodos Numéricos")
        self.geometry("1040x680")
        self.resizable(False, False)

        self._construir_panel_entrada()
        self._construir_panel_resultado()
        self._construir_panel_grafica()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir_panel_entrada(self):
        panel = ttk.LabelFrame(self, text="Datos de entrada")
        panel.place(x=15, y=15, width=320, height=380)

        ttk.Label(panel, text="Función f(x):").place(x=10, y=15)
        self.entry_funcion = ttk.Entry(panel, width=28)
        self.entry_funcion.insert(0, "x**3 + 2*x + 1")
        self.entry_funcion.place(x=10, y=40)

        ttk.Label(panel, text="Límite inferior (a):").place(x=10, y=75)
        self.entry_a = ttk.Entry(panel, width=28)
        self.entry_a.insert(0, "0")
        self.entry_a.place(x=10, y=100)

        ttk.Label(panel, text="Límite superior (b):").place(x=10, y=135)
        self.entry_b = ttk.Entry(panel, width=28)
        self.entry_b.insert(0, "5")
        self.entry_b.place(x=10, y=160)

        ttk.Label(panel, text="Número de subintervalos (n):").place(x=10, y=195)
        self.entry_n = ttk.Entry(panel, width=28)
        self.entry_n.insert(0, "12")
        self.entry_n.place(x=10, y=220)

        ttk.Label(panel, text="Método:").place(x=10, y=255)
        self.metodo_var = tk.StringVar(value="trapecio")
        ttk.Radiobutton(panel, text="Trapecio", variable=self.metodo_var,
                        value="trapecio").place(x=10, y=280)
        ttk.Radiobutton(panel, text="Simpson 1/3", variable=self.metodo_var,
                        value="simpson13").place(x=10, y=305)
        ttk.Radiobutton(panel, text="Simpson 3/8", variable=self.metodo_var,
                        value="simpson38").place(x=10, y=330)

        ttk.Button(panel, text="Calcular", command=self._calcular).place(
            x=180, y=280, width=110, height=55)

    def _construir_panel_resultado(self):
        panel = ttk.LabelFrame(self, text="Resultado")
        panel.place(x=15, y=405, width=320, height=260)

        self.lbl_resultado = ttk.Label(panel, text="Integral ≈ —",
                                       font=("Segoe UI", 13, "bold"))
        self.lbl_resultado.place(x=10, y=12)

        self.lbl_exacto = ttk.Label(panel, text="Valor de referencia: —",
                                    wraplength=295)
        self.lbl_exacto.place(x=10, y=48)

        self.lbl_error = ttk.Label(panel, text="Error relativo: —")
        self.lbl_error.place(x=10, y=80)

        self.lbl_validacion = ttk.Label(panel, text="Validación scipy: —",
                                        foreground="#555555", wraplength=295,
                                        justify="left")
        self.lbl_validacion.place(x=10, y=108)

        ttk.Button(panel, text="Ver tabla de convergencia (n = 2,4,8,16,32)",
                   command=self._abrir_tabla_convergencia).place(
            x=10, y=175, width=295, height=32)

    def _construir_panel_grafica(self):
        panel = ttk.LabelFrame(self, text="Gráfica")
        panel.place(x=350, y=15, width=585, height=620)

        self.figura = Figure(figsize=(5.6, 5.8), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=panel)
        self.canvas.get_tk_widget().place(x=5, y=5, width=570, height=605)
        self._dibujar_vacio()

    def _dibujar_vacio(self):
        self.ax.clear()
        self.ax.set_title("Ingresa una función y presiona Calcular")
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Lógica de cálculo
    # ------------------------------------------------------------------
    def _calcular(self):
        try:
            x_sym = sp.symbols("x")
            expr_texto = self.entry_funcion.get()
            expr = sp.sympify(expr_texto)
            f_lambda = sp.lambdify(x_sym, expr, modules=["numpy"])

            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            n = int(self.entry_n.get())
            metodo = self.metodo_var.get()

            if metodo == "trapecio":
                resultado = trapecio(f_lambda, a, b, n)
            elif metodo == "simpson13":
                if n % 2 != 0:
                    raise ValueError("Simpson 1/3 requiere que n sea PAR")
                resultado = simpson13(f_lambda, a, b, n)
            else:
                if n % 3 != 0:
                    raise ValueError(
                        "Simpson 3/8 requiere que n sea MÚLTIPLO DE 3")
                resultado = simpson38(f_lambda, a, b, n)

            # Valor de referencia (analítico si sympy puede resolverlo)
            try:
                valor_exacto = float(sp.integrate(expr, (x_sym, a, b)))
                texto_exacto = f"Valor de referencia (analítico): {valor_exacto:.6f}"
            except Exception:
                from scipy import integrate as sci_integrate
                valor_exacto, _ = sci_integrate.quad(f_lambda, a, b)
                texto_exacto = f"Valor de referencia (numérico, scipy.quad): {valor_exacto:.6f}"

            err = error_relativo(resultado, valor_exacto)

            self.lbl_resultado.config(text=f"Integral ≈ {resultado:.6f}")
            self.lbl_exacto.config(text=texto_exacto)
            self.lbl_error.config(text=f"Error relativo: {err:.6f} %")

            self._validar_con_scipy(f_lambda, a, b, n, metodo, resultado)
            self._graficar(f_lambda, a, b, n, metodo, expr_texto)

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo calcular la integral.\n\nDetalle: {e}")

    def _validar_con_scipy(self, f, a, b, n, metodo, resultado_propio):
        from scipy import integrate as sci_integrate
        xs = np.linspace(a, b, n + 1)
        ys = f(xs)
        if metodo == "trapecio":
            ref_scipy = sci_integrate.trapezoid(ys, xs)
        else:
            ref_scipy = sci_integrate.simpson(ys, x=xs)
        self.lbl_validacion.config(
            text=f"Validación scipy: propio = {resultado_propio:.6f}  |  "
            f"scipy = {ref_scipy:.6f}"
        )

    # ------------------------------------------------------------------
    # Graficación
    # ------------------------------------------------------------------
    def _graficar(self, f, a, b, n, metodo, expr_texto):
        self.ax.clear()

        xs_finos = np.linspace(a, b, 400)
        ys_finos = f(xs_finos)
        self.ax.plot(xs_finos, ys_finos, color="#1f4e79",
                     linewidth=2, label=f"f(x) = {expr_texto}")

        xs = np.linspace(a, b, n + 1)
        ys = f(xs)

        if metodo == "trapecio":
            self._sombrear_trapecios(xs, ys)
        elif metodo == "simpson13":
            self._sombrear_parabolas(xs, ys, paso=2)
        else:
            self._sombrear_parabolas(xs, ys, paso=3)

        self.ax.set_title("Función y representación geométrica del método")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.legend(loc="best", fontsize=8)
        self.ax.grid(alpha=0.3)
        self.canvas.draw()

    def _sombrear_trapecios(self, xs, ys):
        for i in range(len(xs) - 1):
            self.ax.fill(
                [xs[i], xs[i], xs[i + 1], xs[i + 1]],
                [0, ys[i], ys[i + 1], 0],
                color="#f4a742", alpha=0.35, edgecolor="#b5651d", linewidth=0.8,
            )

    def _sombrear_parabolas(self, xs, ys, paso):
        """Ajusta un polinomio (grado 2 para Simpson 1/3, grado 3 para
        Simpson 3/8) a cada grupo de puntos, únicamente con fines de
        visualización, y sombrea el área bajo esa curva aproximada."""
        i = 0
        while i + paso < len(xs):
            grupo_x = xs[i:i + paso + 1]
            grupo_y = ys[i:i + paso + 1]

            coeficientes = np.polyfit(grupo_x, grupo_y, paso)
            x_suave = np.linspace(grupo_x[0], grupo_x[-1], 60)
            y_suave = np.polyval(coeficientes, x_suave)

            self.ax.fill_between(x_suave, 0, y_suave,
                                 color="#7fb37f", alpha=0.35)
            self.ax.plot(x_suave, y_suave, color="#2e6b2e", linewidth=1.2)

            i += paso

    def _abrir_tabla_convergencia(self):
        try:
            x_sym = sp.symbols("x")
            expr_texto = self.entry_funcion.get()
            expr = sp.sympify(expr_texto)
            f_lambda = sp.lambdify(x_sym, expr, modules=["numpy"])

            a = float(self.entry_a.get())
            b = float(self.entry_b.get())

            try:
                valor_exacto = float(sp.integrate(expr, (x_sym, a, b)))
            except Exception:
                from scipy import integrate as sci_integrate
                valor_exacto, _ = sci_integrate.quad(f_lambda, a, b)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Revisa la función y los límites.\n\nDetalle: {e}")
            return

        ventana = tk.Toplevel(self)
        ventana.title(f"Tabla de convergencia — f(x) = {expr_texto}")
        ventana.geometry("760x320")
        ventana.resizable(False, False)

        ttk.Label(ventana, text=f"Valor de referencia: {valor_exacto:.6f}",
                  font=("Segoe UI", 10, "bold")).pack(pady=8)

        columnas = ("n", "trapecio", "simpson13", "simpson38",
                    "err_trap", "err_s13", "err_s38")
        tabla = ttk.Treeview(ventana, columns=columnas,
                             show="headings", height=8)

        encabezados = {
            "n": "n", "trapecio": "Trapecio", "simpson13": "Simpson 1/3",
            "simpson38": "Simpson 3/8", "err_trap": "Err. Trap (%)",
            "err_s13": "Err. Simp13 (%)", "err_s38": "Err. Simp38 (%)",
        }
        for col in columnas:
            tabla.heading(col, text=encabezados[col])
            tabla.column(col, width=100, anchor="center")

        # n = 6, 12, 24, 48: a la vez par (Simpson 1/3) y múltiplo de 3 (Simpson 3/8)
        for n in [6, 12, 24, 48]:
            r_trap = trapecio(f_lambda, a, b, n)
            r_s13 = simpson13(f_lambda, a, b, n)
            r_s38 = simpson38(f_lambda, a, b, n)

            err_trap = error_relativo(r_trap, valor_exacto)
            err_s13 = error_relativo(r_s13, valor_exacto)
            err_s38 = error_relativo(r_s38, valor_exacto)

            tabla.insert("", "end", values=(
                n, f"{r_trap:.6f}", f"{r_s13:.6f}", f"{r_s38:.6f}",
                f"{err_trap:.6f}", f"{err_s13:.6f}", f"{err_s38:.6f}",
            ))

        tabla.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Label(ventana, text="Nota: se usan valores de n múltiplos de 6 para poder "
                  "comparar los tres métodos con el mismo n en la misma tabla.",
                  foreground="#555555", wraplength=720).pack(pady=(0, 8))


if __name__ == "__main__":
    app = CalculadoraIntegrales()
    app.mainloop()
