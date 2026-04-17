# Solution Blueprint

## Product vision

LeadWise is a digital coaching companion that helps leaders improve their effectiveness through personalized guidance, structured reflection, and grounded answers based on company leadership content.

## Core use cases

### Use case 1: Onboard a leader

The leader completes an onboarding flow that captures:

- role
- title
- function
- location
- number of direct and indirect reports
- total years of leadership experience
- whether they are new to leadership
- strengths
- improvement areas
- leadership preferences such as concise tips, reflective prompts, or action-oriented advice

### Use case 2: Receive a daily tip

Each day, the system generates a short tip that considers:

- leader profile
- goals
- recent coaching topics
- preferred style
- cadence and channel

### Use case 3: Raise an issue

The leader submits a challenge in free text. The system classifies the issue, summarizes it, and responds with:

- reflection prompts
- practical next steps
- coaching questions
- related internal content when applicable

### Use case 4: Track growth

The leader creates goals and reviews progress through milestones, self-check-ins, and trend summaries.

### Use case 5: Ask a company-specific question

The leader asks a question like:

- "What does good delegation look like here?"
- "What is expected from managers during performance reviews?"
- "How should I prepare for a difficult feedback conversation based on our leadership principles?"

The answer should cite the most relevant internal leadership content used.

## Functional requirements

### Leader profile

- Create and update a leadership profile.
- Store demography and coaching preferences.
- Track strengths and improvement areas.
- Capture onboarding timestamp and profile completeness.

### Daily coaching

- Generate personalized tips.
- Respect frequency and preference settings.
- Avoid repetition.
- Connect tips to current goals and issues when relevant.

### Issue coaching

- Accept free-text issues.
- Tag issues by leadership theme.
- Generate prompts, reflection questions, and suggested actions.
- Optionally create a follow-up task or goal linkage.

### Goal tracking

- Create goals with category, target date, and success criteria.
- Support milestones and recurring check-ins.
- Store progress updates and confidence scores.
- Summarize progress over time.

### Content-grounded Q&A

- Ingest approved leadership content.
- Chunk and index content for retrieval.
- Use retrieved passages to ground answers.
- Return references and confidence indicators.
- Avoid unsupported claims when content is missing.

## Non-functional requirements

- Privacy-aware handling of leader data.
- Role-based access to internal content.
- Auditability for retrieved content in grounded answers.
- Extensible design for Teams and web channels.
- Configurable prompt and retrieval logic.

## Domain model

### Core entities

- `LeaderProfile`
- `LeadershipPreference`
- `CoachingIssue`
- `DailyTip`
- `DevelopmentGoal`
- `GoalCheckIn`
- `ContentDocument`
- `ContentChunk`
- `GroundedAnswer`

## Logical architecture

### 1. Experience layer

- Web app for MVP
- Future Microsoft Teams tab
- Future Teams bot for notifications and chat-style coaching

### 2. Application layer

- Profile service
- Coaching service
- Goal service
- Content service
- Notification service

### 3. Intelligence layer

- Classification and tagging
- Tip generation
- Prompt generation
- Retrieval-augmented Q&A

### 4. Data layer

- Relational database for structured user data
- Vector index for leadership content chunks
- Document storage for raw source material

## Recommended API surface

### Profile APIs

- `POST /profiles`
- `GET /profiles/{leaderId}`
- `PATCH /profiles/{leaderId}`

### Tips APIs

- `POST /tips/generate`
- `GET /tips/history/{leaderId}`

### Issue APIs

- `POST /issues`
- `POST /issues/{issueId}/coach`

### Goal APIs

- `POST /goals`
- `PATCH /goals/{goalId}`
- `POST /goals/{goalId}/checkins`
- `GET /goals/{leaderId}`

### Content Q&A APIs

- `POST /content/ingest`
- `POST /ask`
- `GET /content/search`

## Content ingestion approach

1. Collect approved leadership materials.
2. Normalize documents into plain text with metadata.
3. Chunk content into retrieval-friendly passages.
4. Store embeddings and metadata.
5. Use retrieval before answer generation.
6. Return grounded citations in every company-specific answer.

## Teams integration path

### Phase 1

Build as a web app with clean APIs and authentication.

### Phase 2

Expose inside Teams as:

- a personal tab for dashboard, profile, goals, and daily tips
- a bot for chat-based coaching and notifications
- adaptive cards for daily prompts and goal reminders

### Phase 3

Add Teams workflow enhancements:

- proactive messages
- reminders
- manager check-in nudges
- links to internal leadership resources

## Risks to design for early

- hallucinated answers if content grounding is weak
- privacy concerns around sensitive coaching issues
- generic tips if the profile model is too shallow
- low engagement if daily tips become repetitive
- content drift if source documents are not curated

## Recommended MVP success metrics

- onboarding completion rate
- daily tip open rate
- issue-to-action conversion rate
- active goals per leader
- grounded answer usefulness rating
- weekly returning leaders
