from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.models import (
    CoachingIssue,
    CommunityThread,
    DevelopmentGoal,
    GoalCheckIn,
    LeaderFeedback,
    LeaderProfile,
    LeaderTopicNote,
    PortalUser,
    TopicSuggestion,
    TopicQuestion,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "leadwise-data.json"
LEGACY_DB_PATH = DATA_DIR / "wisecoach-data.json"


class JsonStore:
    def __init__(self) -> None:
        self.initialize()

    @staticmethod
    def _empty_payload() -> dict:
        return {
            "profiles": {},
            "goals": {},
            "goal_checkins": {},
            "issues": {},
            "portal_users": {},
            "topic_access": {},
            "leader_feedback": {},
            "topic_suggestions": {},
            "topic_questions": {},
            "leader_notes": {},
            "community_threads": {},
        }

    def initialize(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists() and LEGACY_DB_PATH.exists():
            shutil.copy2(LEGACY_DB_PATH, DB_PATH)
        if not DB_PATH.exists():
            self._write(self._empty_payload())
        else:
            data = self._read()
            for key in ["portal_users", "topic_access", "leader_feedback", "topic_suggestions", "topic_questions", "leader_notes", "community_threads"]:
                data.setdefault(key, {})
            self._write(data)

    def upsert_profile(self, profile: LeaderProfile) -> None:
        data = self._read()
        data["profiles"][profile.leader_id] = profile.model_dump(mode="json")
        self._write(data)

    def get_profile(self, leader_id: str) -> LeaderProfile | None:
        data = self._read()
        payload = data["profiles"].get(leader_id)
        return LeaderProfile.model_validate(payload) if payload else None

    def insert_goal(self, goal: DevelopmentGoal) -> None:
        data = self._read()
        data["goals"][goal.goal_id] = goal.model_dump(mode="json")
        self._write(data)

    def list_goals_for_leader(self, leader_id: str) -> list[DevelopmentGoal]:
        data = self._read()
        goals = [
            DevelopmentGoal.model_validate(payload)
            for payload in data["goals"].values()
            if payload["leader_id"] == leader_id
        ]
        return sorted(goals, key=lambda goal: goal.created_at, reverse=True)

    def get_goal(self, goal_id: str) -> DevelopmentGoal | None:
        data = self._read()
        payload = data["goals"].get(goal_id)
        return DevelopmentGoal.model_validate(payload) if payload else None

    def update_goal(self, goal: DevelopmentGoal) -> None:
        data = self._read()
        data["goals"][goal.goal_id] = goal.model_dump(mode="json")
        self._write(data)

    def insert_check_in(self, check_in: GoalCheckIn) -> None:
        data = self._read()
        data["goal_checkins"][check_in.check_in_id] = check_in.model_dump(mode="json")
        self._write(data)

    def insert_issue(self, issue: CoachingIssue) -> None:
        data = self._read()
        data["issues"][issue.issue_id] = issue.model_dump(mode="json")
        self._write(data)

    def get_issue(self, issue_id: str) -> CoachingIssue | None:
        data = self._read()
        payload = data["issues"].get(issue_id)
        return CoachingIssue.model_validate(payload) if payload else None

    def upsert_portal_user(self, user: PortalUser) -> None:
        data = self._read()
        data["portal_users"][user.user_id] = user.model_dump(mode="json")
        self._write(data)

    def list_portal_users(self) -> list[PortalUser]:
        data = self._read()
        return [PortalUser.model_validate(payload) for payload in data["portal_users"].values()]

    def get_portal_user(self, user_id: str) -> PortalUser | None:
        data = self._read()
        payload = data["portal_users"].get(user_id)
        return PortalUser.model_validate(payload) if payload else None

    def grant_topic_access(self, user_id: str, topic_id: str) -> None:
        data = self._read()
        granted_topics = set(data["topic_access"].get(user_id, []))
        granted_topics.add(topic_id)
        data["topic_access"][user_id] = sorted(granted_topics)
        self._write(data)

    def get_topic_access(self, user_id: str) -> list[str]:
        data = self._read()
        return data["topic_access"].get(user_id, [])

    def insert_leader_feedback(self, feedback: LeaderFeedback) -> None:
        data = self._read()
        data["leader_feedback"][feedback.feedback_id] = feedback.model_dump(mode="json")
        self._write(data)

    def list_leader_feedback(self) -> list[LeaderFeedback]:
        data = self._read()
        feedback = [LeaderFeedback.model_validate(payload) for payload in data["leader_feedback"].values()]
        return sorted(feedback, key=lambda item: item.created_at, reverse=True)

    def insert_topic_suggestion(self, suggestion: TopicSuggestion) -> None:
        data = self._read()
        data["topic_suggestions"][suggestion.suggestion_id] = suggestion.model_dump(mode="json")
        self._write(data)

    def list_topic_suggestions(self) -> list[TopicSuggestion]:
        data = self._read()
        suggestions = [TopicSuggestion.model_validate(payload) for payload in data["topic_suggestions"].values()]
        return sorted(suggestions, key=lambda item: item.created_at, reverse=True)

    def get_topic_suggestion(self, suggestion_id: str) -> TopicSuggestion | None:
        data = self._read()
        payload = data["topic_suggestions"].get(suggestion_id)
        return TopicSuggestion.model_validate(payload) if payload else None

    def update_topic_suggestion(self, suggestion: TopicSuggestion) -> None:
        data = self._read()
        data["topic_suggestions"][suggestion.suggestion_id] = suggestion.model_dump(mode="json")
        self._write(data)

    def insert_topic_question(self, question: TopicQuestion) -> None:
        data = self._read()
        data["topic_questions"][question.question_id] = question.model_dump(mode="json")
        self._write(data)

    def update_topic_question(self, question: TopicQuestion) -> None:
        data = self._read()
        data["topic_questions"][question.question_id] = question.model_dump(mode="json")
        self._write(data)

    def get_topic_question(self, question_id: str) -> TopicQuestion | None:
        data = self._read()
        payload = data["topic_questions"].get(question_id)
        return TopicQuestion.model_validate(payload) if payload else None

    def list_topic_questions(self) -> list[TopicQuestion]:
        data = self._read()
        questions = [TopicQuestion.model_validate(payload) for payload in data["topic_questions"].values()]
        return sorted(questions, key=lambda item: item.updated_at, reverse=True)

    def upsert_leader_note(self, note: LeaderTopicNote) -> None:
        data = self._read()
        data["leader_notes"][note.note_id] = note.model_dump(mode="json")
        self._write(data)

    def list_leader_notes(self, user_id: str, topic_id: str) -> list[LeaderTopicNote]:
        data = self._read()
        notes = [
            LeaderTopicNote.model_validate(payload)
            for payload in data["leader_notes"].values()
            if payload["user_id"] == user_id and payload["topic_id"] == topic_id
        ]
        return sorted(notes, key=lambda item: item.updated_at, reverse=True)

    def get_leader_note(self, user_id: str, topic_id: str, exercise_id: str | None) -> LeaderTopicNote | None:
        data = self._read()
        for payload in data["leader_notes"].values():
            if payload["user_id"] == user_id and payload["topic_id"] == topic_id and payload.get("exercise_id") == exercise_id:
                return LeaderTopicNote.model_validate(payload)
        return None

    def insert_community_thread(self, thread: CommunityThread) -> None:
        data = self._read()
        data["community_threads"][thread.thread_id] = thread.model_dump(mode="json")
        self._write(data)

    def update_community_thread(self, thread: CommunityThread) -> None:
        data = self._read()
        data["community_threads"][thread.thread_id] = thread.model_dump(mode="json")
        self._write(data)

    def get_community_thread(self, thread_id: str) -> CommunityThread | None:
        data = self._read()
        payload = data["community_threads"].get(thread_id)
        return CommunityThread.model_validate(payload) if payload else None

    def list_community_threads(self) -> list[CommunityThread]:
        data = self._read()
        threads = [CommunityThread.model_validate(payload) for payload in data["community_threads"].values()]
        return sorted(threads, key=lambda item: item.updated_at, reverse=True)

    def _read(self) -> dict:
        raw = DB_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            payload = self._empty_payload()
            self._write(payload)
            return payload
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            payload = self._empty_payload()
            self._write(payload)
            return payload

    def _write(self, payload: dict) -> None:
        DB_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


store = JsonStore()
