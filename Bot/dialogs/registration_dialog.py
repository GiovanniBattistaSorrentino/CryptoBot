from botbuilder.dialogs import ComponentDialog, DialogTurnResult, PromptValidatorContext, \
    PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext, ConfirmPrompt
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints

from data_models.databaseManager import DatabaseManager


# Dati del database


class RegistrationDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        self.add_dialog(TextPrompt("1", RegistrationDialog.validate))
        self.add_dialog(ConfirmPrompt("confirm_nome_utente"))
        self.add_dialog(
            WaterfallDialog(
                "WFDialogRegistration",
                [
                    self.insert_nome_utente_step,
                    self.confirm_nome_utente_step,
                    self.loop_step,
                    self.register_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogRegistration"

    async def insert_nome_utente_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "1",
            PromptOptions(
                prompt=MessageFactory.text("Inserisci nome utente:"),
                retry_prompt=MessageFactory.text("Inserisci un nome utente valido (num. di caratteri <20).")
            )
        )

    async def confirm_nome_utente_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["nome_utente"] = step_context.result
        return await step_context.prompt(
            "confirm_nome_utente",
            PromptOptions(
                prompt=MessageFactory.text(f"Va bene questo nome utente: '{step_context.values['nome_utente']}'?"),
            ),
        )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_nome_utente=step_context.result
        if not confirm_nome_utente:
            return await step_context.replace_dialog("WFDialogRegistration")
        else:
            return await step_context.next(step_context.values["nome_utente"])

    async def register_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        nome_utente = step_context.result
        id_utente = step_context.context.activity.from_property.id

        DatabaseManager.insertUser(id_utente, nome_utente)
        user_profile = DatabaseManager.getUser(id_utente)
        if (user_profile is not None):
            print(user_profile)
        else:
            print("Non è stato trovato l'user")

        message_text = ("Registrazione andata a buon fine!")
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)
        return await step_context.end_dialog()

    # Metodi d'appoggio
    @staticmethod
    async def validate(prompt_context: PromptValidatorContext) -> bool:
        nome_utente = str(prompt_context.recognized.value)
        if (len(nome_utente)>0 and len(nome_utente)<20):
            return True
        else:
            return False



