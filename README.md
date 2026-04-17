# LeadWise

LeadWise is a web-first leadership learning portal built around WiseTech Leadership Foundations. It combines a branded landing page, a topic-driven leadership journal, a shared leader community, and internal review workflows for administrators and the people leadership team.

## What the product does today

LeadWise currently supports:

- a branded landing page with entry points into `Journal` and `Community`
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

## Main experiences

### 1. Landing page

The landing page is the front door to LeadWise. It now includes:

- WiseTech branding and logo
- a simple path into the journal or community
- the WiseTech leadership mantra
- a quieter leadership-themed supporting graphic

### 2. LeadWise Journal

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

### 3. LeadWise Community

The community is a thread-based discussion space for leaders. It includes:

- topic-tagged conversations
- filters to browse threads by topic
- conversation search
- replies and support reactions
- collapsible threads
- follow-thread controls
- queued email notifications for followed conversations
- a shared set of actions for feedback, questions, and topic suggestions

### 4. Administrator and People Leadership workflows

The portal includes internal workflow pages for:

- granting access
- reviewing feedback
- assigning questions
- reviewing suggested topics
- approving suggested topics
- shaping follow-on content once a topic suggestion is approved

## Roles

- `Leader`: reads journal content, completes quizzes and exercises, saves notes, joins community conversations, rates topics, and submits feedback/questions/topic suggestions.
- `Leader`: reads journal content, completes quizzes and exercises, saves notes, joins community conversations, follows threads, rates topics, and submits feedback/questions/topic suggestions.
- `Administrator`: grants access, reviews feedback, routes questions, and manages suggested-topic workflow.
- `People leadership team`: answers submitted questions and reviews/approves suggested topics with content guidance.

## Current workspace structure

- `app/`: FastAPI app, portal logic, services, and storage
- `templates/`: landing page, journal, community, admin, and people leadership templates
- `static/`: shared styling for the portal
- `data/`: local persistent JSON data and extracted journal content
- `content/`: grounded leadership content source files
- `docs/`: product and solution notes
- `teams/`: future Teams integration assets kept for later

## Local startup

After installing dependencies:

```powershell
python -m uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

## Current routes

- `/` landing page
- `/journal` leadership journal
- `/community` leader community
- `/admin` administrator workflow page
- `/people-leadership` people leadership workflow page

## Persistence

LeadWise stores local app state in:

- `data/leadwise-data.json`

It also includes a compatibility path from the older `wisecoach-data.json` store so existing local data is not lost.

## Future direction

The current version is web-first by design. The service structure still leaves room for:

- single sign-on and role-based access
- production-ready storage
- deeper analytics and reporting
- real outbound email delivery for queued thread alerts
- Teams notifications for followed conversations
- Microsoft Teams integration later using the same backend and content model
