# WiseCoach

WiseCoach is now structured as a web-first leadership basics portal built from the Leadership Journal V1.

Version 1 is designed to:

- present leadership topics in a readable learning format
- reflect the structure and themes from the Leadership Journal V1 PDF
- include short summaries, examples, case studies, and exercises
- let leaders submit feedback and topic-specific questions
- let administrators grant access and route questions
- let the people leadership team respond to submitted questions
- preserve a future path to Microsoft Teams integration

## Version 1 outcomes

The first version should help the organization do three things well:

1. Publish leadership basics content in a structured format.
2. Collect learner feedback and topic-specific questions.
3. Route questions from leaders to the people leadership team through an administrator workflow.

## Roles

- `Leader`: consumes content, completes exercises, gives feedback, and asks questions.
- `Administrator`: grants access, reviews feedback, and assigns questions.
- `People leadership team`: reviews assigned questions and provides responses.

## Core capabilities

### 1. Leadership topic pages

Each topic can include:

- short summary
- key concepts
- examples
- case study
- exercises

### 2. Leader interaction

Leaders can:

- read assigned topics
- submit content feedback
- ask questions tied to a topic

### 3. Administrator workflow

Administrators can:

- grant content access
- review feedback
- assign questions to the right people leadership team member

### 4. People leadership workflow

The people leadership team can:

- view assigned questions
- respond with guidance
- build a feedback loop for future content improvements

## Recommended MVP architecture

- `Client`: Web application first, with Teams integration added later using the same service layer.
- `API`: Backend service for profile, goals, prompts, tips, and Q&A orchestration.
- `Coaching engine`: Logic that combines user profile, preferences, and recent activity.
- `Content retrieval layer`: Search and retrieve chunks from approved internal leadership content.
- `Data store`: Structured storage for profiles, goals, events, and user preferences.
- `LLM layer`: Generates tips, coaching prompts, summaries, and grounded answers.

## Current scaffold in this workspace

- `app/`: FastAPI app, storage, and role-based portal logic.
- `templates/` and `static/`: the WiseCoach web experience.
- `data/`: persistent local data for users, access, feedback, and questions.
- `data/leadership-journal-extract.txt`: extracted text from the source PDF used to structure the portal topics.
- `teams/`: future Teams integration assets kept for later.

## Web app path

The browser experience is available at `/` and currently supports:

- leadership topic reading
- leader feedback submission
- leader question submission
- administrator access and assignment flow
- people leadership team responses

## Future Teams bot path

The project now includes a Bot Framework-compatible endpoint at `POST /api/messages`.
Microsoft Teams can send activities to that endpoint after the bot is registered and the app credentials are configured.

See [docs/solution-blueprint.md](C:\Users\Srikanth.Parthasarat\OneDrive - WiseTech Global Pty Ltd\Documents\Leadership Coach\docs\solution-blueprint.md) for details.

## Suggested MVP backlog

1. Leader onboarding form and profile storage.
2. Daily tip generation service.
3. Issue intake and prompt generation workflow.
4. Goal tracking data model and check-in flow.
5. Leadership content ingestion and retrieval.
6. Teams-ready authentication and delivery model.

## Assumptions

- Leadership content already exists in documents, presentations, wiki pages, or PDFs.
- The first release can be web-based, with Teams integration added after the core experience is stable.
- Answers to company-specific questions must be grounded in approved content rather than free-form model output.

## Local startup

After installing dependencies:

```powershell
python -m uvicorn app.main:app --reload
```

## Next build step

Refine the topic pages further using the exact source content and then add authentication.
