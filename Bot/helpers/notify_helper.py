from botbuilder.core import TurnContext, MessageFactory

from typing import Any, Callable

from data_models.databaseManager import DatabaseManager


class NotifyObject:
    def __init__(self, body: dict) -> None:
        if 'id' not in body:
            raise Exception('Bad Format Data')

        self.id = body['id']
        self.dizionario_cripto = body['dizionario_cripto']
        self.valore_tracciato = body['valore_tracciato']
        self.maggiore_minore = body['maggiore_minore']


def invia_messaggio(id: str, body: Any) -> Callable:
    oggetto = NotifyObject(body)
    user = DatabaseManager.getUser(oggetto.id)
    if (oggetto.maggiore_minore==">"):
        text = f"Salve {user.getNome_utente()},\n\n"\
               f"ti volevamo informare che la cripto '{oggetto.dizionario_cripto['nome_cripto']}' ({oggetto.dizionario_cripto['symbol_name']}) ha superato il valore da te deciso: \n\n"\
               f"Valore tracciato: {oggetto.valore_tracciato},\n\n" \
               f"Valore attuale: {'{:.2f}'.format(oggetto.dizionario_cripto['prezzo'])}."
    else:
        text = f"Salve {user.getNome_utente()},\n\n" \
               f"ti volevamo informare che la cripto '{oggetto.dizionario_cripto['nome_cripto']}' ({oggetto.dizionario_cripto['symbol_name']}) è inferiore rispetto al valore da te deciso: \n\n" \
               f"Valore tracciato: {oggetto.valore_tracciato},\n\n" \
               f"Valore attuale: {'{:.2f}'.format(oggetto.dizionario_cripto['prezzo'])}."

    reply = MessageFactory.text(text)

    async def func(turn_context: TurnContext):
        await turn_context.send_activity(reply)

    return func