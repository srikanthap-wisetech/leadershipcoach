from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class CoachingStyle(str, Enum):
    REFLECTIVE = "reflective"
    DIRECT = "direct"
    STRUCTURED = "structured"
    SUPPORTIVE = "supportive"
    CHALLENGING = "challenging"


class TipFrequency(str, Enum):
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    WEEKLY = "weekly"


class TipLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"


class DeliveryChannel(str, Enum):
    WEB = "web"
    EMAIL = "email"
    TEAMS = "teams"


class IssueTheme(str, Enum):
    FEEDBACK = "feedback"
    CONFLICT = "conflict"
    DELEGATION = "delegation"
    PERFORMANCE = "performance"
    MOTIVATION = "motivation"
    COMMUNICATION = "communication"
    PRIORITIZATION = "prioritization"
    TEAM_DEVELOPMENT = "team-development"
    OTHER = "other"


class GoalCategory(str, Enum):
    COMMUNICATION = "communication"
    DELEGATION = "delegation"
    FEEDBACK = "feedback"
    COACHING = "coaching"
    PERFORMANCE = "performance"
    TEAM_CULTURE = "team-culture"
    STRATEGIC_THINKING = "strategic-thinking"
    OTHER = "other"


class GoalStatus(str, Enum):
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    AT_RISK = "at-risk"
    COMPLETED = "completed"


class LeadershipPreference(BaseModel):
    coaching_style: CoachingStyle
    tip_frequency: TipFrequency
    tip_length: TipLength
    focus_areas: List[str] = Field(default_factory=list)
    delivery_channel: DeliveryChannel = DeliveryChannel.TEAMS


class LeaderProfileBase(BaseModel):
    role: str
    title: str
    function: str | None = None
    location: str | None = None
    team_size: int = Field(ge=0)
    indirect_team_size: int = Field(default=0, ge=0)
    years_of_leadership_experience: float = Field(ge=0)
    new_to_leadership: bool
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    preferences: LeadershipPreference


class LeaderProfileCreate(LeaderProfileBase):
    leader_id: str


class LeaderProfile(LeaderProfileBase):
    leader_id: str
    created_at: datetime
    updated_at: datetime


class CoachingIssueCreate(BaseModel):
    leader_id: str
    title: str
    description: str
    theme: IssueTheme = IssueTheme.OTHER
    urgency: str = "medium"


class CoachingIssue(CoachingIssueCreate):
    issue_id: str
    created_at: datetime


class DailyTip(BaseModel):
    tip_id: str
    leader_id: str
    headline: str
    message: str
    reason: str
    reflection_question: str
    linked_goal_id: str | None = None
    linked_issue_id: str | None = None
    created_at: datetime


class DevelopmentGoalCreate(BaseModel):
    leader_id: str
    title: str
    category: GoalCategory
    target_date: date | None = None
    success_criteria: List[str] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)


class DevelopmentGoal(DevelopmentGoalCreate):
    goal_id: str
    status: GoalStatus = GoalStatus.NOT_STARTED
    created_at: datetime
    updated_at: datetime


class GoalCheckInCreate(BaseModel):
    progress_note: str
    confidence: int = Field(ge=1, le=5)
    blockers: List[str] = Field(default_factory=list)


class GoalCheckIn(GoalCheckInCreate):
    check_in_id: str
    goal_id: str
    created_at: datetime


class AskRequest(BaseModel):
    leader_id: str
    question: str


class ContentDocument(BaseModel):
    document_id: str
    title: str
    category: str
    source_path: str
    content: str


class Citation(BaseModel):
    document_id: str
    title: str
    chunk_id: str
    url: str | None = None


class GroundedAnswer(BaseModel):
    question: str
    answer: str
    grounded: bool
    confidence: float = Field(ge=0, le=1)
    citations: List[Citation] = Field(default_factory=list)


class TeamsMessageRequest(BaseModel):
    leader_id: str
    message: str
    conversation_id: str | None = None
    channel: str = "teams"


class TeamsMessageResponse(BaseModel):
    response_type: str
    text: str
    suggested_actions: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)


class CoachingResponse(BaseModel):
    summary: str
    prompts: List[str]
    suggested_actions: List[str]
    content_references: List[Citation] = Field(default_factory=list)


class UserRole(str, Enum):
    LEADER = "leader"
    ADMINISTRATOR = "administrator"
    PEOPLE_LEADERSHIP = "people-leadership"


class PortalUser(BaseModel):
    user_id: str
    name: str
    role: UserRole
    active: bool = True


class LeadershipTopic(BaseModel):
    topic_id: str
    title: str
    summary: str
    topics: List[str]
    examples: List[str]
    case_study: str
    exercises: List[str]
    sections: List["TopicSection"] = Field(default_factory=list)
    exercise_items: List["ExerciseNoteItem"] = Field(default_factory=list)
    quiz_type: str = "knowledge-check"
    quiz_questions: List["TopicQuizQuestion"] = Field(default_factory=list)
    quiz_result_bands: List["QuizResultBand"] = Field(default_factory=list)
    course_recommendations: List["CourseRecommendation"] = Field(default_factory=list)
    book_recommendations: List["BookRecommendation"] = Field(default_factory=list)


class TopicSection(BaseModel):
    section_id: str
    title: str
    content: str


class ExerciseNoteItem(BaseModel):
    exercise_id: str
    title: str
    details: str


class QuizOption(BaseModel):
    option_id: str
    label: str
    text: str
    points: int = 0


class TopicQuizQuestion(BaseModel):
    question_id: str
    prompt: str
    options: List[QuizOption] = Field(default_factory=list)
    correct_option_id: str | None = None
    feedback: str | None = None


class QuizResultBand(BaseModel):
    min_score: int
    max_score: int
    title: str
    description: str


class BookRecommendation(BaseModel):
    book_id: str
    title: str
    author: str
    topic_fit: str
    description: str
    goodreads_url: str | None = None
    goodreads_rating: float | None = None


class CourseRecommendation(BaseModel):
    course_id: str
    title: str
    provider: str
    topic_fit: str
    description: str
    url: str


class LeaderFeedback(BaseModel):
    feedback_id: str
    user_id: str
    topic_id: str
    rating: int = Field(ge=1, le=5)
    comments: str
    created_at: datetime


class QuestionStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    ANSWERED = "answered"


class SuggestionStatus(str, Enum):
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    APPROVED = "approved"


class TopicQuestion(BaseModel):
    question_id: str
    user_id: str
    topic_id: str
    question: str
    status: QuestionStatus = QuestionStatus.OPEN
    assigned_to: str | None = None
    answer: str | None = None
    created_at: datetime
    updated_at: datetime


class TopicSuggestion(BaseModel):
    suggestion_id: str
    user_id: str
    topic_name: str
    details: str
    need_description: str
    status: SuggestionStatus = SuggestionStatus.SUBMITTED
    assigned_to: str | None = None
    approved_by: str | None = None
    approval_notes: str | None = None
    content_notes: str | None = None
    created_at: datetime


class LeaderTopicNote(BaseModel):
    note_id: str
    user_id: str
    topic_id: str
    exercise_id: str | None = None
    content: str
    updated_at: datetime


class CommunityReply(BaseModel):
    reply_id: str
    thread_id: str
    user_id: str
    content: str
    liked_by: List[str] = Field(default_factory=list)
    created_at: datetime


class CommunityThread(BaseModel):
    thread_id: str
    user_id: str
    topic_id: str | None = None
    title: str
    content: str
    liked_by: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    replies: List[CommunityReply] = Field(default_factory=list)
