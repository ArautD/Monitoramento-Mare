from fastapi import FastAPI
from services.clima import obter_dados_climaticos
from rules.risco import calcular_risco

app = FastAPI()

@app.get("/")

def home():
    return {"message": "API de Monitoramento de Maré e Chuva"}

@app.get("/status")
def status(cidade: str):
    dados = obter_dados_clima(cidade)
    risco = calcular_risco(dados)
    return {
        "cidade": cidade,
        "dados_climaticos": dados,
        "risco": risco
    }

