from __future__ import annotations

BOT_FRAMEWORK_AVAILABLE = False
adapter = None
bot = None

try:
    from botbuilder.core import TurnContext
    from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

    from app.bot import LeadershipCoachBot
    from app.config import settings

    bot = LeadershipCoachBot()
    bot_framework_authentication = ConfigurationBotFrameworkAuthentication(settings.bot_auth_config)
    adapter = CloudAdapter(bot_framework_authentication)
    BOT_FRAMEWORK_AVAILABLE = True

    async def on_error(turn_context: TurnContext, error: Exception) -> None:
        await turn_context.send_activity("WiseCoach hit an unexpected error.")
        raise error


    adapter.on_turn_error = on_error
except ModuleNotFoundError:
    pass
