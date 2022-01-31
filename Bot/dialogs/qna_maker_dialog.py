import random

import Levenshtein
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, TextPrompt, ConfirmPrompt, WaterfallDialog, WaterfallStepContext, \
    DialogTurnResult, PromptOptions

from botbuilder.schema import CardAction, ActionTypes, SuggestedActions

from data_models.qnaMakerManager import QnAMakerManager


class QnAMakerdialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(QnAMakerdialog, self).__init__(dialog_id or QnAMakerdialog.__name__)

        self.add_dialog(TextPrompt("1"))
        self.add_dialog(ConfirmPrompt("confirm_show_other_answers"))
        self.add_dialog(
            WaterfallDialog(
                "WFDialogQnAMaker",
                [
                    self.write_question_step,
                    self.show_answer_step,
                    self.confirm_show_other_answers_step,
                    self.loop_step,
                    self.end_qna_maker_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogQnAMaker"

    async def write_question_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.turn_context = step_context.context #serve per il qnaMaker per trovare le risposte

        questions = [
            "Cosa sono le criptovalute?",
            "Oltre a un metodo di pagamento, quali sono le altre funzioni delle criptovalute?",
            "Come vengono registrate le transazioni di una criptovaluta?",
            "Blockchain e criptovalute sono la stessa cosa?",
            "Aiutami con il gergo: crypto/criptovaluta, coin, token, ICO.",
            "Quali sono le migliori criptovalute?",
            "Perché ci sono così tante criptovalute?",
            "Le criptovalute possono fallire?",
            "Ho sentito che le criptovalute vengono utilizzate per attività illecite/illegali; è vero?",
            "È legale per me acquistare criptovalute negli Stati Uniti?",
            "Ok, ok, ho dollari USA: come faccio ad acquistare criptovaluta?",
            "Che cos'è un portafoglio crittografico (crypto wallet)?",
            "Quanto volatili sono le cripto?",
            "Può essere hackerato il mio wallet? E se vengo hackerato?"
            ]
        lista_suggested_actions = []
        list_random_numbers = []
        numero_di_domande_da_suggerire = 4

        print(str(len(questions)))
        while (len(list_random_numbers) < numero_di_domande_da_suggerire):
            random_num = random.randint(0, len(questions) - 1)
            if (random_num not in list_random_numbers):
                list_random_numbers.append(random_num)

        print(f"list_random_numbers: {list_random_numbers}")
        for i in list_random_numbers:
            print(f"i: {i}")
            lista_suggested_actions.append(
                CardAction(
                    type=ActionTypes.im_back,
                    title=questions[i],
                    value=questions[i],
                )
            )

        msg = MessageFactory.text("Inserisci domanda:")
        msg.suggested_actions = SuggestedActions(
            actions=lista_suggested_actions
        )

        return await step_context.prompt(
            "1",
            PromptOptions(
                prompt=msg
            )
        )

    async def show_answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        question = str(step_context.result)
        qna_maker = QnAMakerManager.get_qna_maker_top_qna()
        response = await qna_maker.get_answers(context=step_context.context)
        await qna_maker.close()

        # stampo answer
        if (response and len(response) > 0):
            if (len(response)>1):
                print("Più di una")

                lista_domande= []
                for i in range(len(response)):
                    lista_domande.append(response[i].questions[0])
                print("Lista domande trovate dal bot: \n" + str(lista_domande))

                #--------- Codice che mi calcola la similarità tra domande --------
                distances = []
                for i in range(len(response)):
                    distances.append(Levenshtein.distance(question.lower(), response[i].questions[0].lower()))

                distanza_minima = min(distances) + 7
                print("distanza minima: " + str(distanza_minima))
                max = 0
                for i in range(len(response)):
                    if (Levenshtein.distance(question, response[i].questions[0])<=distanza_minima):
                        max +=1
                        await step_context.context.send_activity(
                            MessageFactory.text(f"DOMANDA TROVATA: \n\n{response[i].questions[0]}\n\nRISPOSTA:\n\n{response[i].answer}")
                        )

                if (max >= 2):
                    await step_context.context.send_activity(
                        MessageFactory.text(f"Intendevi una di queste?")
                    )
                # --------- fine --------------

            # Se QnaMaker ha trovato una sola corrispondenza
            if (len(response)==1):
                print("Una sola")
                question = response[0].questions[0]
                answer = response[0].answer
                await step_context.context.send_activity(
                    MessageFactory.text(f"DOMANDA TROVATA: \n\n{question}\n\nRISPOSTA:\n\n{answer}")
                )
            step_context.values["ritentare"] = False

        else: # Se QnaMaker non ha trovato nessuna corrispondenza
            print("Nessuna")
            step_context.values["ritentare"] = True

        return await step_context.next([])

    async def confirm_show_other_answers_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        ritentare = step_context.values["ritentare"]
        if ritentare:
            return await step_context.prompt(
                "confirm_show_other_answers",
                PromptOptions(
                    prompt=MessageFactory.text(f"La risposta alla domanda non è stata trovata. Vuoi ritentare?"),
                ),
            )
        else:
            return await step_context.prompt(
                "confirm_show_other_answers",
                PromptOptions(
                    prompt=MessageFactory.text(f"Vuoi chiedermi qualcos'altro?"),
                ),
            )

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        confirm_show_other_answers = step_context.result
        if confirm_show_other_answers:
            return await step_context.replace_dialog("WFDialogQnAMaker")
        else:
            return await step_context.next([])

    async def end_qna_maker_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()

