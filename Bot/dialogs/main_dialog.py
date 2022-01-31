# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import CreateCard
from data_models.databaseManager import DatabaseManager
from .registration_dialog import RegistrationDialog
from .traccia_cripto_dialog import TracciaCriptoDialog
from .news_from_crypto_world_dialog import NewsFromCryptoWorldDialog
from .qna_maker_dialog import QnAMakerdialog
from .cripto_maggiore_incremento_24h_dialog import CriptoMaggioreIncremento24hDialog
from .cripto_in_range_dialog import CriptoInRangeDialog

#inizializzo i miei dialog
registration_dialog=RegistrationDialog()
traccia_cripto_dialog=TracciaCriptoDialog()
news_from_crypto_world_dialog=NewsFromCryptoWorldDialog()
cripto_maggiore_incremento_24h_dialog=CriptoMaggioreIncremento24hDialog()
qna_maker_dialog=QnAMakerdialog()
cripto_in_range_dialog=CriptoInRangeDialog()


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState, conversation_state):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.user_profile_accessor = user_state.create_property("UserProfile")

        # Setto gli altri dialoghi che ho bisogno
        self.registration_dialog_id = registration_dialog.id
        self.traccia_cripto_dialog_id = traccia_cripto_dialog.id
        self.news_from_crypto_world_dialog_id = news_from_crypto_world_dialog.id
        self.cripto_maggiore_incremento_dialog_id = cripto_maggiore_incremento_24h_dialog.id
        self.qna_maker_dialog_id = qna_maker_dialog.id
        self.cripto_in_range_dialog_id = cripto_in_range_dialog.id

        # Aggiungo le altri classi di dialog
        self.add_dialog(registration_dialog)
        self.add_dialog(traccia_cripto_dialog)
        self.add_dialog(news_from_crypto_world_dialog)
        self.add_dialog(cripto_maggiore_incremento_24h_dialog)
        self.add_dialog(qna_maker_dialog)
        self.add_dialog(cripto_in_range_dialog)

        # Setto gli id dei prompt che utilizzo in questa classe
        self.add_dialog(ChoicePrompt("menu"))
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                "WFDialogLogged",
                [
                    self.summary_user_profile_step,
                    self.menu_step,
                    self.function_choosed_step,
                    self.continue_with_dialog_logged_step
                ],
            )
        )

        self.add_dialog(
            WaterfallDialog(
                "WFDialogLogin",
                [
                    self.login_step,
                    self.continue_with_dialog_logged_step
                ],
            )
        )
        self.initial_dialog_id = "WFDialogLogin"
        self.conversation_state = conversation_state

    #WaterfallDialog: 'WFDialogLogin'
    async def login_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_utente = step_context.context.activity.from_property.id

        #vedo se è registrato l'utente facendomi restituire l'utente stesso nel caso in cui sia registrato, altrimenti vale False
        user_profile = DatabaseManager.user_is_registered(id_utente)

        if user_profile is False:
            await step_context.context.send_activity(
                MessageFactory.text('Non sei registrato, si procede con la fase di registrazione')
            )
            return await step_context.begin_dialog(self.registration_dialog_id)
        else:
            step_context.values["user_profile"] = user_profile
            return await step_context.next([])

    async def continue_with_dialog_logged_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.begin_dialog("WFDialogLogged")

    # WaterfallDialog: 'WFDialogLogged'
    async def summary_user_profile_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_profile = DatabaseManager.getUser(step_context.context.activity.from_property.id)

        #controllo se l'utente è registrato
        if user_profile is False:
            await step_context.context.send_activity(
                MessageFactory.text('Non sei registrato, si procede con la fase di registrazione')
            )
            return await step_context.begin_dialog(self.registration_dialog_id)

        #l'utente è registrato
        await step_context.context.send_activity(
            MessageFactory.attachment(
            CreateCard.create_user_profile_card(
                title=f"Bentornato in CryptoBot, {user_profile.getNome_utente()}!",
                subtitle=f"Ecco le tue informazioni:\n\nCrypto tracciate: {user_profile.getCripto_tracciate()}",
                text="Per iniziare ad utilizzare il bot puoi usufruire del menu sottostante!",
                url="https://www.lineaedp.it/files/2017/01/bot.jpg")
        ))
        return await step_context.next([])


    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        iduser=step_context.context.activity.from_property.id
        user_profile = DatabaseManager.getUser(iduser)
        step_context.values["user_profile"] = user_profile

        await step_context.context.send_activity(CreateCard.createMenuCardWithCarousel())
        return await step_context.prompt(
            "menu",
            PromptOptions(
                prompt=MessageFactory.text("Scegli una delle seguenti funzionalità"),
                choices=[Choice("Traccia cripto"), Choice("News"), Choice("Cripto 24h"), Choice("QnA"), Choice("Cripto in range")]
            )
        )

    async def function_choosed_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result.value

        if option.lower()=="quit" or option.lower()=="esci":
            await step_context.context.send_activity("Resettando il bot... digita qualcosa per ripartire")
            return await step_context.cancel_all_dialogs()
        if option=="1" or option=="Traccia cripto":
            return await step_context.begin_dialog(self.traccia_cripto_dialog_id)
        if (option=="2" or option=="News"):
            return await step_context.begin_dialog(self.news_from_crypto_world_dialog_id)
        if option=="3" or option=="Cripto 24h":
            return await step_context.begin_dialog(self.cripto_maggiore_incremento_dialog_id)
        if (option=="4" or option=="QnA"):
            return await step_context.begin_dialog(self.qna_maker_dialog_id)
        if option=="5" or option=="Cripto in range":
            return await step_context.begin_dialog(self.cripto_in_range_dialog_id)
        # if option=="info":
        #     info_card = self.create_adaptive_card_attachment()
        #     resp = MessageFactory.attachment(info_card)
        #     await step_context.context.send_activity(resp)
        #     return await step_context.next([])


    # Metodi di appoggio