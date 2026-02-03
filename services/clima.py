import requests

def obter_dados_clima(cidade): 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KOPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    chuva = 0
    if "rain" in data:
        chuva = data["rain"].get("1h", 0)
    mare = 2.5  # valor fixo para simulação
    return {
        "chuva": chuva,
        "mare": mare
    }

def obter_prev_chuva(cidade):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        print("Erro de API: ", response.text)
        return 0
    
    data = response.json()

    total_chuva = 0

    for item in data["list"]:
        chuva = item.get("rain", {}).get("3h", 0)
        total_chuva += chuva

    return round(total_chuva,2)
