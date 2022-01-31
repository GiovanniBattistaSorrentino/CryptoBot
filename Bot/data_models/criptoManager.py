from six.moves import urllib
import json
import codecs
import operator

class CriptoManager:

    #il metodo potrebbe restituire una lista con un numero minore di cripto di quelle richiste
    @staticmethod
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

    #il metodo potrebbe restituire una lista con un numero minore di cripto di quelle richiste
    @staticmethod
    def get_lista_cripto_in_un_range(min_range, max_range, numero_di_cripto_da_restituire):
        lista_delle_cripto = CriptoManager.get_lista_migliori_cripto(500)
        lista_da_restituire = []
        numero_cripto_trovate = 0
        for cripto in lista_delle_cripto:
            prezzo = cripto["prezzo"]
            if((prezzo >= min_range) and (prezzo <= max_range)):
                numero_cripto_trovate += 1
                lista_da_restituire.append(cripto)
                if(numero_cripto_trovate >= numero_di_cripto_da_restituire):
                    return lista_da_restituire
        return lista_da_restituire

    @staticmethod
    def get_lista_cripto_maggiore_incremento_24h(numero_di_cripto_da_restituire=5):
        lista_delle_cripto = CriptoManager.get_lista_migliori_cripto(500)
        lista_delle_cripto.sort(key=operator.itemgetter('variazione24h'), reverse=True)
        return lista_delle_cripto[0:numero_di_cripto_da_restituire]

    @staticmethod
    def get_cripto(symbol_cripto):
        lista_cripto = CriptoManager.get_lista_migliori_cripto(500)
        for cripto in lista_cripto:
            if (cripto["symbol_name"] == symbol_cripto):
                return cripto
        return None
