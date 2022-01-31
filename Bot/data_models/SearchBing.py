import requests

from config import DefaultConfig
from data_models.News import News

# Dati di configurazione per l'utilizzo di Search Bing
CONFIG = DefaultConfig()
subscription_key = CONFIG.BING_KEY
search_url = CONFIG.BING_SEARCH_URL

class SearchBing:
    @staticmethod
    def news_from_bing_as_object(news) -> News:
        news_as_object = News(news["name"], news["url"], news["description"], news["datePublished"])
        return news_as_object

    @staticmethod
    def get_news(search_term="cripto", numero_di_notizie=3, market='it-it'):
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {"q": search_term, "textDecorations": True, "textFormat": "HTML", "count": numero_di_notizie,
                  "mkt": market}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        a = response.json()
        lista_notizie = a["value"]
        return lista_notizie


# all_news = SearchBing.get_news(numero_di_notizie=3)
#
# for i in range(len(all_news)):
#     print(f"News number {i}")
#
#     news = SearchBing.news_from_bing_as_object(all_news[i])
#     print(f"Name: {news.getName()}")
#     print(f"Url: {news.getUrl()}")
#     print(f"Description: {news.getDescription()}")
#     print(f"Data pubblicazione: {news.getData_published()}")
#     print()
