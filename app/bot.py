from __future__ import annotations

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount

from app.models import TeamsMessageRequest
from app.services import teams_bot


class LeadershipCoachBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext) -> None:
        activity = turn_context.activity
        account = activity.from_property

        leader_id = self._resolve_leader_id(account)
        message_text = (activity.text or "").strip()

        response = teams_bot.handle_message(
            TeamsMessageRequest(
                leader_id=leader_id,
                message=message_text,
                conversation_id=activity.conversation.id if activity.conversation else None,
                channel=activity.channel_id or "teams",
            )
        )

        reply_text = response.text
        if response.citations:
            sources = ", ".join(citation.title for citation in response.citations)
            reply_text = f"{reply_text}\n\nSources: {sources}"

        if response.suggested_actions:
            suggestion_text = " | ".join(response.suggested_actions)
            reply_text = f"{reply_text}\n\nTry next: {suggestion_text}"

        await turn_context.send_activity(MessageFactory.text(reply_text))

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ) -> None:
        bot_id = turn_context.activity.recipient.id if turn_context.activity.recipient else None
        for member in members_added:
            if member.id != bot_id:
                await turn_context.send_activity(
                    MessageFactory.text(
                "LeadWise is ready. Send `tip` for a daily coaching tip or "
                        "`ask: <question>` for a company-grounded leadership answer."
                    )
                )

    @staticmethod
    def _resolve_leader_id(account: ChannelAccount | None) -> str:
        if not account:
            return "anonymous"

        aad_object_id = getattr(account, "aad_object_id", None)
        return aad_object_id or account.id or "anonymous"
