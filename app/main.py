import re
from urllib.parse import urlencode

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.bot_adapter import BOT_FRAMEWORK_AVAILABLE, adapter, bot
from app.models import TeamsMessageRequest
from app.portal import portal
from app.services import teams_bot

app = FastAPI(
    title="LeadWise",
    version="1.0.0",
    description="LeadWise leadership portal with topic-first navigation, saved notes, and review workflows for administrators and people leadership.",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _bulletize(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []

    sentences = [
        _reframe_sentence(item.strip())
        for item in re.split(r"(?<=[.!?])\s+(?=[A-Z'])", text)
        if item.strip()
    ]
    if not sentences:
        return [text]

    bullets: list[str] = []
    current = ""
    style_markers = (
        "An authoritarian",
        "A democratic",
        "A laissez-faire",
        "Directing",
        "Coaching",
        "Supporting",
        "Delegating",
        "Diversity is",
        "Inclusion is",
        "Belonging is",
        "Allyship is",
    )

    for sentence in sentences:
        starts_new = (
            not current
            or sentence.startswith(style_markers)
            or sentence.startswith("For example")
            or sentence.startswith("In practice")
            or sentence.startswith("By contrast")
            or len(current) > 220
        )
        if starts_new:
            if current:
                bullets.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        bullets.append(current.strip())

    return bullets


def _reframe_summary(text: str) -> str:
    summary = text.strip()
    replacements = [
        ("This section explains", "In this topic, I explore"),
        ("This topic explains", "In this topic, I explore"),
        ("This topic breaks down", "In this topic, I break down"),
        ("This section brings together", "In this topic, I bring together"),
        ("This part of the journal focuses on", "In this topic, I focus on"),
        ("The journal describes", "In this topic, I look at"),
        ("The journal frames", "In this topic, I treat"),
        ("The final section points leaders back to", "In this topic, I connect the journal back to"),
    ]
    for old, new in replacements:
        if summary.startswith(old):
            return summary.replace(old, new, 1)
    return summary


def _reframe_sentence(text: str) -> str:
    sentence = text.strip()
    replacements = [
        ("The journal shows", "I can see"),
        ("The journal makes", "I can see that"),
        ("The journal connects", "I can see that"),
        ("The journal highlights", "I notice that"),
        ("The material connects", "I can strengthen my leadership through"),
        ("The material reinforces", "I can reinforce my leadership by"),
        ("The material adds", "I also need to pay attention to"),
        ("The content points to", "I can build this transition by focusing on"),
        ("Leaders need to", "I need to"),
        ("Strong leaders aim", "I should aim"),
        ("A strong cross-cultural leader does not assume", "I cannot assume"),
        ("Managers often focus", "As a leader, I need to move beyond"),
        ("Good feedback is", "When I give feedback, it should be"),
        ("Trust is", "Trust becomes"),
        ("Psychological safety does not mean", "Psychological safety for me does not mean"),
        ("Cross-cultural friction often comes from", "I need to remember that cross-cultural friction often comes from"),
    ]
    for old, new in replacements:
        if sentence.startswith(old):
            sentence = sentence.replace(old, new, 1)
            break
    return sentence


def _journal_url(**params: str) -> str:
    cleaned = {key: value for key, value in params.items() if value not in ("", None)}
    query = urlencode(cleaned)
    return f"/journal?{query}" if query else "/journal"


def _community_url(**params: str) -> str:
    cleaned = {key: value for key, value in params.items() if value not in ("", None)}
    query = urlencode(cleaned)
    return f"/community?{query}" if query else "/community"


def _landing_url(**params: str) -> str:
    cleaned = {key: value for key, value in params.items() if value not in ("", None)}
    query = urlencode(cleaned)
    return f"/?{query}" if query else "/"


def _actions_url(**params: str) -> str:
    cleaned = {key: value for key, value in params.items() if value not in ("", None)}
    query = urlencode(cleaned)
    return f"/actions?{query}" if query else "/actions"


def _my_activity_url(**params: str) -> str:
    cleaned = {key: value for key, value in params.items() if value not in ("", None)}
    query = urlencode(cleaned)
    return f"/my-activity?{query}" if query else "/my-activity"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def landing_home(request: Request, theme: str | None = None):
    current_user = portal.leader_user()
    topics = portal.accessible_topics_for_user(current_user.user_id)
    threads = portal.list_community_threads()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "current_user": current_user,
            "topic_count": len(topics),
            "thread_count": len(threads),
            "available_topics": topics,
            "theme": theme or "sunrise",
            "theme_options": [
                ("sunrise", "Slate"),
                ("harbor", "Teal"),
                ("sage", "Stone"),
            ],
        },
    )


@app.get("/actions")
def actions_home(request: Request, theme: str | None = None):
    current_user = portal.leader_user()
    topics = portal.accessible_topics_for_user(current_user.user_id)
    return templates.TemplateResponse(
        request,
        "actions.html",
        {
            "current_user": current_user,
            "available_topics": topics,
            "theme": theme or "sunrise",
            "theme_options": [
                ("sunrise", "Slate"),
                ("harbor", "Teal"),
                ("sage", "Stone"),
            ],
        },
    )


@app.get("/journal")
def journal_home(
    request: Request,
    topic_id: str | None = None,
    theme: str | None = None,
    search: str | None = None,
):
    current_user = portal.leader_user()
    search_query = (search or "").strip()
    available_topics = portal.search_topics_for_user(current_user.user_id, search_query)
    selected_topic = portal.get_topic(topic_id)
    if available_topics:
        selected_topic = next((topic for topic in available_topics if topic.topic_id == selected_topic.topic_id), available_topics[0])
    topic_note = portal.get_note(current_user.user_id, selected_topic.topic_id)
    case_study_note = portal.get_note(current_user.user_id, selected_topic.topic_id, "case-study")
    topic_rating_summary = portal.topic_rating_summary(selected_topic.topic_id)
    exercise_notes = {
        item.exercise_id: portal.get_note(current_user.user_id, selected_topic.topic_id, item.exercise_id)
        for item in selected_topic.exercise_items
    }
    section_points = {
        section.section_id: _bulletize(section.content)
        for section in selected_topic.sections
    }
    case_study_points = _bulletize(selected_topic.case_study)
    exercise_points = {
        item.exercise_id: _bulletize(item.details)
        for item in selected_topic.exercise_items
    }

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "current_user": current_user,
            "selected_topic": selected_topic,
            "summary_text": _reframe_summary(selected_topic.summary),
            "available_topics": available_topics,
            "search_query": search_query,
            "topic_note": topic_note,
            "case_study_note": case_study_note,
            "topic_rating_summary": topic_rating_summary,
            "exercise_notes": exercise_notes,
            "section_points": section_points,
            "case_study_points": case_study_points,
            "exercise_points": exercise_points,
            "theme": theme or "sunrise",
            "theme_options": [
                ("sunrise", "Slate"),
                ("harbor", "Teal"),
                ("sage", "Stone"),
            ],
        },
    )


@app.get("/community")
def community_home(request: Request, theme: str | None = None, topic_id: str | None = None):
    current_user = portal.leader_user()
    search = request.query_params.get("search", "")
    search_query = search.strip()
    leader_members = portal.list_leader_community_members()
    available_topics = portal.accessible_topics_for_user(current_user.user_id)
    selected_topic = next((topic for topic in available_topics if topic.topic_id == topic_id), None)
    all_threads = portal.list_community_threads()
    threads = portal.search_community_threads(search_query, topic_id=selected_topic.topic_id if selected_topic else None)
    return templates.TemplateResponse(
        request,
        "community.html",
        {
            "current_user": current_user,
            "threads": threads,
            "available_topics": available_topics,
            "leader_members": leader_members,
            "user_lookup": {user.user_id: user for user in leader_members},
            "topic_lookup": {topic.topic_id: topic for topic in available_topics},
            "followed_thread_ids": portal.followed_thread_ids_for_user(current_user.user_id),
            "thread_follow_counts": {thread.thread_id: portal.follower_count(thread.thread_id) for thread in all_threads},
            "notification_count": len(portal.list_notifications_for_user(current_user.user_id)),
            "selected_topic_id": selected_topic.topic_id if selected_topic else "",
            "search_query": search_query,
            "theme": theme or "sunrise",
            "theme_options": [
                ("sunrise", "Slate"),
                ("harbor", "Teal"),
                ("sage", "Stone"),
            ],
        },
    )


@app.get("/my-activity")
def my_activity_home(request: Request, theme: str | None = None):
    current_user = portal.leader_user()
    dashboard = portal.user_activity_dashboard(current_user.user_id)
    topics = portal.accessible_topics_for_user(current_user.user_id)
    return templates.TemplateResponse(
        request,
        "my_activity.html",
        {
            "current_user": current_user,
            "available_topics": topics,
            "theme": theme or "sunrise",
            "theme_options": [
                ("sunrise", "Slate"),
                ("harbor", "Teal"),
                ("sage", "Stone"),
            ],
            **dashboard,
        },
    )


@app.get("/admin")
def admin_home(request: Request):
    current_user = portal.administrator_user()
    available_topics = portal.list_topics()
    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "current_user": current_user,
            "available_topics": available_topics,
            "all_users": portal.list_users(),
            "feedback_items": portal.list_feedback(),
            "topic_suggestions": portal.list_topic_suggestions(),
            "questions": portal.list_questions(),
        },
    )


@app.get("/people-leadership")
def people_leadership_home(request: Request):
    current_user = portal.people_leadership_user()
    return templates.TemplateResponse(
        request,
        "people_leadership.html",
        {
            "current_user": current_user,
            "questions": portal.list_questions(),
            "topic_suggestions": portal.list_topic_suggestions_for_assignee(current_user.user_id),
        },
    )


@app.post("/web/feedback")
def submit_feedback(
    user_id: str = Form("leader-alex"),
    topic_id: str = Form(...),
    theme: str = Form("sunrise"),
    source: str = Form("journal"),
    rating: int = Form(...),
    comments: str = Form(""),
):
    portal.add_feedback(user_id=user_id, topic_id=topic_id, rating=rating, comments=comments)
    redirect_url = (
        _community_url(theme=theme, topic_id=topic_id)
        if source == "community"
        else _my_activity_url(theme=theme)
        if source == "activity"
        else _actions_url(theme=theme)
        if source == "actions"
        else _landing_url(theme=theme)
        if source == "home"
        else _journal_url(topic_id=topic_id, theme=theme)
    )
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/web/questions")
def submit_question(
    user_id: str = Form("leader-alex"),
    topic_id: str = Form(...),
    theme: str = Form("sunrise"),
    source: str = Form("journal"),
    question: str = Form(...),
):
    portal.submit_question(user_id=user_id, topic_id=topic_id, question=question)
    redirect_url = (
        _community_url(theme=theme, topic_id=topic_id)
        if source == "community"
        else _my_activity_url(theme=theme)
        if source == "activity"
        else _actions_url(theme=theme)
        if source == "actions"
        else _landing_url(theme=theme)
        if source == "home"
        else _journal_url(topic_id=topic_id, theme=theme)
    )
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/web/topic-suggestions")
def submit_topic_suggestion(
    user_id: str = Form("leader-alex"),
    topic_id: str = Form(""),
    theme: str = Form("sunrise"),
    source: str = Form("journal"),
    topic_name: str = Form(...),
    details: str = Form(...),
    need_description: str = Form(...),
):
    portal.submit_topic_suggestion(
        user_id=user_id,
        topic_name=topic_name,
        details=details,
        need_description=need_description,
    )
    redirect_url = (
        _community_url(theme=theme, topic_id=topic_id)
        if source == "community"
        else _my_activity_url(theme=theme)
        if source == "activity"
        else _actions_url(theme=theme)
        if source == "actions"
        else _landing_url(theme=theme)
        if source == "home"
        else _journal_url(topic_id=topic_id, theme=theme)
    )
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/web/community-thread")
def create_community_thread(
    title: str = Form(...),
    content: str = Form(...),
    topic_id: str = Form(""),
    theme: str = Form("sunrise"),
):
    portal.create_community_thread(
        user_id="leader-alex",
        title=title,
        content=content,
        topic_id=topic_id or None,
    )
    filter_topic = topic_id or ""
    query = urlencode({key: value for key, value in {"theme": theme, "topic_id": filter_topic}.items() if value})
    return RedirectResponse(url=f"/community?{query}" if query else "/community", status_code=303)


@app.post("/web/community-reply")
def add_community_reply(
    thread_id: str = Form(...),
    content: str = Form(...),
    theme: str = Form("sunrise"),
    topic_id: str = Form(""),
):
    portal.add_community_reply(thread_id=thread_id, user_id="leader-alex", content=content)
    query = urlencode({key: value for key, value in {"theme": theme, "topic_id": topic_id}.items() if value})
    return RedirectResponse(url=f"/community?{query}" if query else "/community", status_code=303)


@app.post("/web/community-follow")
def toggle_community_follow(
    thread_id: str = Form(...),
    theme: str = Form("sunrise"),
    topic_id: str = Form(""),
):
    portal.toggle_thread_follow(thread_id=thread_id, user_id="leader-alex")
    query = urlencode({key: value for key, value in {"theme": theme, "topic_id": topic_id}.items() if value})
    return RedirectResponse(url=f"/community?{query}" if query else "/community", status_code=303)


@app.post("/web/community-like")
def toggle_community_like(
    thread_id: str = Form(...),
    reply_id: str = Form(""),
    theme: str = Form("sunrise"),
    topic_id: str = Form(""),
):
    if reply_id:
        portal.toggle_reply_like(thread_id=thread_id, reply_id=reply_id, user_id="leader-alex")
    else:
        portal.toggle_thread_like(thread_id=thread_id, user_id="leader-alex")
    query = urlencode({key: value for key, value in {"theme": theme, "topic_id": topic_id}.items() if value})
    return RedirectResponse(url=f"/community?{query}" if query else "/community", status_code=303)


@app.post("/web/access")
def grant_access(
    admin_user_id: str = Form("admin-sam"),
    leader_user_id: str = Form(...),
    topic_id: str = Form(...),
):
    portal.grant_access(user_id=leader_user_id, topic_id=topic_id)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/web/assign")
def assign_question(
    admin_user_id: str = Form("admin-sam"),
    question_id: str = Form(...),
    assignee_id: str = Form(...),
):
    portal.assign_question(question_id=question_id, assignee_id=assignee_id)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/web/assign-topic-suggestion")
def assign_topic_suggestion(
    admin_user_id: str = Form("admin-sam"),
    suggestion_id: str = Form(...),
    assignee_id: str = Form(...),
):
    portal.assign_topic_suggestion(suggestion_id=suggestion_id, assignee_id=assignee_id)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/web/answer")
def answer_question(
    team_user_id: str = Form("pl-jordan"),
    question_id: str = Form(...),
    answer: str = Form(...),
):
    portal.answer_question(question_id=question_id, answer=answer)
    return RedirectResponse(url="/people-leadership", status_code=303)


@app.post("/web/approve-topic-suggestion")
def approve_topic_suggestion(
    team_user_id: str = Form("pl-jordan"),
    suggestion_id: str = Form(...),
    approval_notes: str = Form(""),
    content_notes: str = Form(""),
):
    portal.approve_topic_suggestion(
        suggestion_id=suggestion_id,
        approver_id=team_user_id,
        approval_notes=approval_notes,
        content_notes=content_notes,
    )
    return RedirectResponse(url="/people-leadership", status_code=303)


@app.post("/web/topic-suggestion-content")
def update_topic_suggestion_content(
    admin_user_id: str = Form("admin-sam"),
    suggestion_id: str = Form(...),
    content_notes: str = Form(""),
):
    portal.update_topic_suggestion_content(suggestion_id=suggestion_id, content_notes=content_notes)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/web/topic-note")
def save_topic_note(
    topic_id: str = Form(...),
    theme: str = Form("sunrise"),
    content: str = Form(""),
):
    portal.save_note(user_id="leader-alex", topic_id=topic_id, content=content)
    return RedirectResponse(url=_journal_url(topic_id=topic_id, theme=theme), status_code=303)


@app.post("/web/exercise-note")
def save_exercise_note(
    topic_id: str = Form(...),
    exercise_id: str = Form(...),
    theme: str = Form("sunrise"),
    content: str = Form(""),
):
    portal.save_note(user_id="leader-alex", topic_id=topic_id, content=content, exercise_id=exercise_id)
    return RedirectResponse(url=_journal_url(topic_id=topic_id, theme=theme), status_code=303)


@app.post("/web/case-study-note")
def save_case_study_note(
    topic_id: str = Form(...),
    theme: str = Form("sunrise"),
    content: str = Form(""),
):
    portal.save_note(user_id="leader-alex", topic_id=topic_id, content=content, exercise_id="case-study")
    return RedirectResponse(url=_journal_url(topic_id=topic_id, theme=theme), status_code=303)


@app.post("/teams/messages")
def handle_teams_message(payload: TeamsMessageRequest):
    return teams_bot.handle_message(payload)


@app.post("/api/messages")
async def bot_messages(request: Request):
    if not BOT_FRAMEWORK_AVAILABLE or adapter is None or bot is None:
        raise HTTPException(
            status_code=503,
            detail="Bot Framework dependencies are not installed. Install requirements.txt to enable the Teams adapter.",
        )

    from botbuilder.schema import Activity

    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    invoke_response = await adapter.process_activity(auth_header, activity, bot.on_turn)
    if invoke_response:
        body = invoke_response.body if invoke_response.body is not None else {}
        return JSONResponse(status_code=invoke_response.status, content=body)

    return Response(status_code=201)
