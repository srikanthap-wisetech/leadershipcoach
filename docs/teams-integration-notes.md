# Microsoft Teams Integration Notes

## Why Teams should come after the MVP

The core coaching flows should work well before packaging the solution for Teams. That keeps the Teams app thin and makes the product easier to test, secure, and evolve.

## Best future Teams surfaces

### Personal tab

Use for:

- profile management
- daily tips feed
- development goals dashboard
- issue history and reflection prompts

### Bot

Use for:

- conversational coaching
- asking leadership questions
- proactive daily tips
- reminders for goals and check-ins

### Adaptive cards

Use for:

- daily tip delivery
- goal check-in prompts
- suggested next actions

## Integration design principles

- Keep business logic in backend APIs, not inside the Teams app.
- Treat Teams as one delivery channel.
- Use Teams SSO or Microsoft identity for user authentication.
- Keep company content retrieval and citations server-side.

## Suggested rollout path

1. Build a browser-based MVP.
2. Stabilize profile, goals, daily tips, and grounded Q&A.
3. Add Teams personal tab using the same web app.
4. Add a Teams bot for chat-based coaching.
5. Add proactive notifications for daily tips and goal reminders.

## Teams-ready requirements to preserve now

- stable user identity mapping
- API-first design
- channel-aware notification preferences
- concise card-friendly content responses
- audit-friendly citations for grounded answers

## Example Teams scenarios

### Daily tip

The leader receives an adaptive card in Teams with:

- today's tip
- why it was chosen
- one reflection question
- a button to update a goal or raise an issue

### Coaching issue

The leader messages the bot:

"I need help giving feedback to a strong performer who is missing deadlines."

The bot responds with:

- a reframed summary
- three coaching prompts
- a suggested conversation opener
- links to relevant company leadership content if available

### Company-specific question

The leader asks:

"What leadership behavior is expected during performance calibration?"

The bot returns a grounded answer with the relevant internal references.
