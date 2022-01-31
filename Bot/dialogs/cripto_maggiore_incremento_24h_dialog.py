from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, ConfirmPrompt, WaterfallDialog, WaterfallStepContext, \
    DialogTurnResult, PromptOptions

from data_models.criptoManager import CriptoManager


class CriptoMaggioreIncremento24hDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(CriptoMaggioreIncremento24hDialog, self).__init__(dialog_id or CriptoMaggioreIncremento24hDialog.__name__)

        self.add_dialog(ConfirmPrompt("confirm_show_cripto_maggiore_incremento_24h"))
        self.add_dialog(
            WaterfallDialog(
                "WFDialogCriptoMaggioreIncremento24h",
                [
                    self.show_cripto_maggiore_incremento_24h_step,
                    self.confirm_reshow_cripto_maggiore_incremento_24h_step,
                    self.loop_step,
                    self.end_cripto_maggiore_incremento_24h_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogCriptoMaggioreIncremento24h"

    async def show_cripto_maggiore_incremento_24h_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result = await step_context.context.send_activity(
            MessageFactory.text("Attendi..")
        )
        lista_cripto_maggiore_incremento_24h = CriptoManager.get_lista_cripto_maggiore_incremento_24h(10)
        text = "Cripto con maggior incremento nelle ultime 24h:\n\n \n\n"
        i = 0

        for cripto in lista_cripto_maggiore_incremento_24h:
            text += f"{i+1}) " \
                      f"Nome cripto: {cripto['nome_cripto']}, " \
                      f"Symbol: {cripto['symbol_name']}, " \
                      f"Prezzo: ${'{:.2f}'.format(cripto['prezzo'])}, " \
                      f"Variazione24h: {'{:.2f}'.format(cripto['variazione24h'])}%\n\n"
            i += 1

        msg = MessageFactory.text(text)
        msg.id = result.id
        await step_context.context.update_activity(
            msg
        )
        return await step_context.next([])

    async def confirm_reshow_cripto_maggiore_incremento_24h_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "confirm_show_cripto_maggiore_incremento_24h",
            PromptOptions(
                prompt=MessageFactory.text(f"Vuoi aggiornare?"),
            ),
        )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_show_cripto_maggiore_incremento_24h = step_context.result

        if confirm_show_cripto_maggiore_incremento_24h:
            return await step_context.replace_dialog("WFDialogCriptoMaggioreIncremento24h")
        else:
            return await step_context.next([])

    async def end_cripto_maggiore_incremento_24h_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()

