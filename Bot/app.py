# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes, ConversationReference, ChannelAccount

from config import DefaultConfig
from dialogs import MainDialog
from bots import WelcomeUserBot

from helpers import notify_helper
from helpers.notify_helper import invia_messaggio

CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error]: { error }", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )

        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

    # Clear out state
    await CONVERSATION_STATE.delete(context)


# Set the error handler on the Adapter.
# In this case, we want an unbound method, so MethodType is not needed.
ADAPTER.on_turn_error = on_error

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)

# Create main dialog, dialogs and bot
DIALOG = MainDialog(USER_STATE, CONVERSATION_STATE)
# Create a conversation references
CONVERSATION_REFERENCES: Dict[str, ConversationReference] = dict()

# Create Bot
BOT = WelcomeUserBot(CONVERSATION_STATE, USER_STATE, DIALOG, conversation_references=CONVERSATION_REFERENCES)


# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)

# Listen for requests on /api/notify, and send a message only to 1 person, by Vincenzo Marrazzo(xzan8189)
async def notify(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()

        await _send_proactive_message(body)
        return Response(status=HTTPStatus.OK, text="Proactive messages have been sent")

    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

async def _send_proactive_message(body: Any):
    print("Len: " + str(len(CONVERSATION_REFERENCES.values())))

    for conversation_reference in CONVERSATION_REFERENCES.values():
        user: ChannelAccount = conversation_reference.user
        if (user.id == body['id']):
            callback=invia_messaggio(
                id= user.id,
                body=body
            )
            await ADAPTER.continue_conversation(
                conversation_reference,
                callback,
                CONFIG.APP_ID,
            )
    print("Fine")

APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_post("/api/notify", notify)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
