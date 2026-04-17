from __future__ import annotations

from pathlib import Path
from datetime import UTC, datetime
from uuid import uuid4

from app.models import (
    AskRequest,
    Citation,
    CoachingIssue,
    CoachingIssueCreate,
    CoachingResponse,
    ContentDocument,
    DailyTip,
    DevelopmentGoal,
    DevelopmentGoalCreate,
    GoalCheckIn,
    GoalCheckInCreate,
    GoalStatus,
    GroundedAnswer,
    LeaderProfile,
    LeaderProfileCreate,
    TeamsMessageRequest,
    TeamsMessageResponse,
)
from app.storage import store


def utc_now() -> datetime:
    return datetime.now(UTC)


BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"


class ProfileService:
    def create_or_update(self, payload: LeaderProfileCreate) -> LeaderProfile:
        now = utc_now()
        existing = store.get_profile(payload.leader_id)
        created_at = existing.created_at if existing else now
        profile = LeaderProfile(
            **payload.model_dump(),
            created_at=created_at,
            updated_at=now,
        )
        store.upsert_profile(profile)
        return profile

    def get(self, leader_id: str) -> LeaderProfile | None:
        return store.get_profile(leader_id)


class GoalService:
    def create(self, payload: DevelopmentGoalCreate) -> DevelopmentGoal:
        now = utc_now()
        goal = DevelopmentGoal(
            goal_id=str(uuid4()),
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        store.insert_goal(goal)
        return goal

    def list_for_leader(self, leader_id: str) -> list[DevelopmentGoal]:
        return store.list_goals_for_leader(leader_id)

    def add_check_in(self, goal_id: str, payload: GoalCheckInCreate) -> GoalCheckIn | None:
        goal = store.get_goal(goal_id)
        if not goal:
            return None

        now = utc_now()
        goal.status = GoalStatus.IN_PROGRESS if goal.status == GoalStatus.NOT_STARTED else goal.status
        goal.updated_at = now
        store.update_goal(goal)

        check_in = GoalCheckIn(
            check_in_id=str(uuid4()),
            goal_id=goal_id,
            created_at=now,
            **payload.model_dump(),
        )
        store.insert_check_in(check_in)
        return check_in


class IssueService:
    def create(self, payload: CoachingIssueCreate) -> CoachingIssue:
        issue = CoachingIssue(
            issue_id=str(uuid4()),
            created_at=utc_now(),
            **payload.model_dump(),
        )
        store.insert_issue(issue)
        return issue

    def get(self, issue_id: str) -> CoachingIssue | None:
        return store.get_issue(issue_id)


class ContentService:
    def __init__(self) -> None:
        self._documents: list[ContentDocument] = []
        self.reload()

    def reload(self) -> int:
        self._documents = []
        if not CONTENT_DIR.exists():
            return 0

        for path in sorted(CONTENT_DIR.glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            title = path.stem.replace("-", " ").title()
            category = "leadership"

            lines = raw.splitlines()
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
            for line in lines:
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                    break

            self._documents.append(
                ContentDocument(
                    document_id=path.stem,
                    title=title,
                    category=category,
                    source_path=str(path),
                    content=raw,
                )
            )
        return len(self._documents)

    def list_documents(self) -> list[ContentDocument]:
        return self._documents

    def _search_documents(self, question: str) -> list[tuple[ContentDocument, int]]:
        tokens = [token.strip(".,!?():;\"'").lower() for token in question.split()]
        terms = [token for token in tokens if len(token) > 3]
        matches: list[tuple[ContentDocument, int]] = []

        for document in self._documents:
            haystack = document.content.lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                matches.append((document, score))

        return sorted(matches, key=lambda item: item[1], reverse=True)

    def answer(self, payload: AskRequest) -> GroundedAnswer:
        matches = self._search_documents(payload.question)

        if matches:
            top_matches = matches[:2]
            citations = [
                Citation(
                    document_id=document.document_id,
                    title=document.title,
                    chunk_id=f"{document.document_id}-top",
                    url=document.source_path,
                )
                for document, _score in top_matches
            ]
            themes = ", ".join(document.title for document, _score in top_matches)
            answer = (
                "I found relevant company leadership content for this question. "
                f"The strongest matches are {themes}. "
                "Use these sources to anchor the answer in local expectations, principles, and manager practices."
            )
            confidence = min(0.55 + (0.1 * top_matches[0][1]), 0.92)
            grounded = True
        else:
            answer = (
                "I could not find a strong company-specific match for that question yet. "
                "The next step is to ingest the relevant leadership documents so answers can be grounded."
            )
            citations = []
            confidence = 0.32
            grounded = False

        return GroundedAnswer(
            question=payload.question,
            answer=answer,
            grounded=grounded,
            confidence=confidence,
            citations=citations,
        )


class CoachingService:
    def __init__(self, profiles: ProfileService, goals: GoalService, issues: IssueService, content: ContentService) -> None:
        self._profiles = profiles
        self._goals = goals
        self._issues = issues
        self._content = content

    def generate_daily_tip(self, leader_id: str) -> DailyTip | None:
        profile = self._profiles.get(leader_id)
        if not profile:
            return None

        focus = profile.preferences.focus_areas[0] if profile.preferences.focus_areas else "communication"
        tone = profile.preferences.coaching_style.value

        if profile.new_to_leadership:
            message = (
                "Pick one conversation today where you slow down and confirm what success looks like. "
                "New leaders build trust quickly when expectations are explicit."
            )
            reason = "Chosen because the leader is new to leadership and benefits from high-clarity habits."
        else:
            message = (
                "Review one decision you could delegate this week and define the boundary instead of the method. "
                "That grows ownership without reducing accountability."
            )
            reason = "Chosen because experienced leaders often get the biggest lift from deliberate delegation."

        return DailyTip(
            tip_id=str(uuid4()),
            leader_id=leader_id,
            headline=f"Today's {focus} coaching tip",
            message=message,
            reason=f"{reason} Preferred coaching style: {tone}.",
            reflection_question=f"What is one {focus} behavior you want your team to notice from you this week?",
            created_at=utc_now(),
        )

    def coach_issue(self, issue_id: str) -> CoachingResponse | None:
        issue = self._issues.get(issue_id)
        if not issue:
            return None

        answer = self._content.answer(AskRequest(leader_id=issue.leader_id, question=issue.description))
        summary = (
            f"The issue centers on {issue.theme.value} and needs a response that is both clear and supportive."
        )
        prompts = [
            "What outcome do you want for the person, the team, and the work?",
            "Which facts are clear, and which parts are still assumptions?",
            "How will you describe the gap without making the conversation personal?",
        ]
        suggested_actions = [
            "Write a two-sentence description of the observed behavior and its impact.",
            "Open the conversation with curiosity, then move to expectations and support.",
            "End with one concrete next step and a follow-up date.",
        ]
        return CoachingResponse(
            summary=summary,
            prompts=prompts,
            suggested_actions=suggested_actions,
            content_references=answer.citations,
        )


class TeamsBotService:
    def __init__(self, coaching_service: CoachingService, content_service: ContentService) -> None:
        self._coaching = coaching_service
        self._content = content_service

    def handle_message(self, payload: TeamsMessageRequest) -> TeamsMessageResponse:
        message = payload.message.strip()
        lowered = message.lower()

        if lowered.startswith("ask:"):
            question = message.split(":", 1)[1].strip()
            answer = self._content.answer(AskRequest(leader_id=payload.leader_id, question=question))
            return TeamsMessageResponse(
                response_type="grounded_answer",
                text=answer.answer,
                suggested_actions=["View sources", "Ask a follow-up", "Create a goal"],
                citations=answer.citations,
            )

        if lowered.startswith("tip"):
            tip = self._coaching.generate_daily_tip(payload.leader_id)
            if not tip:
                return TeamsMessageResponse(
                    response_type="error",
                    text="I couldn't find your leadership profile yet. Create your profile first so I can tailor the coaching.",
                    suggested_actions=["Create profile"],
                )
            return TeamsMessageResponse(
                response_type="daily_tip",
                text=f"{tip.headline}\n\n{tip.message}\n\nReflection: {tip.reflection_question}",
                suggested_actions=["Open WiseCoach", "Update a goal", "Raise an issue"],
            )

        return TeamsMessageResponse(
            response_type="coaching_prompt",
            text=(
                "I can help in three ways inside Teams: send `tip` for a daily coaching tip, "
                "send `ask: <question>` for a company-grounded leadership answer, "
                "or use the app to raise an issue and track goals."
            ),
            suggested_actions=["tip", "ask: What does good delegation look like here?"],
        )


profiles = ProfileService()
goals = GoalService()
issues = IssueService()
content = ContentService()
coaching = CoachingService(profiles, goals, issues, content)
teams_bot = TeamsBotService(coaching, content)
