import asyncio
import sys

from flask import Flask, request, Response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)
from botbuilder.schema import Activity
from my_bot import MyBot

LOOP = asyncio.get_event_loop()
APP = Flask(__name__, instance_relative_config=True)

SETTINGS = BotFrameworkAdapterSettings(
    '', ''
)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error]: { error }", file=sys.stderr)
    # Send a message to the user
    await context.send_activity("Oops. Something went wrong!")
    # Clear out state
    await CONVERSATION_STATE.delete(context)


ADAPTER.on_turn_error = on_error

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()

# Commented out user_state because it's not being used.
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

BOT = MyBot(CONVERSATION_STATE, USER_STATE)


@APP.route("/api/messages", methods=["POST"])
def messages():
    """Main bot message handler."""
    if request.headers["Content-Type"] == "application/json":
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = (
        request.headers["Authorization"] if "Authorization" in request.headers else ""
    )

    async def aux_func(turn_context):
        await BOT.on_turn(turn_context)

    try:
        task = LOOP.create_task(
            ADAPTER.process_activity(activity, auth_header, aux_func)
        )
        LOOP.run_until_complete(task)
        return Response(status=201)
    except Exception as exception:
        raise exception


if __name__ == "__main__":
    try:
        APP.run(debug=False, port=8422)  # nosec debug
    except Exception as exception:
        raise exception