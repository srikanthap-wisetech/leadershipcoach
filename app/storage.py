from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from app.models import (
    CoachingIssue,
    CommunityNotification,
    CommunityThread,
    CommunityThreadFollow,
    DevelopmentGoal,
    GoalCheckIn,
    LeaderFeedback,
    LeaderProfile,
    LeaderTopicNote,
    PortalUser,
    TopicQuestion,
    TopicSuggestion,
)

try:
    from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine, delete, select
    from sqlalchemy.engine import Engine

    SQLALCHEMY_AVAILABLE = True
except ImportError:  # pragma: no cover - optional until production deps are installed
    JSON = Column = MetaData = String = Table = create_engine = delete = select = None
    Engine = Any  # type: ignore[assignment]
    SQLALCHEMY_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("LEADWISE_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = DATA_DIR / "leadwise-data.json"
LEGACY_DB_PATH = DATA_DIR / "wisecoach-data.json"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
BOOTSTRAP_JSON_TO_DATABASE = os.getenv("BOOTSTRAP_JSON_TO_DATABASE", "true").lower() in {"1", "true", "yes"}

COLLECTIONS = (
    "profiles",
    "goals",
    "goal_checkins",
    "issues",
    "portal_users",
    "topic_access",
    "leader_feedback",
    "topic_suggestions",
    "topic_questions",
    "leader_notes",
    "community_threads",
    "community_thread_follows",
    "community_notifications",
)


class BaseStore:
    def initialize(self) -> None:
        raise NotImplementedError

    def _put_record(self, collection: str, key: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    def _get_record(self, collection: str, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def _list_records(self, collection: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def _delete_record(self, collection: str, key: str) -> None:
        raise NotImplementedError

    def upsert_profile(self, profile: LeaderProfile) -> None:
        self._put_record("profiles", profile.leader_id, profile.model_dump(mode="json"))

    def get_profile(self, leader_id: str) -> LeaderProfile | None:
        payload = self._get_record("profiles", leader_id)
        return LeaderProfile.model_validate(payload) if payload else None

    def insert_goal(self, goal: DevelopmentGoal) -> None:
        self._put_record("goals", goal.goal_id, goal.model_dump(mode="json"))

    def list_goals_for_leader(self, leader_id: str) -> list[DevelopmentGoal]:
        goals = [
            DevelopmentGoal.model_validate(payload)
            for payload in self._list_records("goals")
            if payload["leader_id"] == leader_id
        ]
        return sorted(goals, key=lambda goal: goal.created_at, reverse=True)

    def get_goal(self, goal_id: str) -> DevelopmentGoal | None:
        payload = self._get_record("goals", goal_id)
        return DevelopmentGoal.model_validate(payload) if payload else None

    def update_goal(self, goal: DevelopmentGoal) -> None:
        self._put_record("goals", goal.goal_id, goal.model_dump(mode="json"))

    def insert_check_in(self, check_in: GoalCheckIn) -> None:
        self._put_record("goal_checkins", check_in.check_in_id, check_in.model_dump(mode="json"))

    def insert_issue(self, issue: CoachingIssue) -> None:
        self._put_record("issues", issue.issue_id, issue.model_dump(mode="json"))

    def get_issue(self, issue_id: str) -> CoachingIssue | None:
        payload = self._get_record("issues", issue_id)
        return CoachingIssue.model_validate(payload) if payload else None

    def upsert_portal_user(self, user: PortalUser) -> None:
        self._put_record("portal_users", user.user_id, user.model_dump(mode="json"))

    def list_portal_users(self) -> list[PortalUser]:
        return [PortalUser.model_validate(payload) for payload in self._list_records("portal_users")]

    def get_portal_user(self, user_id: str) -> PortalUser | None:
        payload = self._get_record("portal_users", user_id)
        return PortalUser.model_validate(payload) if payload else None

    def grant_topic_access(self, user_id: str, topic_id: str) -> None:
        payload = self._get_record("topic_access", user_id) or {"topics": []}
        if isinstance(payload, list):
            granted_topics = set(payload)
        else:
            granted_topics = set(payload.get("topics", []))
        granted_topics.add(topic_id)
        self._put_record("topic_access", user_id, {"topics": sorted(granted_topics)})

    def get_topic_access(self, user_id: str) -> list[str]:
        payload = self._get_record("topic_access", user_id)
        if not payload:
            return []
        if isinstance(payload, list):
            return payload
        return payload.get("topics", [])

    def insert_leader_feedback(self, feedback: LeaderFeedback) -> None:
        self._put_record("leader_feedback", feedback.feedback_id, feedback.model_dump(mode="json"))

    def list_leader_feedback(self) -> list[LeaderFeedback]:
        feedback = [LeaderFeedback.model_validate(payload) for payload in self._list_records("leader_feedback")]
        return sorted(feedback, key=lambda item: item.created_at, reverse=True)

    def insert_topic_suggestion(self, suggestion: TopicSuggestion) -> None:
        self._put_record("topic_suggestions", suggestion.suggestion_id, suggestion.model_dump(mode="json"))

    def list_topic_suggestions(self) -> list[TopicSuggestion]:
        suggestions = [TopicSuggestion.model_validate(payload) for payload in self._list_records("topic_suggestions")]
        return sorted(suggestions, key=lambda item: item.created_at, reverse=True)

    def get_topic_suggestion(self, suggestion_id: str) -> TopicSuggestion | None:
        payload = self._get_record("topic_suggestions", suggestion_id)
        return TopicSuggestion.model_validate(payload) if payload else None

    def update_topic_suggestion(self, suggestion: TopicSuggestion) -> None:
        self._put_record("topic_suggestions", suggestion.suggestion_id, suggestion.model_dump(mode="json"))

    def insert_topic_question(self, question: TopicQuestion) -> None:
        self._put_record("topic_questions", question.question_id, question.model_dump(mode="json"))

    def update_topic_question(self, question: TopicQuestion) -> None:
        self._put_record("topic_questions", question.question_id, question.model_dump(mode="json"))

    def get_topic_question(self, question_id: str) -> TopicQuestion | None:
        payload = self._get_record("topic_questions", question_id)
        return TopicQuestion.model_validate(payload) if payload else None

    def list_topic_questions(self) -> list[TopicQuestion]:
        questions = [TopicQuestion.model_validate(payload) for payload in self._list_records("topic_questions")]
        return sorted(questions, key=lambda item: item.updated_at, reverse=True)

    def upsert_leader_note(self, note: LeaderTopicNote) -> None:
        self._put_record("leader_notes", note.note_id, note.model_dump(mode="json"))

    def list_leader_notes(self, user_id: str, topic_id: str) -> list[LeaderTopicNote]:
        notes = [
            LeaderTopicNote.model_validate(payload)
            for payload in self._list_records("leader_notes")
            if payload["user_id"] == user_id and payload["topic_id"] == topic_id
        ]
        return sorted(notes, key=lambda item: item.updated_at, reverse=True)

    def get_leader_note(self, user_id: str, topic_id: str, exercise_id: str | None) -> LeaderTopicNote | None:
        for payload in self._list_records("leader_notes"):
            if payload["user_id"] == user_id and payload["topic_id"] == topic_id and payload.get("exercise_id") == exercise_id:
                return LeaderTopicNote.model_validate(payload)
        return None

    def insert_community_thread(self, thread: CommunityThread) -> None:
        self._put_record("community_threads", thread.thread_id, thread.model_dump(mode="json"))

    def update_community_thread(self, thread: CommunityThread) -> None:
        self._put_record("community_threads", thread.thread_id, thread.model_dump(mode="json"))

    def get_community_thread(self, thread_id: str) -> CommunityThread | None:
        payload = self._get_record("community_threads", thread_id)
        return CommunityThread.model_validate(payload) if payload else None

    def list_community_threads(self) -> list[CommunityThread]:
        threads = [CommunityThread.model_validate(payload) for payload in self._list_records("community_threads")]
        return sorted(threads, key=lambda item: item.updated_at, reverse=True)

    def upsert_community_thread_follow(self, follow: CommunityThreadFollow) -> None:
        self._put_record("community_thread_follows", follow.follow_id, follow.model_dump(mode="json"))

    def delete_community_thread_follow(self, follow_id: str) -> None:
        self._delete_record("community_thread_follows", follow_id)

    def list_community_thread_follows(self) -> list[CommunityThreadFollow]:
        follows = [CommunityThreadFollow.model_validate(payload) for payload in self._list_records("community_thread_follows")]
        return sorted(follows, key=lambda item: item.created_at, reverse=True)

    def get_community_thread_follow(self, thread_id: str, user_id: str) -> CommunityThreadFollow | None:
        for payload in self._list_records("community_thread_follows"):
            if payload["thread_id"] == thread_id and payload["user_id"] == user_id:
                return CommunityThreadFollow.model_validate(payload)
        return None

    def insert_community_notification(self, notification: CommunityNotification) -> None:
        self._put_record("community_notifications", notification.notification_id, notification.model_dump(mode="json"))

    def list_community_notifications(self) -> list[CommunityNotification]:
        notifications = [CommunityNotification.model_validate(payload) for payload in self._list_records("community_notifications")]
        return sorted(notifications, key=lambda item: item.created_at, reverse=True)


class JsonStore(BaseStore):
    def __init__(self) -> None:
        self.initialize()

    @staticmethod
    def _empty_payload() -> dict[str, dict[str, Any]]:
        return {collection: {} for collection in COLLECTIONS}

    def initialize(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists() and LEGACY_DB_PATH.exists():
            shutil.copy2(LEGACY_DB_PATH, DB_PATH)
        if not DB_PATH.exists():
            self._write(self._empty_payload())
            return
        payload = self._read()
        for collection in COLLECTIONS:
            payload.setdefault(collection, {})
        self._write(payload)

    def _read(self) -> dict[str, dict[str, Any]]:
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

    def _write(self, payload: dict[str, dict[str, Any]]) -> None:
        DB_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _put_record(self, collection: str, key: str, payload: dict[str, Any]) -> None:
        data = self._read()
        data.setdefault(collection, {})
        data[collection][key] = payload
        self._write(data)

    def _get_record(self, collection: str, key: str) -> dict[str, Any] | None:
        data = self._read()
        return data.get(collection, {}).get(key)

    def _list_records(self, collection: str) -> list[dict[str, Any]]:
        data = self._read()
        return list(data.get(collection, {}).values())

    def _delete_record(self, collection: str, key: str) -> None:
        data = self._read()
        data.setdefault(collection, {}).pop(key, None)
        self._write(data)


class PostgresStore(BaseStore):
    def __init__(self, database_url: str) -> None:
        if not SQLALCHEMY_AVAILABLE:
            raise RuntimeError("SQLAlchemy dependencies are not installed.")
        self.engine: Engine = create_engine(database_url, future=True, pool_pre_ping=True)
        self.metadata = MetaData()
        self.records = Table(
            "leadwise_records",
            self.metadata,
            Column("collection", String(80), primary_key=True),
            Column("record_key", String(255), primary_key=True),
            Column("payload", JSON, nullable=False),
        )
        self.initialize()

    def initialize(self) -> None:
        self.metadata.create_all(self.engine)
        if BOOTSTRAP_JSON_TO_DATABASE and self._is_empty():
            bootstrap_path = DB_PATH if DB_PATH.exists() else LEGACY_DB_PATH
            if bootstrap_path.exists():
                payload = JsonStore._empty_payload()
                try:
                    raw = bootstrap_path.read_text(encoding="utf-8").strip()
                    if raw:
                        payload = json.loads(raw)
                except json.JSONDecodeError:
                    payload = JsonStore._empty_payload()
                with self.engine.begin() as conn:
                    for collection in COLLECTIONS:
                        for key, record in payload.get(collection, {}).items():
                            conn.execute(self.records.insert().values(collection=collection, record_key=key, payload=record))

    def _is_empty(self) -> bool:
        with self.engine.begin() as conn:
            first_record = conn.execute(select(self.records.c.collection).limit(1)).first()
        return first_record is None

    def _put_record(self, collection: str, key: str, payload: dict[str, Any]) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                delete(self.records).where(
                    self.records.c.collection == collection,
                    self.records.c.record_key == key,
                )
            )
            conn.execute(self.records.insert().values(collection=collection, record_key=key, payload=payload))

    def _get_record(self, collection: str, key: str) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            row = conn.execute(
                select(self.records.c.payload).where(
                    self.records.c.collection == collection,
                    self.records.c.record_key == key,
                )
            ).first()
        return row[0] if row else None

    def _list_records(self, collection: str) -> list[dict[str, Any]]:
        with self.engine.begin() as conn:
            rows = conn.execute(
                select(self.records.c.payload).where(self.records.c.collection == collection)
            ).all()
        return [row[0] for row in rows]

    def _delete_record(self, collection: str, key: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                delete(self.records).where(
                    self.records.c.collection == collection,
                    self.records.c.record_key == key,
                )
            )


def build_store() -> BaseStore:
    if DATABASE_URL:
        try:
            return PostgresStore(DATABASE_URL)
        except RuntimeError:
            pass
    return JsonStore()


store = build_store()
