from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, ConfirmPrompt, WaterfallDialog, WaterfallStepContext, \
    DialogTurnResult, PromptOptions

from data_models.SearchBing import SearchBing
from data_models.Utils import Utils
from data_models import CreateCard


class NewsFromCryptoWorldDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(NewsFromCryptoWorldDialog, self).__init__(dialog_id or NewsFromCryptoWorldDialog.__name__)

        self.add_dialog(ConfirmPrompt("confirm_show_other_news"))
        self.add_dialog(
            WaterfallDialog(
                "WFDialogNews",
                [
                    self.show_news_step,
                    self.confirm_show_other_news_step,
                    self.loop_step,
                    self.end_news_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogNews"

    async def show_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        all_news = SearchBing.get_news(numero_di_notizie=3)

        await step_context.context.send_activity(CreateCard.createCarouselWithNews(all_news))
        return await step_context.next([])

    async def confirm_show_other_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "confirm_show_other_news",
            PromptOptions(
                prompt=MessageFactory.text(Utils.replace_escapes(f"Ricaricare le notizie?")),
            ),
        )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_show_other_news = step_context.result
        if confirm_show_other_news:
            return await step_context.replace_dialog("WFDialogNews")
        else:
            return await step_context.next([])

    async def end_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()