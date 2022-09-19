import datetime
import logging
from azure.cosmos import CosmosClient
from six.moves import urllib
import json
import codecs
import requests
from config import DefaultConfig

import azure.functions as func

CONFIG = DefaultConfig()
uri = CONFIG.SERVERLESS_FUNCTION_URI
key = CONFIG.SERVERLESS_FUNCTION_KEY
database_name = CONFIG.COSMOSDB_DATABASE_NAME
container_name = CONFIG.COSMOSDB_CONTAINER_NAME

def get_lista_migliori_cripto(numero_di_cripto_da_restituire, numero_di_cripto_nella_ricerca = 500):
    url = "https://data.messari.io/api/v2/assets?limit=" + str(numero_di_cripto_nella_ricerca)
    web_json = urllib.request.urlopen(url).read()
    data_in_tipo_str: str = codecs.decode(web_json, 'UTF-8')
    dati_in_json = json.loads(data_in_tipo_str)
    lista_da_restituire=[]
    numero_cripto_trovate=0
    for i in range(numero_di_cripto_nella_ricerca):
        variazione = dati_in_json["data"][i]["metrics"]["market_data"]["percent_change_usd_last_24_hours"]
        if(variazione is not None):
            numero_cripto_trovate += 1
            dizionario = {}
            dizionario["nome_cripto"] = dati_in_json["data"][i]["name"]
            dizionario["symbol_name"] = dati_in_json["data"][i]["symbol"]
            dizionario["prezzo"] = dati_in_json["data"][i]["metrics"]["market_data"]["price_usd"]
            dizionario["variazione24h"] = dati_in_json["data"][i]["metrics"]["market_data"]["percent_change_usd_last_24_hours"]
            lista_da_restituire.append(dizionario)
            if(numero_cripto_trovate >= numero_di_cripto_da_restituire):
                return lista_da_restituire
    return lista_da_restituire


def get_lista_utenti():
    client = CosmosClient(uri, credential=key, consistency_level='Session')
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query1 = 'SELECT * FROM ContainerProva'
    lista_utenti = container.query_items(query = query1, enable_cross_partition_query=True)
    lista_da_ristornare = []
    for item in lista_utenti:
        lista_da_ristornare.append(item)
    return lista_da_ristornare

def get_cripto_dalla_lista(lista_cripto, symbol_cripto):
    for cripto in lista_cripto:
        if(cripto["symbol_name"] == symbol_cripto):
            return cripto
    return None

def invia_messaggio(id, dizionario_cripto, valore_tracciato, maggiore_minore):
    json_obj = {
        "id" : id,
        "dizionario_cripto" : dizionario_cripto,
        "valore_tracciato" : valore_tracciato,
        "maggiore_minore" : maggiore_minore
    }

    url = 'https://CryBotWebApp.azurewebsites.net/api/notify'
    headers = {'Content-Type': 'application/json'}

    requests.post(url, headers=headers, json=json_obj)


def controlla_cripto_tracciate():
    lista_utenti = get_lista_utenti()
    lista_cripto = get_lista_migliori_cripto(500)
    for utente in lista_utenti:
        lista_cripto_tracciate = utente["cripto_tracciate"].split(', ')
        for cripto_tracciata in lista_cripto_tracciate:
            if(cripto_tracciata != ''):
                symbol_cripto = cripto_tracciata.split(':')[0]
                valore_tracciato = float(cripto_tracciata.split(':')[1])
                maggiore_minore = cripto_tracciata.split(':')[2]
                dizionario_cripto = get_cripto_dalla_lista(lista_cripto, symbol_cripto)
                if(dizionario_cripto is not None):
                    valore_attuale_cripto = dizionario_cripto["prezzo"]
                    if (maggiore_minore == ">"):
                        if(valore_attuale_cripto >= valore_tracciato):
                            invia_messaggio(utente["id"], dizionario_cripto, valore_tracciato, maggiore_minore)
                    else:
                        if(valore_attuale_cripto <= valore_tracciato):
                            invia_messaggio(utente["id"], dizionario_cripto, valore_tracciato, maggiore_minore)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    controlla_cripto_tracciate()


