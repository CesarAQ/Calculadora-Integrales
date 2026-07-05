"""
metodos_numericos.py

Implementaciones PROPIAS (desde cero, sin usar funciones de librerías
que ya resuelvan la integral) de los métodos de integración numérica:
- Regla del trapecio (compuesta)
- Regla de Simpson 1/3 (compuesta)
- Regla de Simpson 3/8 (compuesta)

Basado en el enfoque de Chapra, S. C., & Canale, R. P. (2015).
Métodos numéricos para ingenieros (7.a ed.). McGraw-Hill Education.
"""


def trapecio(f, a, b, n):
    """
    Aproxima la integral definida de f entre a y b usando la regla
    del trapecio compuesta con n subintervalos.

    Parámetros:
        f: función a integrar (callable, recibe un float y devuelve un float)
        a: límite inferior
        b: límite superior
        n: número de subintervalos (n >= 1)

    Retorna:
        Aproximación numérica de la integral (float)
    """
    if n < 1:
        raise ValueError("n debe ser mayor o igual a 1")

    h = (b - a) / n
    suma = f(a) + f(b)

    for i in range(1, n):
        xi = a + i * h
        suma += 2 * f(xi)

    return (h / 2) * suma


def simpson13(f, a, b, n):
    """
    Aproxima la integral definida de f entre a y b usando la regla
    de Simpson 1/3 compuesta con n subintervalos.

    Parámetros:
        f: función a integrar
        a: límite inferior
        b: límite superior
        n: número de subintervalos (debe ser PAR)

    Retorna:
        Aproximación numérica de la integral (float)
    """
    if n < 2:
        raise ValueError("n debe ser mayor o igual a 2")
    if n % 2 != 0:
        raise ValueError("Simpson 1/3 requiere que n sea un número par")

    h = (b - a) / n
    suma = f(a) + f(b)

    for i in range(1, n):
        xi = a + i * h
        if i % 2 == 0:
            suma += 2 * f(xi)   # puntos con índice par (interiores)
        else:
            suma += 4 * f(xi)   # puntos con índice impar

    return (h / 3) * suma


def simpson38(f, a, b, n):
    """
    Aproxima la integral definida de f entre a y b usando la regla
    de Simpson 3/8 compuesta con n subintervalos.

    Parámetros:
        f: función a integrar
        a: límite inferior
        b: límite superior
        n: número de subintervalos (debe ser MÚLTIPLO DE 3)

    Retorna:
        Aproximación numérica de la integral (float)
    """
    if n < 3:
        raise ValueError("n debe ser mayor o igual a 3")
    if n % 3 != 0:
        raise ValueError("Simpson 3/8 requiere que n sea múltiplo de 3")

    h = (b - a) / n
    suma = f(a) + f(b)

    for i in range(1, n):
        xi = a + i * h
        if i % 3 == 0:
            suma += 2 * f(xi)   # puntos múltiplos de 3 (interiores)
        else:
            suma += 3 * f(xi)   # los demás puntos

    return (3 * h / 8) * suma


def error_relativo(valor_aproximado, valor_exacto):
    """
    Calcula el error relativo porcentual entre un valor aproximado
    y el valor exacto (o de referencia).
    """
    if valor_exacto == 0:
        return abs(valor_aproximado - valor_exacto)
    return abs((valor_exacto - valor_aproximado) / valor_exacto) * 100
