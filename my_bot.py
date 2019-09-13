from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount

class MyBot:
    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                reply = MessageFactory.text(
                    "Welcome to My Bot. "
                    + "This bot will show you different information about KMS "
                    + "Please type anything to get started."
                )
                await turn_context.send_activity(reply)