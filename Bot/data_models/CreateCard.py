from botbuilder.core import CardFactory, MessageFactory
from botbuilder.schema import HeroCard, CardAction, ActionTypes, CardImage, AttachmentLayoutTypes

from data_models.SearchBing import SearchBing
from data_models.Utils import Utils


class CreateCard:

    @staticmethod
    def createMenuCardWithCarousel():
        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel
        reply.attachments.append(CreateCard.create_user_profile_card(
            title="1.Traccia cryptovaluta",
            subtitle="",
            text="Rimani sempre aggiornato sulla tua criptovaluta preferita!\n\nTi proponiamo tutte le cryptovalute a nostra disposizione",
            url="https://image.cnbcfm.com/api/v1/image/106984655-1638720074358-gettyimages-1294303237-01_jan_01_005.jpeg?v=1640801347&w=929&h=523"))
        reply.attachments.append(CreateCard.create_user_profile_card(
            title="2.Ultime notizie sul mondo crypto",
            subtitle="",
            text="Scopri quali sono le ultime notizie riguardo il mondo cripto con un semplice click, non te ne pentirai",
            url="https://play-lh.googleusercontent.com/1F0mOUKA4iU5l6HZliXZnzfWGnxBqmMPs2L5Kiq1j9_IoFxZ198NulqckvyBhnYNGew"))
        reply.attachments.append(CreateCard.create_user_profile_card(
            title="3.Ultime crypto con maggior incremento",
            subtitle="",
            text="Vuoi conoscere le ultime 5 crypto che hanno avuto maggior incremento di valore nelle ultime 24 ore? Cosa aspetti a cliccare",
            url="https://d110erj175o600.cloudfront.net/wp-content/uploads/2018/02/bitcoin_740407774.jpg"))
        reply.attachments.append(CreateCard.create_user_profile_card(
            title="4.Servizio Question and Answer",
            subtitle="",
            text="Servizio Question and Answer per rispondere a tutte le tue domande sul mondo delle crypto!",
            url="https://www.gannett-cdn.com/presto/2021/04/19/USAT/cf9a04e6-b511-415f-b90a-1c438bd88bc8-Copy_of_crypto_qa.png?width=660&height=347&fit=crop&format=pjpg&auto=webp"))
        reply.attachments.append(CreateCard.create_user_profile_card(
            title="5.Restituire cryptovalute",
            subtitle="",
            text="Restituire cryptovalute che hanno un valore compreso in un range di valori",
            url="https://www.interactivebrokers.com/images/web/crypto-low-cost.jpg"))

        return reply

    @staticmethod
    def createCarouselWithNews(all_news):
        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel

        for i in range(len(all_news)):
            news = SearchBing.news_from_bing_as_object(all_news[i])
            #print(f"News n.{i}\nNews: {Utils.replace_escapes(Utils.cleanhtml(news.getDescription()))}\n")
            reply.attachments.append(
                CreateCard.create_news_card(
                    title=Utils.cleanhtml(news.getName()),
                    subtitle=f"Pubblicazione: {news.getData_published()[0:10]}",
                    text=Utils.cleanhtml(news.getDescription()),
                    url=news.getUrl()
                )
            )
        return reply

    @staticmethod
    def create_user_profile_card(title, subtitle, text, url: str=None):
        if (url is not None):
            image=CardImage(url= url)
            card = HeroCard(
                title=title,
                subtitle=subtitle,
                text=text,
                images=[image]
            )
        else:
            card = HeroCard(
                title=Utils.replace_escapes(title),
                subtitle=Utils.replace_escapes(subtitle),
                text=Utils.replace_escapes(text)
            )

        return CardFactory.hero_card(card)


    @staticmethod
    def create_news_card(title, subtitle, text, url: str=None):
        card = HeroCard(
            title=Utils.replace_escapes(title),
            subtitle=Utils.replace_escapes(subtitle),
            text=Utils.replace_escapes(text),
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title=Utils.replace_escapes("link"),
                    value=url
                )
            ]
        )

        return CardFactory.hero_card(card)
