"""
experimentos.py

Genera los datos y las gráficas necesarias para las secciones de
Desarrollo y Cálculos (5) y Análisis de Resultados y Precisión (6)
del informe. Este script no es el software entregable (ese es
gui.py); su función es correr el experimento por lotes sobre varias
funciones de prueba y dejar los resultados (tablas en consola +
gráficas PNG) listos para pegar en el documento Word.

Genera dentro de la carpeta resultados/:
  - Una gráfica de convergencia del error (log-log) por cada función
    de prueba, comparando Trapecio, Simpson 1/3 y Simpson 3/8.
"""

import os

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy import integrate as sci_integrate

from metodos_numericos import trapecio, simpson13, simpson38, error_relativo

CARPETA_RESULTADOS = "resultados"
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

x = sp.symbols("x")

funciones_prueba = [
    {"nombre": "x^3 + 2x + 1", "archivo": "polinomial", "expr": x**3 + 2*x + 1,
     "f": lambda x: x**3 + 2*x + 1, "a": 0, "b": 5},
    {"nombre": "sin(x)", "archivo": "seno", "expr": sp.sin(x),
     "f": lambda x: np.sin(x), "a": 0, "b": np.pi},
    {"nombre": "e^(-x^2)", "archivo": "gaussiana", "expr": sp.exp(-x**2),
     "f": lambda x: np.exp(-x**2), "a": -2, "b": 2},
    {"nombre": "1 / (1 + 25x^2)  [Runge]", "archivo": "runge", "expr": 1 / (1 + 25*x**2),
     "f": lambda x: 1 / (1 + 25*x**2), "a": -1, "b": 1},
]

# n múltiplos de 6: a la vez par (Simpson 1/3) y múltiplo de 3 (Simpson 3/8)
VALORES_N = [6, 12, 24, 48, 96, 192]


def calcular_valor_exacto(caso):
    try:
        return float(sp.integrate(caso["expr"], (x, caso["a"], caso["b"])))
    except Exception:
        valor, _ = sci_integrate.quad(caso["f"], caso["a"], caso["b"])
        return valor


def generar_tabla(caso, valor_exacto):
    print(
        f"\nFunción: f(x) = {caso['nombre']}   |   Intervalo [{caso['a']}, {caso['b']}]")
    print(f"Valor de referencia: {valor_exacto:.8f}")
    print(f"{'n':>5} | {'Err. Trapecio (%)':>18} | {'Err. Simpson 1/3 (%)':>20} | {'Err. Simpson 3/8 (%)':>20}")

    errores = {"n": [], "trap": [], "s13": [], "s38": []}
    for n in VALORES_N:
        err_trap = error_relativo(
            trapecio(caso["f"], caso["a"], caso["b"], n), valor_exacto)
        err_s13 = error_relativo(
            simpson13(caso["f"], caso["a"], caso["b"], n), valor_exacto)
        err_s38 = error_relativo(
            simpson38(caso["f"], caso["a"], caso["b"], n), valor_exacto)

        print(f"{n:>5} | {err_trap:>18.8f} | {err_s13:>20.8f} | {err_s38:>20.8f}")

        errores["n"].append(n)
        # evita log(0) en la gráfica
        errores["trap"].append(max(err_trap, 1e-16))
        errores["s13"].append(max(err_s13, 1e-16))
        errores["s38"].append(max(err_s38, 1e-16))

    return errores


def graficar_convergencia(caso, errores):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.loglog(errores["n"], errores["trap"], "o-",
              label="Trapecio", color="#b5651d")
    ax.loglog(errores["n"], errores["s13"], "s-",
              label="Simpson 1/3", color="#2e6b2e")
    ax.loglog(errores["n"], errores["s38"], "^-",
              label="Simpson 3/8", color="#1f4e79")

    ax.set_title(f"Convergencia del error — f(x) = {caso['nombre']}")
    ax.set_xlabel("Número de subintervalos (n)")
    ax.set_ylabel("Error relativo (%) [escala log]")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)

    ruta = os.path.join(CARPETA_RESULTADOS,
                        f"convergencia_{caso['archivo']}.png")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfica guardada en: {ruta}")


def main():
    for caso in funciones_prueba:
        valor_exacto = calcular_valor_exacto(caso)
        errores = generar_tabla(caso, valor_exacto)
        graficar_convergencia(caso, errores)


if __name__ == "__main__":
    main()
