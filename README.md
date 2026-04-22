# LeadWise

LeadWise is a web-first leadership learning portal built around WiseTech Leadership Foundations. It combines a branded landing page, a topic-driven leadership journal, a shared leader community, and internal review workflows for administrators and the people leadership team.

## What the product does today

LeadWise currently supports:

- a branded landing page with entry points into `Journal` and `Community`
- a dedicated `Actions` page for feedback, questions, and new topic suggestions
- a personal `My Activity` page that gathers each leader's conversations, notes, contributions, followed threads, and recent actions
- a topic-first leadership journal with rich topic pages
- journal search to quickly find topics by title or content
- topic summaries, deeper subtopics, practical workplace examples, case studies, quizzes, exercises, notes, suggested courses, and recommended reading
- per-topic star ratings with average scores across users
- shared feedback, question, and suggested-topic actions
- a threaded community area with topic filters, replies, support reactions, collapsible conversations, and follow-thread subscriptions
- community search to find conversations by topic, thread title, thread content, or replies
- a suggested-topic workflow from leader submission through administrator review and people leadership approval
- queued email-style alerts for followed threads when new replies are added
- local persistence for feedback, questions, notes, goals, issues, community threads, follow records, notification queue items, and workflow state
- optional PostgreSQL-backed persistence via `DATABASE_URL`, with JSON bootstrap support for migration

## Main experiences

### 1. Landing page

The landing page is the front door to LeadWise. It now includes:

- WiseTech branding and logo
- a simple path into the journal or community
- direct entry points into `Journal`, `Community`, `My Activity`, and `Actions`
- the WiseTech leadership mantra
- a quieter leadership-themed supporting graphic

### 2. LeadWise Actions

The `Actions` page is a dedicated place for leader input. It includes:

- a shared `Give Feedback` form
- a shared `Ask a Question` form
- a shared `Suggest New Topics` form
- the same backend submission flows used elsewhere in the portal, with a cleaner single-page experience

### 3. LeadWise Journal

The journal is the main learning space for leaders. It includes:

- left-side topic navigation
- topic search
- rich topic pages with overviews and structured subtopics
- practical workplace examples built into the topic flow
- case studies in popup format
- quizzes with instant results
- exercises with notes and reflections
- recommended courses
- recommended reading with Goodreads placeholders
- topic notes, case-study notes, and exercise notes
- topic ratings with average score display

### 4. LeadWise Community

The community is a thread-based discussion space for leaders. It includes:

- topic-tagged conversations
- filters to browse threads by topic
- conversation search
- replies and support reactions
- collapsible threads
- follow-thread controls
- queued email notifications for followed conversations
- a shared set of actions for feedback, questions, and topic suggestions

### 5. My Activity

The `My Activity` page is a personal workspace for leaders. It includes:

- summary cards for conversations, replies, ratings, notes, followed threads, and queued alerts
- a view of conversations started, replied to, or followed
- saved topic notes, case study reflections, and exercise reflections
- submitted ratings, questions, and topic suggestions
- supported questions and liked replies
- a recent activity timeline with links back into the journal or community

### 6. Administrator and People Leadership workflows

The portal includes internal workflow pages for:

- granting access
- reviewing feedback
- assigning questions
- reviewing suggested topics
- approving suggested topics
- shaping follow-on content once a topic suggestion is approved

## Roles

- `Leader`: reads journal content, completes quizzes and exercises, saves notes, joins community conversations, follows threads, rates topics, reviews personal activity in `My Activity`, and uses `Actions` to submit feedback, questions, and topic suggestions.
- `Administrator`: grants access, reviews feedback, routes questions, and manages suggested-topic workflow.
- `People leadership team`: answers submitted questions and reviews/approves suggested topics with content guidance.

## Current workspace structure

- `app/`: FastAPI app, portal logic, services, and storage
- `.github/workflows/`: deployment automation
- `azure/`: Azure App Service settings templates and deployment notes
- `templates/`: landing page, actions page, journal, community, my activity, admin, and people leadership templates
- `static/`: shared styling for the portal
- `data/`: local persistent JSON data and extracted journal content
- `content/`: grounded leadership content source files
- `docs/`: product and solution notes
- `teams/`: future Teams integration assets kept for later

## Production deployment path

The recommended production target for LeadWise is:

- Azure App Service (Linux) for the FastAPI app
- Azure Database for PostgreSQL Flexible Server for persistent data
- Microsoft Entra ID for SSO and role-based access
- Azure Key Vault for secrets
- Application Insights for monitoring

This workspace now includes:

- `startup.sh` for a production Gunicorn/Uvicorn startup path
- environment-variable support for deployment-friendly settings such as `APP_ENVIRONMENT`, `APP_BASE_URL`, `WEB_CONCURRENCY`, `DATABASE_URL`, and `LEADWISE_DATA_DIR`
- `.github/workflows/deploy-azure-appservice.yml` for GitHub Actions deployment to Azure App Service
- `azure/appsettings.production.sample.json` as a production App Service settings template
- `azure/provision-appservice.ps1` as a starter provisioning script for Azure resources
- deployment docs:
  - `docs/production-architecture.md`
  - `docs/deployment-checklist.md`

## Local startup

After installing dependencies:

```powershell
python -m uvicorn app.main:app --reload
```

For a production-style local start, after reinstalling dependencies:

```powershell
gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app
```

Then open:

```text
http://127.0.0.1:8000/
```

## Current routes

- `/` landing page
- `/actions` shared actions page
- `/my-activity` personal activity dashboard
- `/journal` leadership journal
- `/community` leader community
- `/admin` administrator workflow page
- `/people-leadership` people leadership workflow page

## Persistence

LeadWise stores local app state in:

- `data/leadwise-data.json`

It also includes a compatibility path from the older `wisecoach-data.json` store so existing local data is not lost.

For production-oriented environments, LeadWise can now use PostgreSQL-backed persistence by setting:

- `DATABASE_URL`
- optional `BOOTSTRAP_JSON_TO_DATABASE=true` to seed PostgreSQL from the current JSON store on first startup

## Future direction

The current version is web-first by design. The service structure still leaves room for:

- single sign-on and role-based access
- production-ready storage
- deeper analytics and reporting
- real outbound email delivery for queued thread alerts
- Teams notifications for followed conversations
- Microsoft Teams integration later using the same backend and content model
