# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import ssl
from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState, MessageFactory, CardFactory
from botbuilder.dialogs import Dialog
from botbuilder.schema import HeroCard, CardImage, ChannelAccount, Activity, ConversationReference
from typing import Dict
from helpers.dialog_helper import DialogHelper


class WelcomeUserBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState, dialog: Dialog,
                 conversation_references: Dict[str, ConversationReference]):
        if conversation_state is None:
            raise TypeError("[WelcomeUserBot]: Missing parameter. conversation_state is required but None was given")
        if user_state is None:
            raise TypeError("[WelcomeUserBot]: Missing parameter. user_state is required but None was given")
        if dialog is None:
            raise Exception("[WelcomeUserBot]: Missing parameter. dialog is required")

        self.conversation_references = conversation_references
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)


    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                conversation_reference = TurnContext.get_conversation_reference(turn_context.activity)
                self.conversation_references[conversation_reference.user.id] = conversation_reference
                await self.__send_intro_card(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )
        # serve per recuperare il "turn_context" per darlo in pasto al QnAMaker che altrimenti non ci trova le answers senza questo oggetto
        await self.conversation_state.save_changes(turn_context)

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        return await super().on_conversation_update_activity(turn_context)

    def _add_conversation_reference(self, activity: Activity):
        """
        This populates the shared Dictionary that holds conversation references. In this sample,
        this dictionary is used to send a message to members when /api/notify is hit.
        :param activity:
        :return:
        """
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[conversation_reference.user.id] = conversation_reference

    async def __send_intro_card(self, turn_context: TurnContext):
        card = HeroCard(
            title="Benvenuto nel bot CryptoBot!",
            subtitle="Speriamo che l'utilizzo di questo bot venga in tuo aiuto!",
            text="Scrivi qualcosa per far partire il bot!!",
            images=[CardImage(url="https://static.news.bitcoin.com/wp-content/uploads/2018/04/bitcoin-trading-bot.jpg")],

        )
        await turn_context.send_activity(
            MessageFactory.attachment(CardFactory.hero_card(card))
        )