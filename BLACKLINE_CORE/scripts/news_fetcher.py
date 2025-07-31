
import requests
import yaml

# 1. Cargar clave API desde config.yaml
with open('C:/Users/dondriano/Desktop/BLACKLINE_SYSTEM/BLACKLINE_CORE/configuracion/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
api_key = config['newsapi_key']

# 2. Lista de países a analizar
countries = {
    'Ucrania': 'Ukraine',
    'Irán': 'Iran',
    'China': 'China',
    'Argelia': 'Algeria',
    'Israel': 'Israel'
}

# 3. Palabras clave
keywords = ['attack', 'protest', 'military', 'bomb', 'war', 'strike']

# 4. Buscar titulares por país
for name, country in countries.items():
    print(f"\n🛰️ Noticias de {name.upper()}:")
    for keyword in keywords:
        url = f"https://newsapi.org/v2/everything?q={keyword}+{country}&sortBy=publishedAt&apiKey={api_key}&language=en&pageSize=1"
        response = requests.get(url)
        data = response.json()

        if data.get("articles"):
            article = data["articles"][0]
            print(f"- {article['title']}")
        break  # Solo muestra 1 keyword por país para no saturar
