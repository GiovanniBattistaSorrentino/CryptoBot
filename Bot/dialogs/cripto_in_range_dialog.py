from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, TextPrompt, ConfirmPrompt, WaterfallDialog, WaterfallStepContext, \
    DialogTurnResult, PromptOptions, PromptValidatorContext

from data_models.criptoManager import CriptoManager


class CriptoInRangeDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(CriptoInRangeDialog, self).__init__(dialog_id or CriptoInRangeDialog.__name__)

        self.add_dialog(TextPrompt("min_range", CriptoInRangeDialog.validate_for_min_and_max_value))
        self.add_dialog(TextPrompt("max_range", CriptoInRangeDialog.validate_for_min_and_max_value))
        self.add_dialog(ConfirmPrompt("confirm_range"))
        self.add_dialog(ConfirmPrompt("confirm_loop_2"))
        self.add_dialog(TextPrompt("cripto_to_show", CriptoInRangeDialog.validate_num_cripto_to_show))
        self.add_dialog(
            WaterfallDialog(
                "WFDialogCriptoInRange",
                [
                    self.insert_min_range_step,
                    self.insert_max_range_step,
                    self.check_if_range_is_valid_step,
                    self.confirm_range_step,
                    self.loop_step,
                    self.insert_number_of_cripto_to_show_step,
                    self.show_cripto_in_range_step,
                    self.loop_2_step,
                    self.end_cripto_in_range_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogCriptoInRange"

    async def insert_min_range_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "min_range",
            PromptOptions(
                prompt=MessageFactory.text("Inserisci prezzo della cripto minimo:"),
                retry_prompt=MessageFactory.text("Inserisci un valore minimo valido (maggiore di 0).")
            )
        )

    async def insert_max_range_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["min_range_value"] = float(step_context.result)
        return await step_context.prompt(
            "max_range",
            PromptOptions(
                prompt=MessageFactory.text("Inserisci prezzo della cripto massimo:"),
                retry_prompt=MessageFactory.text("Inserisci un valore massimo valido (maggiore di 0).")
            )
        )

    async def check_if_range_is_valid_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["max_range_value"] = float(step_context.result)
        min_value = step_context.values["min_range_value"]
        max_value = step_context.values["max_range_value"]

        if (min_value <= max_value):
            return await step_context.next([])
        else:
            await step_context.context.send_activity(
                MessageFactory.text(
                    f"Prezzo Minimo: {min_value}\n\n"
                    f"Prezzo Massimo: {max_value}\n\n"
                    f"Il valore massimo '{max_value}' è minore del valore minimo '{min_value}'!\n\n"
                    f"Hai sbagliato intervallo.. si riinizia"
                )
            )
            return await step_context.replace_dialog("WFDialogCriptoInRange")

    async def confirm_range_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        min_value = step_context.values["min_range_value"]
        max_value = step_context.values["max_range_value"]
        return await step_context.prompt(
            "confirm_range",
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Confermi intervallo?\n\n"
                    f"Min_value: {min_value}\n\n"
                    f"Max_value: {max_value}")
            )
        )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_range = step_context.result

        if confirm_range:
            return await step_context.next([])
        else:
            return await step_context.replace_dialog("WFDialogCriptoInRange")

    async def insert_number_of_cripto_to_show_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "cripto_to_show",
            PromptOptions(
                prompt=MessageFactory.text("Quante cripto massimo vuoi visualizzare?"),
                retry_prompt=MessageFactory.text("Inserisci un valore valido (maggiore di 0 e minore di 51).")
            )
        )

    async def show_cripto_in_range_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result_activity = await step_context.context.send_activity(
            MessageFactory.text("Attendi..")
        )
        step_context.values["num_cripto_to_show"] = int(step_context.result)

        num_cripto_to_show = int(step_context.result)
        min_value = step_context.values["min_range_value"]
        max_value = step_context.values["max_range_value"]

        lista_cripto_in_range = CriptoManager.get_lista_cripto_in_un_range(
            min_range=min_value,
            max_range=max_value,
            numero_di_cripto_da_restituire=num_cripto_to_show)
        text = "Cripto in range:\n\n \n\n"
        i = 0

        for cripto in lista_cripto_in_range:
            text += f"{i}) " \
                      f"Nome cripto: {cripto['nome_cripto']}, " \
                      f"Symbol: {cripto['symbol_name']}, " \
                      f"Prezzo: ${'{:.2f}'.format(cripto['prezzo'])}, " \
                      f"Variazione24h: {'{:.2f}'.format(cripto['variazione24h'])}%\n\n"
            i += 1

        msg_to_send = MessageFactory.text(text)
        msg_to_send.id = result_activity.id
        await step_context.context.update_activity(
            msg_to_send
        )

        if len(lista_cripto_in_range)<num_cripto_to_show:
            msg =f"Hai voluto visualizzare {num_cripto_to_show} cripto,\n\n"\
                 f"ma nella ricerca sono state trovate {len(lista_cripto_in_range)} cripto!\n\n"\
                 f"Vuoi riprovare?"
        else:
            msg = f"Hai voluto visualizzare {num_cripto_to_show} cripto.\n\n" \
                  f"Vuoi riprovare?"

        return await step_context.prompt(
            "confirm_loop_2",
            PromptOptions(
                prompt=MessageFactory.text(msg),
            ),
        )

    async def loop_2_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        riprovare = step_context.result

        if riprovare:
            return await step_context.replace_dialog("WFDialogCriptoInRange")
        else:
            return await step_context.next([])

    async def end_cripto_in_range_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()

    # Metodi d'appoggio
    @staticmethod
    async def validate_for_min_and_max_value(prompt_context: PromptValidatorContext) -> bool:
        try:
            range = float(prompt_context.recognized.value)
            if (range>0):
                return True
            else:
                return False
        except:
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