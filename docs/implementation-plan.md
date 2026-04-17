# Implementation Plan

## Chosen direction

This project is now scaffolded as a web-first solution with:

- a backend API for all leadership coaching logic
- a browser-based LeadWise experience for profile, goals, coaching, and Q&A
- a future Teams personal tab for the same web app
- a future Teams bot for chat-based coaching and proactive tips
- adaptive cards for daily tip delivery and check-ins

## Current scaffold

### Backend

- `app/main.py` exposes the starter API.
- `app/models.py` defines the domain models.
- `app/services.py` provides in-memory services for the MVP.
- `content/` contains local leadership source material used for grounded answers.
- `app/bot.py`, `app/bot_adapter.py`, and `app/config.py` provide the real Bot Framework adapter path for Teams.

### Web app

- `templates/index.html` provides the main browser-based LeadWise UI.
- `static/styles.css` provides the visual design for the MVP.

### Teams app

- `teams/manifest.template.json` is a placeholder Teams manifest.
- `teams/adaptive-cards/daily-tip-card.json` is a starter adaptive card for proactive tip delivery.

## Current bot contract

The workspace now has two bot-facing options:

- `POST /api/messages` for the real Bot Framework / Microsoft Teams adapter flow
- `POST /teams/messages` as a simplified local JSON endpoint for testing service logic

Supported message patterns inside the bot:

- `tip`
- `ask: <question>`

This keeps the bot layer thin while the backend owns coaching and retrieval logic.

## Recommended next implementation steps

1. Add persistent storage for profiles, goals, issues, and check-ins.
2. Add Microsoft identity and Teams SSO.
3. Add persistence and metadata for uploaded leadership documents.
4. Replace keyword retrieval with embedding-based search and answer synthesis.
5. Add persistence and authentication for real users.
6. Reuse the same web app as a Teams personal tab when Teams integration is ready.

## Suggested folder ownership

- `app/`: backend domain and APIs
- `teams/`: Teams app packaging and card assets
- `docs/`: architecture, rollout, and operating model
- `schemas/`: shared model definitions for validation and integration

## Run model

The scaffold assumes this flow:

1. A leader authenticates from Teams.
2. The Teams tab calls backend APIs for profile, goals, and history.
3. The Teams bot sends messages to backend coaching endpoints.
4. The backend uses company leadership content to produce grounded answers.
5. Adaptive cards are used for proactive tips and reminders.
