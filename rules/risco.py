def calcular_risco(dados):
    chuva = dados["chuva"]
    mare = dados["mare"]

    if chuva > 50 and mare > 2.5:
        return "Alto"
    elif chuva > 30:
        return "Médio"
    else:
        return "Baixo"