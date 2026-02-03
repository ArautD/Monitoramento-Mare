from fastapi import FastAPI
from services.clima import obter_prev_chuva
from services.clima import obter_dados_clima
from rules.risco import calcular_risco

app = FastAPI()

"""Adicionar as variaveis em inglês tras maior profissionalismo"""
@app.get("/")

def home():
    return {"message": "API de Monitoramento de Maré e Chuva"}

@app.get("/status-atual")
def status_atual(cidade: str):
    dados = obter_dados_clima(cidade)
    risco = calcular_risco(dados)

    return {
        "cidade": cidade,
        "chuva_mm": dados["chuva"],
        "mare_m": dados["mare"],
        "risco": risco
    }

@app.get("/status-previsao")
def status_previsao(cidade: str):
    chuva_prevista = obter_prev_chuva(cidade)
    risco = calcular_risco(dados)

    dados = {
        "chuva": chuva_prevista,
        "mare": 2.5
    }


    return {
        "cidade": cidade,
        "chuva_prevista_24_mm": chuva_prevista,
        "mare_m": dados["mare"],
        "risco": risco
    }
