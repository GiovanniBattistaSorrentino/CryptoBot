from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, TextPrompt, ConfirmPrompt, WaterfallDialog, WaterfallStepContext, \
    DialogTurnResult, PromptOptions, PromptValidatorContext, Choice, ChoicePrompt

from data_models.criptoManager import CriptoManager
from data_models.databaseManager import DatabaseManager


class TracciaCriptoDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(TracciaCriptoDialog, self).__init__(dialog_id or TracciaCriptoDialog.__name__)

        #menu WaterfallDialog
        self.add_dialog(ChoicePrompt("menu"))
        #primo WaterfallDialog: 'WFDialogMenuTracciaCripto'
        self.add_dialog(TextPrompt("insert_symbol_cripto_to_follow", TracciaCriptoDialog.validate_symbol_cripto))
        self.add_dialog(TextPrompt("insert_valore_da_tracciare", TracciaCriptoDialog.validate_valore_da_tracciare))
        self.add_dialog(ChoicePrompt("insert_maggiore_minore"))
        self.add_dialog(ConfirmPrompt("confirm_tracciamento_cripto"))
        #secondo WaterfallDialog: 'WFDialogTracciaCripto'
        self.add_dialog(TextPrompt("insert_symbol_cripto_to_remove", TracciaCriptoDialog.validate_symbol_cripto_to_remove))
        #terzo WaterfallDialog
        self.add_dialog(TextPrompt("number_cripto_to_show", TracciaCriptoDialog.validate_num_cripto_to_show))

        #Menu: 'traccia cripto', 'elimina cripto', 'esci'
        self.add_dialog(
            WaterfallDialog(
                "WFDialogMenuTracciaCripto",
                [
                    self.choose_path_step,
                    self.check_and_deliver_path_step
                ]
            )
        )

        #WaterfallDialog che traccia cripto
        self.add_dialog(
            WaterfallDialog(
                "WFDialogTracciaCripto",
                [
                    self.insert_symbol_cripto_to_follow_step,
                    self.insert_valore_da_tracciare_step,
                    self.insert_maggiore_minore_step,
                    self.confirm_cripto_to_follow_step,
                    self.loop_step
                ]
            )
        )

        #WaterfallDialog che elimina le cripto che segue l'utente
        self.add_dialog(
            WaterfallDialog(
                "WFDialogEliminaCripto",
                [
                    self.insert_symbol_cripto_to_remove_step,
                    self.remove_cripto_step
                ]
            )
        )

        #WaterfallDialog che stampa le migliori cripto. Servirà all'utente per capire quali cripto tracciare.
        self.add_dialog(
            WaterfallDialog(
                "WFDialogStampaMigliriCripto",
                [
                    self.insert_number_of_cripto_to_show_step,
                    self.show_migliori_cripto_step,
                ]
            )
        )

        self.initial_dialog_id = "WFDialogMenuTracciaCripto"

    #Metodi per il WaterfallDialog: 'WFDialogMenuTracciaCripto'
    async def choose_path_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "menu",
            PromptOptions(
                prompt=MessageFactory.text("Cosa vuoi fare"),
                choices=[Choice("Traccia cripto"), Choice("Elimina cripto"), Choice("Migliori cripto"), Choice("Esci")]
            )
        )

    async def check_and_deliver_path_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        path=step_context.result.value

        if path=="1" or path.lower()=="traccia cripto":
            return await step_context.begin_dialog("WFDialogTracciaCripto")
        if (path=="2" or path.lower()=="elimina cripto"):
            return await step_context.begin_dialog("WFDialogEliminaCripto")
        if (path=="3" or path.lower()=="migliori cripto"):
            return await step_context.begin_dialog("WFDialogStampaMigliriCripto")
        if path=="4" or path.lower()=="esci":
            return await step_context.end_dialog()

    #Metodi per il WaterfallDialog: 'WFDialogTracciaCripto'
    async def insert_symbol_cripto_to_follow_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "insert_symbol_cripto_to_follow",
            PromptOptions( # controllo se esiste la cripto
                prompt=MessageFactory.text("Inserisci simbolo della cripto che vuoi seguire:"),
                retry_prompt=MessageFactory.text("Inserisci un simbolo valido e che non segui (ad esempio 'BTC').")
            )
        )

    async def insert_valore_da_tracciare_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        cripto_found = step_context.result
        step_context.values["cripto_found"] = cripto_found
        step_context.values["symbol_cripto"] = str(cripto_found["symbol_name"]).upper()

        # stampo cripto trovata
        text = f"------- Cripto trovata! ------- \n\n"\
               f"Nome cripto: {cripto_found['nome_cripto']}, \n\n"\
               f"Symbol: {cripto_found['symbol_name']}, \n\n"\
               f"Prezzo: ${'{:.2f}'.format(cripto_found['prezzo'])}, \n\n"\
               f"Variazione24h: {'{:.2f}'.format(cripto_found['variazione24h'])}%\n\n"
        await step_context.context.send_activity(
            MessageFactory.text(text)
        )

        # chiedo il valore da tracciare
        return await step_context.prompt(
            "insert_valore_da_tracciare",
            PromptOptions( #controllo se il valore da tracciare è valido
                prompt=MessageFactory.text("Inserisci valore da tracciare:"),
                retry_prompt=MessageFactory.text("Inserisci un valore da tracciare valido (maggiore di 0).")
            )
        )

    async def insert_maggiore_minore_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["valore_da_tracciare"] = float(step_context.result)
        valore_da_tracciare = step_context.values["valore_da_tracciare"]

        return await step_context.prompt(
            "insert_maggiore_minore",
            PromptOptions(
                prompt=MessageFactory.text(f"Scegli quando vuoi essere notificato: \n\n"
                                           f"'maggiore' = quando il valore della cripto supera '{valore_da_tracciare}' \n\n"
                                           f"'minore' = quando il valore della cripto è inferiore rispetto a '{valore_da_tracciare}'"),
                choices=[Choice("maggiore"), Choice("minore")]
            )
        )

    async def confirm_cripto_to_follow_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["maggiore_minore"] = str(step_context.result.value).lower()
        if (step_context.values["maggiore_minore"] == "maggiore"):
            maggiore_minore = ">"
        else:
            maggiore_minore = "<"
        valore_da_tracciare = step_context.values["valore_da_tracciare"]

        cripto = step_context.values["cripto_found"]

        await step_context.context.send_activity(
            MessageFactory.text(
                f"------- Info cripto da tracciare ------- \n\n"
                f"Nome cripto: {cripto['nome_cripto']}, \n\n"
                f"Symbol: {cripto['symbol_name']}, \n\n"
                f"Prezzo: ${'{:.2f}'.format(cripto['prezzo'])}, \n\n"
                f"Variazione24h: {'{:.2f}'.format(cripto['variazione24h'])}%\n\n"
                f"------- Quando vuoi essere notificato -------\n\n"
                f"Valore da tracciare: {valore_da_tracciare}, \n\n"
                f"Ti notifichiamo quando il valore della cripto è '{maggiore_minore}' rispetto al valore da tracciare"
            )
        )

        return await step_context.prompt(
            "confirm_tracciamento_cripto",
            PromptOptions(
                prompt=MessageFactory.text(f"Confermi il tracciamento su tale cripto?")
            )
        )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_tracciamento_cripto = step_context.result

        if confirm_tracciamento_cripto:
            symbol_cripto = str(step_context.values["symbol_cripto"])
            valore_da_tracciare = step_context.values["valore_da_tracciare"]
            maggiore_minore = step_context.values["maggiore_minore"]
            if (maggiore_minore == "maggiore"):
                maggiore_minore = True
            else:
                maggiore_minore = False
            DatabaseManager.aggiungi_cripto_utente(
                id=step_context.context.activity.from_property.id,
                symbol_cripto_tracciata=symbol_cripto.upper(),
                valore_da_tracciare=valore_da_tracciare,
                maggiore = maggiore_minore
            )
            await step_context.context.send_activity(MessageFactory.text("Cripto tracciata!"))
            return await step_context.replace_dialog("WFDialogMenuTracciaCripto")
        else:
            return await step_context.replace_dialog("WFDialogMenuTracciaCripto")

    #Metodi per il WaterfallDialog: 'WFDialogEliminaCripto'
    async def insert_symbol_cripto_to_remove_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        lista_cripto_tracciate = DatabaseManager.get_lista_cripto_tracciate(step_context.context.activity.from_property.id)

        if (len(lista_cripto_tracciate)>0): #Se l'utente segue almeno una cripto allora gliele mostro
            text = f"Crypto tracciate: "
            for cripto in lista_cripto_tracciate.split(", "):
                text += f"{cripto}, "
            await step_context.context.send_activity(MessageFactory.text(text))

            return await step_context.prompt(
                "insert_symbol_cripto_to_remove",
                PromptOptions( # controllo se l'utente segue il symbol della cripto che ha inserito
                    prompt=MessageFactory.text("Inserisci il simbolo della cripto che vuoi rimuovere (ad esempio 'BTC'):"),
                    retry_prompt=MessageFactory.text("Inserisci il simbolo di una cripto che segui (ad esempio 'BTC' se la segui).")
                )
            )
        else:
            await step_context.context.send_activity(MessageFactory.text("Non segui nessuna cripto!"))
            return await step_context.replace_dialog("WFDialogMenuTracciaCripto")

    async def remove_cripto_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        symbol_cripto_to_remove = str(step_context.result).upper()

        DatabaseManager.elimina_cripto_utente(
            id=step_context.context.activity.from_property.id,
            symbol_cripto_tracciata=symbol_cripto_to_remove
        )
        await step_context.context.send_activity(MessageFactory.text("Cripto rimossa"))
        return await step_context.replace_dialog("WFDialogMenuTracciaCripto")

    # Metodi per il WaterfallDialog: 'WFDialogStampaMigliriCripto'
    async def insert_number_of_cripto_to_show_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "number_cripto_to_show",
            PromptOptions(
                prompt=MessageFactory.text("Quante cripto vuoi visualizzare?"),
                retry_prompt=MessageFactory.text("Inserisci un valore valido (1<= numero <=50).")
            )
        )

    async def show_migliori_cripto_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["num_cripto_to_show"] = int(step_context.result)

        num_cripto_to_show = int(step_context.result)

        lista_cripto_migliori_cripto = CriptoManager.get_lista_migliori_cripto(numero_di_cripto_da_restituire=num_cripto_to_show)
        text = "Lista migliori cripto:\n\n \n\n"
        i = 0

        for cripto in lista_cripto_migliori_cripto:
            text += f"{i}) " \
                      f"Nome cripto: {cripto['nome_cripto']}, " \
                      f"Symbol: {cripto['symbol_name']}, " \
                      f"Prezzo: ${'{:.2f}'.format(cripto['prezzo'])}, " \
                      f"Variazione24h: {'{:.2f}'.format(cripto['variazione24h'])}%\n\n"
            i += 1

        await step_context.context.send_activity(
            MessageFactory.text(text)
        )
        return await step_context.replace_dialog("WFDialogMenuTracciaCripto")

    # Metodi d'appoggio
    @staticmethod
    async def validate_symbol_cripto(prompt_context: PromptValidatorContext) -> bool:
        symbol = str(prompt_context.recognized.value).upper()

        #controllo se l'utente segue già la cripto
        id_user = prompt_context.context.activity.from_property.id
        lista_cripto_tracciate = DatabaseManager.get_lista_cripto_tracciate(id_user)
        if (symbol in lista_cripto_tracciate):
            return False

        #controllo se la cripto esiste
        cripto_found = CriptoManager.get_cripto(symbol)
        if (cripto_found is None):
            return False

        prompt_context.recognized.value = cripto_found
        return True

    @staticmethod
    async def validate_valore_da_tracciare(prompt_context: PromptValidatorContext) -> bool:
        try:
            valore_da_tracciare = float(prompt_context.recognized.value)
            if (valore_da_tracciare>0):
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    async def validate_symbol_cripto_to_remove(prompt_context: PromptValidatorContext) -> bool:
        symbol_to_remove = str(prompt_context.recognized.value).upper()

        # controllo se è un int oppure float: il metodo "float" controlla entrambe le cose
        try:
            float(symbol_to_remove)
            return False
        except:
            # controllo se l'utente segue la cripto
            id_user = prompt_context.context.activity.from_property.id
            lista_cripto_tracciate = DatabaseManager.get_lista_cripto_tracciate(id_user).split(", ")
            for symbol_in_list in lista_cripto_tracciate:
                sym = symbol_in_list.split(":")[0]
                if (symbol_to_remove == sym):
                    return True

            return False

    @staticmethod
    async def validate_num_cripto_to_show(prompt_context: PromptValidatorContext) -> bool:
        try:
            num_cripto_to_show = int(prompt_context.recognized.value)
            if (num_cripto_to_show>=1 and num_cripto_to_show<=50):
                return True
            else:
                return False
        except:
            return False