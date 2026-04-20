from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote_plus
from uuid import uuid4

from app.models import (
    BookRecommendation,
    CommunityNotification,
    CommunityReply,
    CommunityThreadFollow,
    CommunityThread,
    CourseRecommendation,
    LeaderFeedback,
    LeaderTopicNote,
    LeadershipTopic,
    PortalUser,
    QuizOption,
    QuizResultBand,
    QuestionStatus,
    SuggestionStatus,
    TopicSection,
    TopicSuggestion,
    TopicQuizQuestion,
    TopicQuestion,
    UserRole,
    ExerciseNoteItem,
)
from app.storage import store


def utc_now() -> datetime:
    return datetime.now(UTC)


def _quiz_question(
    question_id: str,
    prompt: str,
    answers: list[tuple[str, str, int]],
    *,
    correct_option_id: str | None = None,
    feedback: str | None = None,
) -> TopicQuizQuestion:
    return TopicQuizQuestion(
        question_id=question_id,
        prompt=prompt,
        options=[
            QuizOption(option_id=option_id, label=option_id.upper(), text=text, points=points)
            for option_id, text, points in answers
        ],
        correct_option_id=correct_option_id,
        feedback=feedback,
    )


def _book(
    book_id: str,
    title: str,
    author: str,
    topic_fit: str,
    description: str,
) -> BookRecommendation:
    return BookRecommendation(
        book_id=book_id,
        title=title,
        author=author,
        topic_fit=topic_fit,
        description=description,
        goodreads_url=f"https://www.goodreads.com/search?q={quote_plus(title)}",
        goodreads_rating={
            "Start With Why": 4.1,
            "Leaders Eat Last": 4.0,
            "The Coaching Habit": 4.2,
            "Turn the Ship Around": 4.1,
            "The Making of a Manager": 4.3,
            "It’s Your Ship": 4.1,
            "Radical Candor": 4.1,
            "Bringing Out the Best in People": 4.0,
            "Emotional Intelligence": 4.2,
            "Working with Emotional Intelligence": 4.1,
            "Emotional": 4.0,
            "The Tipping Point": 3.9,
            "Give and Take": 4.1,
            "The Power of Vulnerability": 4.3,
            "Managing Up": 4.0,
            "Team of Teams": 4.1,
            "Scaling People": 4.4,
            "The Leadership Pipeline": 4.0,
            "An Elegant Puzzle": 4.2,
            "The Hard Thing About Hard Things": 4.2,
            "Build": 4.3,
        }.get(title, 4.0),
    )


def _course(
    course_id: str,
    title: str,
    provider: str,
    topic_fit: str,
    description: str,
    url: str,
) -> CourseRecommendation:
    return CourseRecommendation(
        course_id=course_id,
        title=title,
        provider=provider,
        topic_fit=topic_fit,
        description=description,
        url=url,
    )


class LeadershipBasicsPortal:
    def __init__(self) -> None:
        self._topics = [
            LeadershipTopic(
                topic_id="wisetech-leadership-foundations",
                title="WiseTech Leadership Foundations",
                summary="The journal opens with WiseTech's leadership mantra: lead others, manage yourself. This section frames leadership as a daily practice of self-management, visible role modelling, honest communication, trust-building, and active support for team growth.",
                topics=[
                    "What it means to lead others while first managing your own behaviour, standards, and energy.",
                    "How people leaders at WiseTech are expected to role model the behaviours they want to see in their teams.",
                    "Why trust, open communication, and good judgement matter more than positional authority.",
                    "How to turn mistakes and setbacks into development opportunities instead of blame cycles.",
                ],
                examples=[
                    "A people leader notices tension rising in a delivery discussion and chooses calm, direct communication rather than frustration. The team sees the standard for how pressure is handled.",
                    "A leader uses a one-on-one not only to review delivery but also to ask about the team member's development goals, strengths, and next stretch opportunities.",
                    "A manager openly reflects on a poor decision, explains what they learned, and shows the team that accountability includes self-correction.",
                ],
                case_study="Nina has just become a people leader after years of being a high-performing individual contributor. In her first month, she realizes the team is watching her reactions more closely than her instructions. When deadlines slip, she sees two options: blame the team and tighten control, or demonstrate the culture she wants to build. She chooses to stay composed, clarify expectations, acknowledge where she could have been clearer, and ask the team what support they need. Over time, the team starts mirroring that same openness and accountability. Nina learns that leadership at WiseTech is not just about directing work. It is about modelling the behaviour, judgement, and learning mindset others can follow.",
                exercises=[
                    "Write down three behaviours you want your team to consistently experience from you in high-pressure moments.",
                    "Identify one recent setback and rewrite it as a learning discussion you could have with the team.",
                    "List one self-management habit you need to strengthen so your leadership feels more consistent.",
                ],
            ),
            LeadershipTopic(
                topic_id="leadership-styles",
                title="Leadership Styles",
                summary="This section explains the main leadership styles a leader is likely to use in practice, how each style affects the team, and why strong leaders adapt their style to the situation rather than relying on one default approach.",
                topics=[
                    "How your instinctive decision-making style affects the team around you.",
                    "What your preferred style looks like in conflict, team meetings, and moments of uncertainty.",
                    "How leadership style influences delegation, collaboration, and accountability.",
                    "Why a style that works in one situation may limit you in another.",
                ],
                examples=[
                    "A leader who prefers fast control may drive clarity in a crisis but may also unintentionally shut down useful input from the team.",
                    "A leader who values collaboration may create stronger buy-in, but if they over-consult on urgent decisions the team can experience drift.",
                    "A hands-off leader may empower capable people well, but if expectations are vague the team can experience confusion rather than ownership.",
                ],
                case_study="Arjun leads a capable engineering team and prides himself on being decisive. In delivery meetings, he often jumps quickly to solutions, sets aggressive targets, and expects people to follow through. Results are strong, but over time the team becomes quieter and less likely to challenge assumptions. After using the self-assessment, Arjun realizes that his default style creates speed but reduces shared ownership. He experiments with asking for input before locking a decision, especially in planning discussions. The result is not weaker leadership. The result is broader judgement and stronger commitment from the team.",
                exercises=[
                    "Complete the self-assessment and note which style you default to most often.",
                    "Write one strength, one blind spot, and one workplace situation where your current style may not serve you well.",
                    "Choose one upcoming meeting where you will deliberately adapt your style to fit the need of the room.",
                ],
            ),
            LeadershipTopic(
                topic_id="delegation",
                title="Delegation",
                summary="This topic explores delegation as a leadership capability that creates scale, ownership, growth, and better judgement. It focuses on how to decide what to delegate, how to delegate clearly, and how to build trust and accountability without slipping into micromanagement or abandonment.",
                topics=[
                    "Why delegation matters for leadership scale, team growth, and better use of time.",
                    "How to decide what to delegate, to whom, and at what level of autonomy.",
                    "How to set expectations clearly enough that ownership grows instead of confusion.",
                    "How to support, monitor, and coach without taking the work back too early.",
                ],
                examples=[
                    "A leader stops holding onto every customer update and instead delegates ownership of a weekly stakeholder note to a team member who wants more visibility.",
                    "A manager breaks a complex project into smaller workstreams and assigns them not only by capability, but also by each person’s learning goals and interests.",
                    "A technical leader resists rewriting a solution themselves and instead coaches the team through checkpoints so capability grows inside the team, not just in the leader.",
                ],
                case_study="Sana leads a high-performing product and engineering squad, but she is overwhelmed because too much still flows through her. She reviews key documents, joins almost every problem-solving discussion, and steps back into hands-on work whenever delivery pressure rises. The team respects her, but they have also learned to wait for her direction. After reflecting on delegation, Sana realizes she is protecting quality in the short term while limiting ownership in the long term. She starts by listing the work that only she can do versus the work that could be delegated with the right context and support. She then chooses one capable team member who wants more stretch, agrees the outcome, defines what good looks like, sets checkpoints, and stays available without taking the work back. The first attempt is not identical to how Sana would have done it, but it is strong enough, and the team member grows significantly. Over time, Sana notices a deeper change: the team becomes more proactive, she spends more time on bigger leadership decisions, and delegation starts feeling less like loss of control and more like building a stronger team.",
                exercises=[
                    "Write down three responsibilities you are still holding that someone else could own with the right support.",
                    "Choose one upcoming task and match it to a team member based on both capability and development opportunity.",
                    "Before you delegate, define the outcome, success measures, decision boundaries, and check-in points in writing.",
                ],
            ),
            LeadershipTopic(
                topic_id="building-trust",
                title="Building Trust",
                summary="Trust is presented as a non-negotiable leadership foundation. This topic breaks down how trust is built, how it is damaged, and what leaders can do in daily work to create confidence, openness, and credibility.",
                topics=[
                    "Why trust allows teams to collaborate well and take sensible risks.",
                    "How trust is created through reliable everyday actions, not just major gestures.",
                    "What leaders need to do to maintain trust after mistakes, tension, or change.",
                    "How communication, accountability, and feedback help protect trust over time.",
                ],
                examples=[
                    "A leader shares context openly during organizational change instead of withholding information until people become anxious and speculative.",
                    "A manager follows through on a promised action from a one-on-one, reinforcing that team members can rely on what they hear.",
                    "Peer recognition is built into team meetings so contribution and effort are visibly noticed, not left to chance.",
                ],
                case_study="Maya leads a team that delivers consistently, but people rarely challenge ideas or admit blockers early. After a few missed commitments, Maya realizes the problem is not capability but trust. Team members are not sure whether transparency will be met with support or judgement. Maya begins changing the pattern in visible ways: she shares more context, follows through on commitments faster, invites dissent in meetings, and responds constructively when people raise concerns. She also creates moments for peer recognition and collaborative problem-solving. Over time, the team becomes more open, escalations happen earlier, and discussions get more honest. Trust was not fixed by one speech. It was rebuilt through repeated, predictable leader behaviour.",
                exercises=[
                    "Run a recognition moment in your next meeting and notice how it changes the tone of the discussion.",
                    "Reflect on one habit of yours that could erode trust if repeated under pressure.",
                    "Identify one trust-building action you can repeat consistently so it becomes visible and expected.",
                ],
            ),
            LeadershipTopic(
                topic_id="empathy-and-emotional-intelligence",
                title="Empathy and Emotional Intelligence",
                summary="The journal treats empathy and emotional intelligence as practical leadership capabilities, not soft extras. This topic explains what those capabilities are, how they show up at work, and how leaders can use them to improve judgement, conversations, and team relationships.",
                topics=[
                    "Why empathy improves trust, motivation, and psychological connection within teams.",
                    "How emotional intelligence supports better judgement, healthier conflict, and stronger relationships.",
                    "What active listening, self-awareness, and self-regulation look like in leadership practice.",
                    "How to respond constructively in emotionally charged or high-pressure situations.",
                ],
                examples=[
                    "A leader pauses a difficult conversation to check understanding rather than pushing harder when someone becomes defensive.",
                    "A manager journals emotional triggers after a tense meeting and notices recurring patterns in how they react under stress.",
                    "A team member feels heard because the leader listens for meaning and emotion, not just facts and action items.",
                ],
                case_study="Daniel is respected for being calm and analytical, but his team often leaves hard conversations feeling unseen. In retrospectives, people describe him as fair but distant. Daniel starts to realize that solving the problem quickly is not the same as connecting with the people experiencing it. He begins using more open-ended questions, summarizing what he hears before offering solutions, and reflecting on how his own stress changes his tone. Over time, the team becomes more candid and discussions get less defensive. Daniel still values logic, but now he uses empathy and emotional self-awareness to make that logic more human and more effective.",
                exercises=[
                    "Use active listening in one important conversation and record what changed when you focused fully on the other person's perspective.",
                    "Write about a recent high-pressure moment and identify the emotion beneath your visible behaviour.",
                    "Practice one small pause before reacting in tense situations and reflect on the effect.",
                ],
            ),
            LeadershipTopic(
                topic_id="psychological-safety-diversity-allyship",
                title="Psychological Safety, Diversity, Inclusion, Belonging and Allyship",
                summary="This topic treats psychological safety, diversity, inclusion, belonging, and allyship as connected but distinct leadership responsibilities. It breaks the topic into practical subtopics so I can understand what each concept means, how they differ, and what leadership behaviour makes them real for a team.",
                topics=[
                    "How psychological safety helps people speak up, admit mistakes, ask for help, and challenge ideas without fear.",
                    "What diversity, inclusion, and belonging each mean in practice, and why they should not be treated as the same thing.",
                    "What allyship looks like in everyday decisions, meetings, sponsorship, hiring, and recognition.",
                    "How team norms, fairness, feedback, and representation shape whether people feel safe and included over time.",
                ],
                examples=[
                    "A leader notices that the same confident voices dominate every planning discussion, so they start using round-robin input and pre-reads to make space for broader contribution.",
                    "A manager thanks someone for raising a delivery risk early, even though it creates short-term discomfort, showing that honesty is safer than silence.",
                    "A leader interrupts biased language in a meeting, recentres the discussion, and makes sure the affected person does not have to carry the correction alone.",
                ],
                case_study="Sofia manages a diverse team with strong technical depth, yet she notices the same few people dominate discussions while others hesitate to contribute. Some newer team members privately describe the environment as polite but not fully safe. Sofia starts by separating the problem into parts. She looks at psychological safety in meetings, inclusion in decision-making, belonging in how contribution is recognized, and allyship in how leaders respond when bias shows up. She introduces more structured input, thanks people who raise concerns early, invites feedback on team dynamics, and steps in when assumptions marginalize someone’s perspective. She also changes recognition so different forms of contribution are seen, not just the loudest voices or fastest responders. Over time, participation broadens, challenge becomes more constructive, and the team starts to feel more inclusive in practice instead of only in principle.",
                exercises=[
                    "Identify one barrier to psychological safety on your team and one concrete change you can make in meetings or decision-making this month.",
                    "Write one allyship commitment you can make visible in sponsorship, recognition, feedback, or hiring conversations.",
                    "Review who tends to speak most, who tends to hold back, and what that may be telling you about inclusion and belonging on the team.",
                ],
            ),
            LeadershipTopic(
                topic_id="cross-cultural-leadership",
                title="Leading Cross-Cultural Teams and Communicating Across Cultures",
                summary="This topic breaks cross-cultural leadership into practical subtopics so I can understand how culture shapes communication, trust, decision-making, conflict, and collaboration. It focuses on how to lead fairly across differences without reducing culture to stereotypes or losing clarity.",
                topics=[
                    "How culture shapes communication norms, expectations, and what people interpret as respectful, clear, or credible leadership.",
                    "How to adapt meetings, written communication, and decision-making across different cultural preferences.",
                    "Why conflict, silence, disagreement, and commitment can be read very differently across teams.",
                    "How to build shared team habits that reduce misinterpretation and make collaboration more inclusive.",
                ],
                examples=[
                    "A leader shares pre-reads before a planning meeting because some team members think best after reflection, while others are comfortable responding live and immediately.",
                    "A manager notices silence after asking for reactions and stops assuming agreement. Instead, they invite written follow-up and ask specific people for their view after the meeting.",
                    "A distributed team creates a simple set of shared meeting norms around decision clarity, response time, challenge style, and documentation so fewer assumptions are left unspoken.",
                ],
                case_study="Scenario one: Ravi leads a geographically distributed team across multiple cultures. In one region, direct disagreement is common and seen as productive. In another, people prefer more context and indirectness before they challenge something openly. Ravi initially interprets silence as agreement and directness as impatience, which causes tension. After reflection, he starts sending context in advance, invites written responses, and checks for understanding before treating silence as alignment. Scenario two: Mei runs a cross-functional meeting where one group wants quick decisions and another wants broader consultation before committing. Instead of framing one side as slow and the other as reckless, she surfaces the difference openly and agrees a clearer decision pattern for the team. Scenario three: Carlos notices that feedback lands unevenly across a global team. He shifts from one communication style to a more explicit approach, giving more context, checking interpretation, and clarifying expectations so the same message is less likely to be misread.",
                exercises=[
                    "Run a cultural awareness discussion or culture map exercise in your next team conversation and capture what changed in how people understood one another.",
                    "Choose one important message and rewrite it for a cross-cultural audience with less assumed context, clearer language, and more explicit next steps.",
                    "Identify one communication habit of yours that works well locally but may travel poorly across cultures, then test a more inclusive alternative.",
                ],
            ),
            LeadershipTopic(
                topic_id="transition-to-leadership",
                title="Moving from Individual Contributor to Leadership",
                summary="The journal describes the move from individual contributor to leader as a deep role shift. This topic explains what changes in the role, where new managers often struggle, and how to build the habits that make the transition successful.",
                topics=[
                    "How leadership changes your core job from personal delivery to enabling team delivery.",
                    "Why communication becomes a central part of the role.",
                    "How delegation, team building, and time management support the transition.",
                    "What it means to lead while balancing your own work and management responsibilities.",
                ],
                examples=[
                    "A new manager role-plays a difficult conversation before having it live, building confidence and clarity.",
                    "A leader delegates a recurring planning task and resists the urge to reclaim it when it is done differently from how they would do it.",
                    "Time-blocking is used to protect one-on-ones, team planning, and thinking time instead of reacting to everything as it arrives.",
                ],
                case_study="Leah was known as one of the strongest individual contributors in her area, so promotion felt like a natural next step. But once she became a manager, she kept stepping into detailed work, solving problems herself, and measuring success by her own output. Her calendar filled up, her team became dependent, and she felt constantly behind. Through reflection and practice, Leah begins to understand that her job is now to create clarity, remove blockers, grow others, and make sure the team performs sustainably. Delegation and communication stop feeling like secondary work. They become the real work of leadership.",
                exercises=[
                    "Write down which parts of your old individual contributor identity you need to let go of to lead well.",
                    "Choose one recurring task to delegate with clear support, boundaries, and follow-up.",
                    "Review your calendar and identify whether your time allocation reflects a leader's job or an individual contributor's habits.",
                ],
            ),
            LeadershipTopic(
                topic_id="giving-and-receiving-feedback",
                title="Giving and Receiving Feedback",
                summary="The journal frames feedback as one of the main engines of growth. This topic explains how to give feedback, how to receive it well, and how to handle difficult conversations without becoming vague, avoidant, or overly aggressive.",
                topics=[
                    "Why feedback matters for performance, development, and team culture.",
                    "How to give feedback that is specific, timely, and constructive.",
                    "How to receive feedback without defensiveness and turn it into improvement.",
                    "What barriers make feedback difficult and how leaders can reduce them.",
                ],
                examples=[
                    "A feedback survey creates data for a team conversation about where performance and collaboration can improve.",
                    "A feedback journal helps a leader turn input into visible change rather than vague intention.",
                    "A recurring feedback challenge helps normalize constructive feedback instead of waiting for formal review cycles.",
                ],
                case_study="Marcus wants to be supportive, so he regularly softens or postpones difficult feedback. Over time, a high-potential team member keeps repeating the same behaviour because the real message never lands. Marcus learns that avoiding discomfort is not kindness if it blocks someone's growth. He starts using specific examples, explains impact clearly, and works with the team member on a concrete improvement plan. He also becomes more intentional about how he receives feedback from others. The result is not harsher leadership. It is more honest, useful, and developmental leadership.",
                exercises=[
                    "Draft a feedback conversation using a concrete example, clear impact, and a next step.",
                    "Reflect on the last piece of feedback you received and what you actually changed because of it.",
                    "Identify one feedback conversation you have been delaying and write the opener you will use.",
                ],
            ),
        ]
        self._enrich_topics()
        self._seed_defaults()

    def _enrich_topics(self) -> None:
        topic_map = {
            "wisetech-leadership-foundations": {
                "sections": [
                    (
                        "lead-yourself",
                        "Lead Yourself First",
                        "Effective leadership starts with leading yourself. That means being grounded in purpose, vision, and values so your leadership choices are not random or reactive. In practical work terms, leaders who know what they stand for create more consistency for their teams, especially when change, ambiguity, or pressure increase. A leader who has done this inner work is less likely to swing between being overly controlling in one moment and too hands-off in the next. For example, when a release slips, a self-managed leader can acknowledge the issue calmly, separate facts from emotion, and guide the team forward instead of letting frustration set the tone.",
                    ),
                    (
                        "lead-others",
                        "Lead Others Through Trust, Communication, and Motivation",
                        "The material connects strong leadership with three repeatable behaviours: building trust and confidence, communicating transparently, and motivating others. This is especially relevant in a workforce that is more global, diverse, virtual, and multigenerational than before. Leaders need to adapt how they build relationships and how they communicate change. In real work, that may mean explaining not just what decision was made but why, what tradeoffs were considered, and what support is available. A team generally handles difficult news better when the leader shares context early and honestly rather than waiting until rumours fill the gap.",
                    ),
                    (
                        "leadership-competencies",
                        "Critical Leadership Competencies",
                        "The course notes call out competencies such as strategy, results orientation, leading a diverse workforce, communication, trust and integrity, and self-development. These are not separate boxes to tick. Together they describe what modern leadership capability looks like in practice. A leader may be strong at driving results but weaker at developing others, or excellent at relationship building but less disciplined with follow-through. The goal is not perfection in every area on day one. The goal is to understand which capabilities are already strengths and which ones need deliberate development.",
                    ),
                ],
                "exercise_items": [
                    (
                        "foundation-note-1",
                        "Personal leadership baseline",
                        "Write down your purpose, the leadership values you want to be known for, and one behaviour your team should consistently experience from you.",
                    ),
                    (
                        "foundation-note-2",
                        "Team trust reflection",
                        "Capture one place where your team may need more clarity, confidence, or open communication from you.",
                    ),
                ],
            },
            "leadership-styles": {
                "sections": [
                    (
                        "style-self-assessment",
                        "Understanding Your Default Style",
                        "The journal self-assessment points to a core idea: leadership style should be situational. A leader needs to know their natural pattern first before they can adapt it consciously. Some people default to directing quickly, some to consultation, and others to stepping back. That default usually becomes most visible under pressure, when time is short and the leader falls back on instinct rather than choice. Understanding your natural pattern helps you spot where it is helping and where it may be limiting the team.",
                    ),
                    (
                        "style-classic-types",
                        "Classic Leadership Styles and What They Look Like",
                        "Three classic styles are especially helpful as a starting point. An authoritarian or directive style is leader-led: the manager sets direction, makes decisions quickly, and expects clear execution. This can work well in a crisis, such as a production incident where the team needs immediate coordination, but overused it can make people passive or hesitant to challenge bad assumptions. A democratic or participative style invites input before decisions are made. This often works well in planning, problem-solving, and change discussions because people feel heard and buy in more strongly. The risk is that a leader can over-consult and slow the team down when decisive action is needed. A laissez-faire or hands-off style gives people wide autonomy and minimal interference. This can be effective with highly capable specialists who know the work deeply, but if goals, boundaries, and accountability are vague it can feel less like empowerment and more like abandonment.",
                    ),
                    (
                        "style-situational",
                        "Using the Right Style at the Right Time",
                        "The material also references situational leadership styles like directing, coaching, supporting, and delegating. Directing works best when someone is new to a task and needs clear instruction. Coaching is useful when a team member has some capability but still needs guidance, feedback, and encouragement. Supporting works when the person can do the work but may need confidence, alignment, or help thinking through tradeoffs. Delegating works best when the team member is both capable and trusted to run with ownership. For example, a newly promoted analyst learning stakeholder management may need a coaching style, while a seasoned team lead running a well-understood process may benefit more from delegation and light-touch check-ins.",
                    ),
                    (
                        "style-risks",
                        "Style Risks and Practical Signals",
                        "Each style has a shadow side. If you are too directive, your team may wait for answers instead of thinking for themselves. If you are too collaborative, people may leave meetings feeling heard but unclear on the decision. If you are too hands-off, high performers may thrive while others drift quietly. Practical signals help here. If people stop challenging you, you may be too dominant. If decisions keep reopening, you may be under-directing. If work quality varies wildly, your delegation may lack enough clarity or follow-up.",
                    ),
                ],
                "exercise_items": [
                    (
                        "style-note-1",
                        "Leadership style self-reflection",
                        "Complete the style self-assessment, record your score, then note one strength, one blind spot, and one situation where your default style helps or hurts.",
                    ),
                    (
                        "style-note-2",
                        "Situational style check",
                        "Think of three team members at different levels of confidence and capability and choose whether directing, coaching, supporting, or delegating would help each one most right now.",
                    ),
                ],
            },
            "delegation": {
                "sections": [
                    (
                        "why-delegation-matters",
                        "Why Delegation Matters",
                        "Delegation is not simply about taking work off my plate. In this topic, I use delegation to create scale, build capability, and free up attention for the work only I should be doing. The material in the uploaded extracts is clear on one important point: when leaders keep solving everything themselves, the team stays dependent and the leader becomes the bottleneck. Delegation gives other people the chance to learn, stretch, and develop confidence through real work. It also gives me the room to focus on bigger decisions, judgement calls, and leadership responsibilities that cannot be handed off in the same way.",
                    ),
                    (
                        "what-to-delegate",
                        "What to Delegate and to Whom",
                        "Good delegation starts with choosing the right work, not just any work. The course extracts highlight that I should delegate based not only on who can do the job now, but also on learning goals, interests, and the broader spread of capability across the team. That means I am not only asking who is fastest. I am asking who would grow from this, who needs exposure to this kind of problem, and how I can distribute ownership more evenly. In practice, this could mean giving a capable team member ownership of a stakeholder update, asking someone to lead a planning segment, or assigning a technical workstream to a person who is ready to move up a level with support.",
                    ),
                    (
                        "clarity-and-checkpoints",
                        "Clarity, Autonomy, and Checkpoints",
                        "Delegation works best when I am clear about the outcome, the boundaries, and the support model. If I only hand over the task, I increase the risk of vague ownership. The uploaded material reinforces that leaders should break large work into manageable chunks, agree the plan, and monitor progress without smothering it. In practice, that means making the desired result explicit, naming the success measures, explaining what decisions the other person can make on their own, and setting a few sensible checkpoints. That is very different from either micromanaging every step or disappearing completely after the handoff.",
                    ),
                    (
                        "freedom-ladder",
                        "From Delegation to Empowerment",
                        "One of the more useful ideas in the extracts is the movement from tightly directed work toward greater freedom and empowerment. People often start by waiting to be told, then asking what is next, then suggesting options, then acting and reporting back, and eventually operating with much more independent ownership. In this topic, I treat delegation as part of that ladder rather than the end of it. My role is to help people move upward by giving challenge, coaching, and trust in a paced way. I do not need to jump to full autonomy immediately, but I do need to stop holding people below the level they are ready for.",
                    ),
                ],
                "exercise_items": [
                    (
                        "delegation-note-1",
                        "Delegation inventory",
                        "List the work you still hold personally, then divide it into three buckets: work only you should do, work you could delegate now, and work you could delegate within the next quarter if you trained or coached someone first.",
                    ),
                    (
                        "delegation-note-2",
                        "Stretch assignment match",
                        "Choose one meaningful piece of work and map it against a team member’s current capability, interests, and development goals. Note why this is the right assignment and what support they will need from you.",
                    ),
                    (
                        "delegation-note-3",
                        "Delegation briefing template",
                        "Draft a short delegation brief that covers the desired outcome, success measures, constraints, decision rights, check-in points, and what support the person can expect if they get stuck.",
                    ),
                ],
            },
            "building-trust": {
                "sections": [
                    (
                        "trust-core",
                        "Trust as a Performance Multiplier",
                        "The journal makes trust central. Trust is built when leaders communicate clearly, follow through on commitments, behave with integrity, and treat people with respect. It is not only emotional. It directly affects whether people share concerns early, ask for help, and collaborate effectively. In teams with strong trust, bad news travels faster because people assume honesty will be met with problem-solving. In teams with weak trust, people often delay raising issues because they expect blame, defensiveness, or indifference.",
                    ),
                    (
                        "trust-practices",
                        "Repeatable Trust-Building Practices",
                        "The source material suggests practical ways to build trust: be open and honest, lead by example, keep promises, create recognition moments, and invest in relationships across the organization. In real teams, trust often grows through dozens of small moments rather than one big intervention. A leader who regularly closes the loop after a one-on-one, admits when they got something wrong, and makes time to understand what matters to each team member is building trust in a way people can actually feel.",
                    ),
                    (
                        "trust-breakdowns",
                        "How Trust Gets Damaged",
                        "Trust is usually damaged through patterns rather than a single dramatic event. Leaders erode trust when they say one thing and do another, hold different people to different standards, avoid difficult truths, or become unpredictable under pressure. For example, if a manager says feedback is welcome but becomes defensive every time they are challenged, the team learns that speaking up is risky. If deadlines are changed without explanation or promises to remove blockers keep slipping, reliability starts to weaken. Repair begins with naming the problem clearly, taking responsibility where needed, and rebuilding consistency over time.",
                    ),
                ],
                "exercise_items": [
                    (
                        "trust-note-1",
                        "Sharing personal stories",
                        "Invite your team to share a personal story or meaningful experience and note what you learn about trust, connection, and psychological closeness when people feel known beyond their task list.",
                    ),
                    (
                        "trust-note-2",
                        "Peer recognition and trust repair",
                        "Run a short recognition round, then capture one commitment you will keep visibly, one trust-building behaviour you want to repeat, and one area where you need to rebuild confidence through consistency.",
                    ),
                    (
                        "trust-note-3",
                        "Group problem-solving",
                        "Bring the team into a real problem, observe how openly people contribute, and note what your own behaviour did to increase or reduce honesty, accountability, and shared ownership.",
                    ),
                ],
            },
            "empathy-and-emotional-intelligence": {
                "sections": [
                    (
                        "eq-domains",
                        "The Four Domains of Emotional Intelligence",
                        "Emotional intelligence can be understood through self-awareness, self-management, social awareness, and relationship management. Self-awareness is noticing what you are feeling, what triggers you, and how your behaviour lands on others. Self-management is your ability to regulate that response rather than act on impulse. Social awareness is reading the room accurately, including tone, energy, and what may be unsaid. Relationship management is using all of that information to communicate, influence, and resolve tension well. Leaders who are strong in these areas manage themselves better under stress, make better decisions, and communicate in ways that strengthen rather than weaken relationships.",
                    ),
                    (
                        "emotional-agility",
                        "Emotional Agility and Empathy in Action",
                        "The material highlights showing up to emotions, stepping out from automatic reactions, connecting to your values, and choosing courage over comfort. It also makes a useful point about empathy: you need enough empathy to understand the other person, but not so much that you become overwhelmed and lose your ability to lead the conversation. For example, if a team member is upset after tough feedback, empathy does not mean withdrawing the message to make the discomfort disappear. It means acknowledging the emotion, listening properly, and still helping the conversation move toward clarity and growth.",
                    ),
                    (
                        "workplace-empathy",
                        "Empathy at Work",
                        "Communicating with empathy at work means paying attention to intention and impact, listening actively, and responding in ways that acknowledge the other person's experience without losing clarity about expectations or outcomes. A practical example is a leader saying, 'I can see this change is frustrating and I understand why it feels disruptive. Let me walk through what is changing, what is not, and how we will support the team through it.' That response is different from either dismissing the emotion or getting lost in it.",
                    ),
                ],
                "exercise_items": [
                    (
                        "eq-note-1",
                        "EI self-awareness journal",
                        "Write about a recent emotionally charged interaction, name the emotion underneath your reaction, and note how that feeling shaped your behaviour, judgment, and communication.",
                    ),
                    (
                        "eq-note-2",
                        "Active listening and empathy practice",
                        "Choose one conversation where your goal is to understand before solving, then capture what changed when you listened for the other person's perspective, concerns, and emotion rather than rushing to advice.",
                    ),
                    (
                        "eq-note-3",
                        "Communication and mindfulness exercise",
                        "Draft one difficult message in plain language, reduce it to the clearest core sentence you can, and pair that with a calming routine you can use before high-pressure conversations.",
                    ),
                ],
            },
            "psychological-safety-diversity-allyship": {
                "sections": [
                    (
                        "psychological-safety",
                        "Psychological Safety",
                        "Psychological safety is the team condition that lets people speak honestly without bracing for embarrassment, ridicule, or punishment. In this journal, I think about it as the answer to a simple question: how safe does it feel here to be candid? A psychologically safe team is more willing to raise risks early, ask for help, challenge an idea, admit uncertainty, or say, 'I do not think this is working.' That does not mean standards are low or that difficult conversations disappear. It means truth can enter the room before the situation gets worse. In real work, I see psychological safety when someone flags a delivery concern before a deadline is missed, when a new team member asks a basic question without feeling small, or when people disagree on an approach without turning disagreement into a personal threat.",
                    ),
                    (
                        "diversity",
                        "Diversity",
                        "Diversity is about difference within the team: difference in background, lived experience, identity, thought, culture, communication style, and perspective. I do not treat diversity as a headline metric alone because a team can be diverse on paper and still feel narrow in whose ideas carry weight. Diversity matters because it expands how problems are seen, what risks get noticed, and what possibilities become visible. In practice, I notice diversity when a team brings multiple points of view to planning, customer understanding, technical debate, or problem-solving. The leadership responsibility here is not just to recruit for diversity. It is to recognize that difference changes how people experience the same environment, and that those differences need to be understood rather than flattened.",
                    ),
                    (
                        "inclusion",
                        "Inclusion",
                        "Inclusion is about whether people are genuinely invited into the work, not just present around it. This is where I ask harder questions: who gets heard, who gets interrupted, whose ideas get picked up, who gets the stretch opportunity, and who is trusted quickly versus slowly? Inclusion is visible in the daily mechanics of leadership, not only in formal policy. A leader can have a diverse group but still run meetings in a way that rewards only the fastest speakers, the most confident communicators, or the people who already match the dominant style. A more inclusive leader creates multiple ways to contribute, makes expectations explicit, rotates visible opportunities, and notices where important decisions are being shaped by too narrow a set of voices.",
                    ),
                    (
                        "belonging",
                        "Belonging",
                        "Belonging is the felt experience of being able to show up fully and still be respected, included, and valued. I think of belonging as the emotional proof that inclusion is working. People can be included mechanically and still not feel they belong if they are constantly editing themselves, downplaying part of their identity, or reading subtle signals that they are outside the real centre of the group. In practice, belonging shows up when a person does not have to spend extra energy decoding whether they are accepted, when recognition is not limited to one type of contribution, and when people see that their perspective influences outcomes rather than simply being tolerated. Leaders shape belonging through fairness, curiosity, representation, language, recognition, and the everyday signals of who matters here.",
                    ),
                    (
                        "allyship",
                        "Allyship",
                        "Allyship is not a label I claim once. It is a pattern of action. In this topic, allyship means noticing where someone is being overlooked, disadvantaged, interrupted, stereotyped, or left to carry a burden alone, then using my position, voice, and influence to change that moment. In real work, allyship may mean crediting an idea back to the person who first raised it, interrupting biased language instead of waiting for the affected person to respond, sponsoring someone for an opportunity they might otherwise be excluded from, or challenging a hiring conversation that drifts into comfort and similarity bias. Good allyship is active, specific, and visible enough that people do not have to guess whether support exists.",
                    ),
                    (
                        "team-practice",
                        "What This Looks Like in Team Practice",
                        "These ideas become real through team habits. The journal material points to useful contrasts: shame versus empathy, heroes versus teams, stress versus calm, and failure versus experimentation. Those contrasts help me see the culture patterns that either strengthen or weaken safety and inclusion. A hero culture usually rewards the loudest rescuer and hides the team conditions that created the problem. A shame-based response may produce short-term compliance, but it usually drives issues underground. A healthier pattern is calmer and more team-oriented: leaders thank people for raising concerns, invite dissent before decisions harden, make room for quieter contributors, and create clear standards without using fear as the operating system. This is also why psychological safety and DIB work belong together. Teams are most effective when people feel both safe to contribute and confident that their contribution will be valued fairly.",
                    ),
                ],
                "exercise_items": [
                    (
                        "safety-note-1",
                        "Psychological safety check",
                        "Think about the last time someone on your team made a mistake, challenged your view, or raised a risk. Record how you responded and what your response may have taught the rest of the team about the safety of speaking up.",
                    ),
                    (
                        "safety-note-2",
                        "Inclusion and belonging audit",
                        "After your next meeting, note who spoke most, who spoke least, whose ideas were picked up, and what you did to widen participation and strengthen belonging.",
                    ),
                    (
                        "safety-note-3",
                        "Visible allyship commitment",
                        "Write one practical allyship action you will take this month in a meeting, feedback conversation, hiring discussion, or stretch-assignment decision, then note how you will make that action visible and repeatable.",
                    ),
                    (
                        "safety-note-4",
                        "Belonging signal review",
                        "List the subtle signals your team sends about who belongs, who gets trusted, and whose contribution is celebrated. Note one signal you want to strengthen and one you want to interrupt.",
                    ),
                ],
            },
            "cross-cultural-leadership": {
                "sections": [
                    (
                        "cultural-awareness",
                        "Cultural Awareness and Leadership Perspective",
                        "Cross-cultural leadership starts with noticing that my own norms are not neutral. The way I communicate, challenge, ask questions, make decisions, or show confidence is shaped by a context, not by a universal standard. Some teams may read directness as efficiency and honesty, while others may experience the same tone as abrupt or disrespectful unless there is more context around it. Some people expect decisions to be debated openly. Others expect more alignment-building before disagreement becomes public. I become a stronger leader when I stop assuming my version of normal is the baseline everyone else shares.",
                    ),
                    (
                        "communication-norms",
                        "Communication Norms Across Cultures",
                        "Communication is one of the quickest places where cross-cultural friction shows up. People vary in how directly they speak, how much context they expect, how comfortable they are interrupting, and whether they are more likely to contribute live or after reflection. The journal material helps here because it points me toward active listening, open-ended questions, and multiple channels for contribution. In practice, I improve cross-cultural communication when I make the context clearer, reduce idioms and local shorthand, invite follow-up in writing, and confirm what people heard instead of assuming that everyone interpreted the same message in the same way.",
                    ),
                    (
                        "decision-making-and-conflict",
                        "Decision-Making, Disagreement, and Conflict",
                        "Differences in culture also shape how people experience conflict and commitment. One person may think a healthy meeting is full of visible debate. Another may prefer to test concerns privately or through questions that sound less confrontational. Agreement in a meeting may mean commitment, or it may simply mean politeness in the moment. Silence may mean reflection, uncertainty, disagreement, or respect for hierarchy. When I lead across cultures, I need to make decision rules clearer. I need to say when we are discussing, when we are deciding, what input is still open, and what commitment looks like once a decision is made.",
                    ),
                    (
                        "building-shared-team-norms",
                        "Building Shared Team Norms",
                        "The goal is not to master every culture individually. The goal is to build a team environment where the important norms are explicit enough that people can work well together. Shared team norms help here. These might include how decisions are documented, how challenge is invited, how meetings are prepared, what response times are reasonable, when written follow-up is expected, and how feedback should be framed. Shared norms reduce the pressure on individuals to decode the team by guesswork. They also lower the chance that one dominant communication style quietly becomes the only acceptable one.",
                    ),
                    (
                        "common-misreads",
                        "Common Misreads and Repair Moves",
                        "Cross-cultural friction often comes from misinterpretation rather than bad intent. Silence can be read as disengagement when it is actually reflection. Directness can be read as aggression when it is intended as efficiency. A lack of questions can be mistaken for understanding when it may reflect caution or hierarchy. Repair usually starts with curiosity rather than correction. I can ask what someone meant, what would help them contribute more easily, or how they prefer to work through disagreement. Those questions help me move from assumption to understanding before tension hardens into judgement.",
                    ),
                ],
                "exercise_items": [
                    (
                        "culture-note-1",
                        "Communication translation",
                        "Choose one message you routinely deliver and rewrite it for a more cross-cultural audience. Remove local shorthand, make the context explicit, and spell out what action or decision is needed.",
                    ),
                    (
                        "culture-note-2",
                        "Meeting norm review",
                        "Think about one recurring team meeting and note which behaviours it currently rewards. Does it favour fast speakers, confident challengers, or people with more context? Capture one change that would widen participation.",
                    ),
                    (
                        "culture-note-3",
                        "Decision clarity exercise",
                        "Take one recent decision and write down where confusion may have come from: unclear discussion boundaries, unclear ownership, unclear commitment, or different cultural assumptions about how disagreement should happen.",
                    ),
                    (
                        "culture-note-4",
                        "Shared team norms draft",
                        "Draft a simple set of cross-cultural team norms for communication, meetings, challenge, and follow-through. Note which norm would reduce the most friction in your current team.",
                    ),
                ],
            },
            "transition-to-leadership": {
                "sections": [
                    (
                        "role-shift",
                        "From Doing the Work to Enabling the Work",
                        "This transition material is especially useful here. It explains that new managers often struggle because they keep measuring themselves like individual contributors. The role shift is toward communication, delegation, team support, and systems for performance. Many new leaders still feel most comfortable being the person with the answers, the person doing the hardest task, or the person who rescues delivery. The challenge is that these habits can make the team dependent and keep the leader overloaded.",
                    ),
                    (
                        "engineering-manager-skills",
                        "Practical Skills in the Transition",
                        "The content points to role-play, delegation, team building, time management, and communication as transitional skills. These are not peripheral. They are the core capabilities that help a new leader scale beyond personal output. For example, a new manager who learns to run effective one-on-ones, delegate a planning responsibility properly, and protect time for coaching is usually building far more long-term value than one who personally fixes every urgent task.",
                    ),
                    (
                        "transition-traps",
                        "Common Transition Traps",
                        "The most common traps are over-involvement, under-delegation, and identity confusion. Over-involvement looks like rewriting someone else's work, jumping into every decision, or treating support work as secondary to your own output. Under-delegation happens when leaders say they want ownership but do not hand over authority, context, or room to learn. Identity confusion appears when a leader is promoted but still defines success mainly through personal execution rather than team growth, team clarity, and team results.",
                    ),
                ],
                "exercise_items": [
                    (
                        "transition-note-1",
                        "Old role / new role",
                        "List three habits that served you as an individual contributor but now make it harder to lead through others, then note what leader behaviour should replace each one.",
                    ),
                    (
                        "transition-note-2",
                        "Delegation and time audit",
                        "Choose one task to delegate properly, write the context and guardrails you will provide, and review your calendar to see whether your time reflects leadership work or individual contributor habits.",
                    ),
                    (
                        "transition-note-3",
                        "Role-play preparation",
                        "Prepare for one real leadership conversation by role-playing how you will explain expectations, ask questions, and avoid stepping back into rescuer mode.",
                    ),
                ],
            },
            "giving-and-receiving-feedback": {
                "sections": [
                    (
                        "feedback-growth",
                        "Feedback as a Growth System",
                        "Feedback is framed as an ongoing practice, not a once-a-year ritual. Leaders need to create conditions where feedback is normal, specific, and developmental. Good feedback is usually timely, grounded in observable behaviour, clear about impact, and connected to a future action. For example, instead of saying 'You need to communicate better,' a stronger leader might say, 'In the client update yesterday, the risks were mentioned very late, which made the conversation harder to steer. Next time, raise the risk earlier and propose a recommendation so the discussion stays constructive.'",
                    ),
                    (
                        "difficult-conversations",
                        "Difficult Conversations and Performance",
                        "The material adds depth on avoider versus aggressor styles, fear of emotions, assumptions, rescuing, and mapping difficult conversations in advance. This gives managers a more practical toolkit for how to start, steer, and stay productive in hard conversations. Avoiders often soften the message so much that the issue remains unclear. Aggressors may be clear but create defensiveness that blocks learning. Strong leaders aim for a middle path: direct, respectful, specific, and future-focused.",
                    ),
                    (
                        "growth-mindset-feedback",
                        "Mindset and Curiosity",
                        "The course also highlights growth versus fixed mindset, replacing assumptions with curiosity, and setting expectations from the start. These ideas matter because feedback conversations improve when both leader and employee believe growth is possible. A curiosity-led manager asks, 'What got in the way here?' or 'What support would help you do this differently next time?' That does not remove accountability. It makes the conversation more useful than simply labelling the person as a problem.",
                    ),
                ],
                "exercise_items": [
                    (
                        "feedback-note-1",
                        "Feedback journal",
                        "Track one piece of feedback you gave, one piece you received, how specific it was, and what visible follow-through happened afterwards.",
                    ),
                    (
                        "feedback-note-2",
                        "Feedback challenge and conversation map",
                        "Use a real upcoming conversation to map what happened, the impact, the change you are asking for, and whether you are slipping into avoidance, aggression, rescuing, or curiosity.",
                    ),
                    (
                        "feedback-note-3",
                        "GROW coaching notes",
                        "Use the GROW model to coach someone through a topic by capturing the goal, the current reality, the options available, and what they will commit to next.",
                    ),
                ],
            },
        }

        quiz_map = {
            "wisetech-leadership-foundations": [
                _quiz_question(
                    "foundation-quiz-1",
                    "What is the strongest starting point for effective leadership in this journal?",
                    [
                        ("a", "Managing myself before trying to lead others well.", 0),
                        ("b", "Using authority early so the team moves faster.", 0),
                        ("c", "Keeping mistakes quiet so confidence stays high.", 0),
                    ],
                    correct_option_id="a",
                    feedback="The journal keeps returning to one idea: leadership starts with how I manage myself, my choices, and my visible behaviour.",
                ),
                _quiz_question(
                    "foundation-quiz-2",
                    "Which behaviour best converts failure into growth?",
                    [
                        ("a", "Assigning blame quickly so standards stay firm.", 0),
                        ("b", "Turning setbacks into a learning discussion with accountability and support.", 0),
                        ("c", "Avoiding the topic until emotions settle down.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The draft frames failure as something leaders should convert into learning, not blame or avoidance.",
                ),
                _quiz_question(
                    "foundation-quiz-3",
                    "When pressure increases, what does strong role modelling look like?",
                    [
                        ("a", "Staying calm, communicating openly, and making the next step clear.", 0),
                        ("b", "Keeping everyone guessing until the full answer is known.", 0),
                        ("c", "Taking over every task personally.", 0),
                    ],
                    correct_option_id="a",
                    feedback="Visible steadiness, honest communication, and good judgement are some of the clearest signals of leadership maturity in the journal.",
                ),
            ],
            "leadership-styles": [
                _quiz_question("style-quiz-1", "When it comes to decision-making, I prefer to:", [("a", "Make decisions based on my instincts and experience.", 1), ("b", "Gather input from others before making a decision.", 2), ("c", "Consider all possible options and make a logical choice.", 3)]),
                _quiz_question("style-quiz-2", "In a team setting, I tend to:", [("a", "Take charge and make sure everyone knows what they should be doing.", 1), ("b", "Listen to everyone's ideas and encourage collaboration.", 2), ("c", "Ensure that everyone is following the rules and sticking to the plan.", 3)]),
                _quiz_question("style-quiz-3", "When facing a difficult problem, I usually:", [("a", "Trust my gut and take action quickly.", 1), ("b", "Gather information and brainstorm with others before deciding on a solution.", 2), ("c", "Analyze the problem thoroughly and come up with a logical solution.", 3)]),
                _quiz_question("style-quiz-4", "In a conflict situation, I tend to:", [("a", "Take a firm stance and assert my authority.", 1), ("b", "Listen to both sides and try to find a compromise.", 2), ("c", "Try to avoid conflict altogether.", 3)]),
                _quiz_question("style-quiz-5", "When it comes to delegating tasks, I tend to:", [("a", "Give clear instructions and expect them to be followed.", 1), ("b", "Provide guidance and support while encouraging independence.", 2), ("c", "Trust others to handle the task in their own way.", 3)]),
                _quiz_question("style-quiz-6", "My communication style is usually:", [("a", "Direct, concise, and focused on action.", 1), ("b", "Open, collaborative, and discussion-oriented.", 2), ("c", "Reserved, reflective, and focused on analysis.", 3)]),
                _quiz_question("style-quiz-7", "When setting goals, I usually:", [("a", "Set the direction myself and expect the team to execute.", 1), ("b", "Co-create goals with the team so there is buy-in.", 2), ("c", "Set broad outcomes and let people shape the approach.", 3)]),
                _quiz_question("style-quiz-8", "In a leadership role, I see myself primarily as:", [("a", "The person responsible for direction and control.", 1), ("b", "The person who guides, involves, and develops others.", 2), ("c", "The person who creates space and autonomy for others to operate.", 3)]),
            ],
            "delegation": [
                _quiz_question(
                    "delegation-quiz-1",
                    "What is the strongest reason to delegate well as a leader?",
                    [
                        ("a", "To clear low-value tasks from my calendar only.", 0),
                        ("b", "To create scale, grow capability, and free myself for higher-value leadership work.", 0),
                        ("c", "To stay less involved in team development.", 0),
                    ],
                    correct_option_id="b",
                    feedback="This topic treats delegation as a leadership multiplier. It helps the team grow while freeing me for the work only I should be doing.",
                ),
                _quiz_question(
                    "delegation-quiz-2",
                    "What should shape a good delegation decision?",
                    [
                        ("a", "Only who can do the work fastest right now.", 0),
                        ("b", "Capability, learning goals, interest, and a sensible spread of ownership.", 0),
                        ("c", "Whoever is least likely to challenge the task.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The extracts point to delegation based on both current capability and future development, not speed alone.",
                ),
                _quiz_question(
                    "delegation-quiz-3",
                    "What best separates strong delegation from micromanagement?",
                    [
                        ("a", "Agreeing the outcome, boundaries, and checkpoints while leaving room for ownership.", 0),
                        ("b", "Reviewing every step before the person can move forward.", 0),
                        ("c", "Handing over the task and disappearing entirely.", 0),
                    ],
                    correct_option_id="a",
                    feedback="Strong delegation keeps clarity and support, but it does not drag the work back into the leader’s hands at every step.",
                ),
            ],
            "building-trust": [
                _quiz_question(
                    "trust-quiz-1",
                    "What tends to build trust fastest over time?",
                    [
                        ("a", "One inspiring speech from the leader.", 0),
                        ("b", "Repeated follow-through, openness, and consistent standards.", 0),
                        ("c", "Avoiding difficult topics so relationships stay smooth.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The trust material treats trust as cumulative. Small, reliable actions matter more than occasional big gestures.",
                ),
                _quiz_question(
                    "trust-quiz-2",
                    "Which leader behaviour is most likely to damage trust?",
                    [
                        ("a", "Saying feedback is welcome, then becoming defensive when challenged.", 0),
                        ("b", "Closing the loop on promised actions.", 0),
                        ("c", "Admitting when you got something wrong.", 0),
                    ],
                    correct_option_id="a",
                    feedback="Trust breaks down quickly when there is a gap between what I say and how I actually respond.",
                ),
                _quiz_question(
                    "trust-quiz-3",
                    "What is the most useful first move when trust has weakened?",
                    [
                        ("a", "Pretend nothing happened and focus on the next deliverable.", 0),
                        ("b", "Name the issue, take responsibility where needed, and rebuild consistency.", 0),
                        ("c", "Wait until the team brings it up again.", 0),
                    ],
                    correct_option_id="b",
                    feedback="Repair starts with clarity and accountability, then gets reinforced by consistent behaviour over time.",
                ),
            ],
            "empathy-and-emotional-intelligence": [
                _quiz_question(
                    "eq-quiz-1",
                    "Which set best describes the core domains of emotional intelligence?",
                    [
                        ("a", "Confidence, charisma, decisiveness, resilience.", 0),
                        ("b", "Self-awareness, self-management, social awareness, relationship management.", 0),
                        ("c", "Empathy, feedback, planning, delegation.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The journal frames EQ through those four connected domains so leaders can notice and strengthen what sits underneath their behaviour.",
                ),
                _quiz_question(
                    "eq-quiz-2",
                    "What does empathy look like in a difficult conversation?",
                    [
                        ("a", "Softening the message so the discomfort disappears.", 0),
                        ("b", "Ignoring emotions and moving straight to action.", 0),
                        ("c", "Acknowledging the emotion while still helping the conversation move toward clarity.", 0),
                    ],
                    correct_option_id="c",
                    feedback="The material makes it clear that empathy is not avoiding the issue. It is understanding the person without losing the purpose of the conversation.",
                ),
                _quiz_question(
                    "eq-quiz-3",
                    "Which exercise from the draft most strengthens self-awareness?",
                    [
                        ("a", "Keeping a journal of emotionally charged interactions and what triggered them.", 0),
                        ("b", "Waiting until conflict is over before reflecting.", 0),
                        ("c", "Only focusing on the other person's behaviour.", 0),
                    ],
                    correct_option_id="a",
                    feedback="The journal specifically recommends written reflection because it helps me see the roots of my reactions instead of only the surface behaviour.",
                ),
            ],
            "psychological-safety-diversity-allyship": [
                _quiz_question(
                    "safety-quiz-1",
                    "Psychological safety means:",
                    [
                        ("a", "People can contribute honestly without fear of humiliation, while standards still stay high.", 0),
                        ("b", "Leaders avoid challenge so no one feels uncomfortable.", 0),
                        ("c", "Teams stop holding one another accountable.", 0),
                    ],
                    correct_option_id="a",
                    feedback="The journal treats safety and accountability as partners, not opposites.",
                ),
                _quiz_question(
                    "safety-quiz-2",
                    "Which statement best describes allyship?",
                    [
                        ("a", "A one-time statement of support.", 0),
                        ("b", "Active behaviour that notices inequity and uses influence to address it.", 0),
                        ("c", "Letting inclusion sit with HR alone.", 0),
                    ],
                    correct_option_id="b",
                    feedback="Allyship in the journal is behavioural. It becomes visible in meetings, decisions, and who gets heard or sponsored.",
                ),
                _quiz_question(
                    "safety-quiz-3",
                    "What is a common anti-pattern that weakens safety?",
                    [
                        ("a", "A hero culture that celebrates the rescuer more than the team system.", 0),
                        ("b", "Calm leaders who encourage learning.", 0),
                        ("c", "Structured ways for quieter voices to contribute.", 0),
                    ],
                    correct_option_id="a",
                    feedback="Hero patterns often hide the deeper team habits that would have prevented the problem in the first place.",
                ),
            ],
            "cross-cultural-leadership": [
                _quiz_question(
                    "culture-quiz-1",
                    "What is a good default assumption in cross-cultural leadership?",
                    [
                        ("a", "My normal communication style is neutral for everyone.", 0),
                        ("b", "Silence always means agreement.", 0),
                        ("c", "Different cultures may read the same behaviour differently, so I should test assumptions.", 0),
                    ],
                    correct_option_id="c",
                    feedback="The journal warns against treating my own norm as universal. Good leaders check interpretation rather than assuming shared meaning.",
                ),
                _quiz_question(
                    "culture-quiz-2",
                    "Which practice usually makes a global team conversation more equitable?",
                    [
                        ("a", "Sharing context in advance and inviting input in more than one format.", 0),
                        ("b", "Only relying on live verbal discussion.", 0),
                        ("c", "Equating fast responses with commitment.", 0),
                    ],
                    correct_option_id="a",
                    feedback="Written pre-reads, clear summaries, and multiple response channels reduce the advantage of one communication norm over another.",
                ),
                _quiz_question(
                    "culture-quiz-3",
                    "What is the most common source of cross-cultural friction?",
                    [
                        ("a", "Bad intent from one side.", 0),
                        ("b", "Misinterpretation and untested assumptions.", 0),
                        ("c", "A lack of technical skill.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The draft repeatedly points to misreads around directness, silence, and agreement rather than assuming malice.",
                ),
            ],
            "transition-to-leadership": [
                _quiz_question(
                    "transition-quiz-1",
                    "What is the deepest shift when moving from individual contributor to leader?",
                    [
                        ("a", "Owning more complex personal work.", 0),
                        ("b", "Moving from personal output toward enabling team output.", 0),
                        ("c", "Reducing communication to save time.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The transition topic keeps coming back to one thing: my job changes from doing the work myself to helping the team do the work well.",
                ),
                _quiz_question(
                    "transition-quiz-2",
                    "Which is a common transition trap?",
                    [
                        ("a", "Delegating with context and follow-up.", 0),
                        ("b", "Protecting time for one-on-ones and coaching.", 0),
                        ("c", "Jumping back into every detail because doing feels more comfortable than leading.", 0),
                    ],
                    correct_option_id="c",
                    feedback="Over-involvement and identity confusion are classic signs that a new leader is still measuring themselves like an individual contributor.",
                ),
                _quiz_question(
                    "transition-quiz-3",
                    "Which capability is central to a healthy transition?",
                    [
                        ("a", "Perfect technical answers.", 0),
                        ("b", "Delegation, communication, and team support.", 0),
                        ("c", "Keeping every critical task personally owned.", 0),
                    ],
                    correct_option_id="b",
                    feedback="The draft positions delegation, communication, and coaching as the core of the new role, not a side responsibility.",
                ),
            ],
            "giving-and-receiving-feedback": [
                _quiz_question(
                    "feedback-quiz-1",
                    "What makes feedback most useful?",
                    [
                        ("a", "It is specific, timely, and linked to observable behaviour and next steps.", 0),
                        ("b", "It stays broad so the other person can interpret it freely.", 0),
                        ("c", "It only happens during formal review cycles.", 0),
                    ],
                    correct_option_id="a",
                    feedback="The journal describes feedback as an ongoing growth system, not an annual event or a vague impression.",
                ),
                _quiz_question(
                    "feedback-quiz-2",
                    "What is the main risk of an avoider style in difficult conversations?",
                    [
                        ("a", "People feel attacked immediately.", 0),
                        ("b", "The message gets softened so much that the issue never becomes clear.", 0),
                        ("c", "The team receives too much structure.", 0),
                    ],
                    correct_option_id="b",
                    feedback="Avoidance can feel kind in the moment, but it often blocks growth because the real issue never lands.",
                ),
                _quiz_question(
                    "feedback-quiz-3",
                    "What does the GROW model help a leader do?",
                    [
                        ("a", "Coach someone through a goal, the current reality, options, and next steps.", 0),
                        ("b", "Decide a performance rating faster.", 0),
                        ("c", "Avoid emotions completely.", 0),
                    ],
                    correct_option_id="a",
                    feedback="The draft uses GROW as a simple coaching structure that keeps conversations developmental and practical.",
                ),
            ],
        }

        quiz_band_map = {
            "leadership-styles": [
                QuizResultBand(
                    min_score=8,
                    max_score=16,
                    title="Authoritarian / Directive Tendency",
                    description="I may naturally step into control, fast decision-making, and strong direction. That can help in a crisis, but I need to watch whether it reduces input and ownership.",
                ),
                QuizResultBand(
                    min_score=17,
                    max_score=24,
                    title="Democratic / Participative Tendency",
                    description="I tend to value collaboration, shared problem-solving, and team input. This usually builds buy-in well, though I still need to stay decisive when speed matters.",
                ),
                QuizResultBand(
                    min_score=25,
                    max_score=32,
                    title="Laissez-Faire / Hands-Off Tendency",
                    description="I likely create strong autonomy and space. That can work well with experienced people, but I need to make sure freedom is supported by clarity, boundaries, and follow-through.",
                ),
            ],
        }

        book_map = {
            "wisetech-leadership-foundations": [
                _book("found-book-1", "Start With Why", "Simon Sinek", "Leadership and Motivation", "Helps me connect leadership to purpose, meaning, and the ability to explain why the work matters before I ask people to follow."),
                _book("found-book-2", "Leaders Eat Last", "Simon Sinek", "Leadership", "Useful for thinking about trust, safety, and the responsibility leaders carry for the environment their teams experience."),
                _book("found-book-3", "The Coaching Habit", "Michael Bungay Stanier", "Mentoring and Coaching", "A practical guide for leading through questions and habit-building rather than always being the person with the answer."),
                _book("practice-book-2", "The Hard Thing About Hard Things", "Ben Horowitz", "Leadership Under Pressure", "Adds a more realistic lens on pressure, hard calls, and the kind of difficult people decisions that often sit beneath leadership fundamentals."),
                _book("practice-book-3", "Build", "Tony Fadell", "Product and People Leadership", "Useful for leaders balancing product, business, and people judgement while still trying to build a healthy leadership approach."),
            ],
            "leadership-styles": [
                _book("style-book-1", "Turn the Ship Around", "L. David Marquet", "Leadership and Motivation", "A strong companion to the styles topic because it shows how a leader can shift from control-heavy direction toward intent, ownership, and capability-building."),
                _book("style-book-2", "The Making of a Manager", "Julie Zhuo", "Leadership", "Covers the basics of first-time leadership with a tone that makes it easier to reflect on what style I default to and what my team needs instead."),
                _book("style-book-3", "It’s Your Ship", "D. Michael Abrashoff", "Leadership", "A practical case study in how leadership approach changes team performance, especially when trust and empowerment start replacing command-and-control habits."),
            ],
            "delegation": [
                _book("delegation-book-1", "The One Minute Manager Meets the Monkey", "Kenneth Blanchard, William Oncken Jr., and Hal Burrows", "Delegation", "A classic delegation read that helps leaders notice when work keeps jumping back onto their shoulders and how to stop becoming the bottleneck."),
                _book("delegation-book-2", "Turn the Ship Around", "L. David Marquet", "Empowerment and Ownership", "A strong fit for delegation because it shows how leaders can move from control to intent, capability, and ownership without losing accountability."),
                _book("delegation-book-3", "Multipliers", "Liz Wiseman", "Capability Building", "Useful for delegation because it focuses on how leaders create more intelligence, confidence, and contribution in the people around them instead of being the smartest person in every room."),
            ],
            "building-trust": [
                _book("trust-book-1", "Radical Candor", "Kim Scott", "Leadership and People", "Useful for trust because it links care, challenge, honesty, and direct communication instead of treating them as competing priorities."),
                _book("trust-book-2", "Leaders Eat Last", "Simon Sinek", "Leadership", "Reinforces the idea that trust is a leadership responsibility and that team safety comes from repeated, visible leader behaviour."),
                _book("trust-book-3", "Bringing Out the Best in People", "Aubrey Daniels", "Leadership and Motivation", "Recommended in the draft for its message on feedback, reinforcement, and how to create conditions where people can contribute at their best."),
            ],
            "empathy-and-emotional-intelligence": [
                _book("eq-book-1", "Emotional Intelligence", "Daniel Goleman", "Emotional Intelligence", "A foundational read for understanding why self-awareness, regulation, empathy, and social skill shape leadership effectiveness."),
                _book("eq-book-2", "Working with Emotional Intelligence", "Daniel Goleman", "Emotional Intelligence", "Builds on the original EQ framework with more direct links to workplace behaviour, team relationships, and emotionally intelligent organizations."),
                _book("eq-book-3", "Emotional", "Leonard Mlodinow", "Emotional Intelligence", "Offers a more science-based and practical lens on how emotions work, which helps deepen the journal’s treatment of empathy and self-management."),
            ],
            "psychological-safety-diversity-allyship": [
                _book("safety-book-1", "The Fearless Organization", "Amy C. Edmondson", "Psychological Safety", "One of the strongest direct fits for this topic because it explains how psychological safety helps teams learn, speak up, and perform without confusing safety with low standards."),
                _book("safety-book-2", "Inclusion on Purpose", "Ruchika Tulshyan", "Inclusion and Belonging", "A practical leadership read on making inclusion visible in everyday work rather than treating it as a side initiative."),
                _book("safety-book-3", "The Power of Vulnerability", "Brene Brown", "Belonging and Courage", "A strong companion to conversations about courage, openness, belonging, and what it takes to create emotionally safer team environments."),
                _book("safety-book-4", "Give and Take", "Adam Grant", "Team Culture and Reciprocity", "Useful for reflecting on generosity, reciprocity, and how cultures shape whether people feel safe to contribute and support one another."),
            ],
            "cross-cultural-leadership": [
                _book("culture-book-1", "The Culture Map", "Erin Meyer", "Cross-Cultural Communication", "A very strong direct fit for this topic because it helps me see how cultures differ across communication, feedback, decision-making, trust, and disagreement."),
                _book("culture-book-2", "Global Dexterity", "Andy Molinsky", "Adapting Across Cultures", "Useful for leaders who need to adapt their style across cultures without feeling inauthentic or over-scripted."),
                _book("culture-book-3", "Team of Teams", "Stanley McChrystal", "Global Coordination", "Shows how leaders can build shared understanding and coordination across complex, distributed groups with different contexts and viewpoints."),
                _book("culture-book-4", "Scaling People", "Claire Hughes Johnson", "Distributed Team Operating Rhythm", "Useful for leaders navigating distributed teams because it combines operational clarity with people systems that need to work across contexts."),
            ],
            "transition-to-leadership": [
                _book("transition-book-1", "The Making of a Manager", "Julie Zhuo", "Leadership", "One of the best fits for this topic because it speaks directly to the move from individual contributor to first-time leader in a practical and accessible way."),
                _book("transition-book-2", "The Leadership Pipeline", "Ram Charan", "Leadership", "Helpful for understanding the real shift from managing self to managing others and why each leadership step requires new habits, skills, and values."),
                _book("transition-book-3", "An Elegant Puzzle", "Will Larson", "Software Development", "Particularly useful for technical leaders because it tackles the practical challenges of engineering management, team design, and leadership tradeoffs."),
                _book("practice-book-1", "Scaling People", "Claire Hughes Johnson", "Leadership Operations", "A strong fit for new and growing leaders because it turns good management into repeatable operating rhythms, systems, and clearer people practices."),
            ],
            "giving-and-receiving-feedback": [
                _book("feedback-book-1", "Radical Candor", "Kim Scott", "Leadership and People", "A natural companion to this topic because it gives practical language for caring personally while challenging directly."),
                _book("feedback-book-2", "The Coaching Habit", "Michael Bungay Stanier", "Mentoring and Coaching", "Useful for making feedback conversations less one-directional and more developmental through stronger questions and coaching habits."),
                _book("feedback-book-3", "Bringing Out the Best in People", "Aubrey Daniels", "Leadership and Motivation", "Directly relevant because the draft highlights its message on feedback and on getting the best out of each person in the team."),
            ],
        }

        course_map = {
            "wisetech-leadership-foundations": [
                _course("found-course-1", "Leadership Foundations", "LinkedIn Learning", "Leadership fundamentals", "A broad leadership basics course that covers leading yourself, trust, empathy, communication, and inclusive leadership practices.", "https://www.linkedin.com/learning/leadership-foundations-22307442"),
                _course("found-course-2", "Leadership Foundations & Personal Development", "Coursera", "Leadership fundamentals", "A structured introduction to leadership principles, power, influence, and different leadership approaches.", "https://www.coursera.org/learn/leadership-foundations-and-personal-development"),
                _course("found-course-3", "Foundations of Leadership and Management", "Coursera", "New manager readiness", "A practical course for aspiring managers that brings together trust, adaptability, and structured problem-solving.", "https://www.coursera.org/learn/foundations-of-leadership-and-management"),
                _course("practice-course-3", "Foundations of Leadership", "Coursera", "Leadership decision-making", "A useful extra option for leaders who want a more structured lens on leadership choices, judgement, and practical decision-making.", "https://www.coursera.org/learn/foundations-of-leadership"),
            ],
            "leadership-styles": [
                _course("style-course-1", "Leadership Styles, Behaviors, and Approaches", "LinkedIn Learning", "Leadership styles", "A focused course on modern leadership styles and how to adapt your approach to different contexts.", "https://www.linkedin.com/learning/leadership-styles-behaviors-and-approaches"),
                _course("style-course-2", "Leadership Foundations & Personal Development", "Coursera", "Leadership approaches", "Useful for understanding different leadership theories and deciding what style fits different situations.", "https://www.coursera.org/learn/leadership-foundations-and-personal-development"),
                _course("style-course-3", "Leadership Foundations", "LinkedIn Learning", "Situational leadership", "Includes a practical section on leadership styles within a broader foundation course.", "https://www.linkedin.com/learning/leadership-foundations-22307442"),
            ],
            "delegation": [
                _course("delegation-course-1", "Delegation Strategies for People Leaders", "LinkedIn Learning", "Delegation strategy", "A current course focused on delegation principles, clear goals, autonomy, feedback, and common delegation challenges for people leaders.", "https://www.linkedin.com/learning/delegation-strategies-for-people-leaders"),
                _course("delegation-course-2", "Delegating Tasks", "LinkedIn Learning", "Delegation mechanics", "A practical course on delegation mindset, communicating expectations, accountability systems, and what to do when mistakes happen.", "https://www.linkedin.com/learning/delegating-tasks"),
                _course("delegation-course-3", "Delegating", "Coursera", "Delegation basics", "A beginner-friendly delegation course covering task matching, accountability, empowerment, and practical delegation scenarios.", "https://www.coursera.org/learn/delegating"),
            ],
            "building-trust": [
                _course("trust-course-1", "Building Trust", "LinkedIn Learning", "Trust building", "A direct match for the topic, covering the drivers of trust and how leaders build or repair it at work.", "https://www.linkedin.com/learning/building-trust-14841538"),
                _course("trust-course-2", "Foundations of Leadership and Management", "Coursera", "Credibility and trust", "Includes practical strategies for building trust, professionalism, and leadership credibility as a manager.", "https://www.coursera.org/learn/foundations-of-leadership-and-management"),
                _course("trust-course-3", "New Manager Foundations", "LinkedIn Learning", "Trust as a new leader", "Especially useful if the trust challenge is tied to stepping into management for the first time.", "https://www.linkedin.com/learning/new-manager-foundations-21965262"),
            ],
            "empathy-and-emotional-intelligence": [
                _course("eq-course-1", "Leading with Empathy", "LinkedIn Learning", "Empathy in leadership", "A practical course on turning empathy into everyday leadership behaviours such as listening, presence, and relationship-building.", "https://www.linkedin.com/learning/leading-with-empathy"),
                _course("eq-course-2", "Inspiring Leadership through Emotional Intelligence", "Coursera", "Emotional intelligence", "A well-known EQ leadership course focused on mindfulness, compassion, coaching, and self-awareness.", "https://www.coursera.org/learn/emotional-intelligence-leadership"),
                _course("eq-course-3", "Emotional Intelligence in Leadership", "Coursera", "Leadership self-awareness", "A shorter course for building self-awareness, emotional regulation, and stronger professional relationships.", "https://www.coursera.org/learn/emotional-intelligence-in-leadership-1"),
            ],
            "psychological-safety-diversity-allyship": [
                _course("safety-course-1", "Inclusive Leadership", "LinkedIn Learning", "Inclusive leadership", "A focused course on creating inclusive environments, assessing your inclusion impact, and leading with belonging in mind.", "https://www.linkedin.com/learning/inclusive-leadership/welcome"),
                _course("safety-course-2", "Psychological Safety", "Coursera", "Psychological safety", "A direct topic match that focuses on how to create environments where people can contribute honestly and safely.", "https://www.coursera.org/learn/psychological-safety"),
                _course("safety-course-3", "Leadership Foundations", "LinkedIn Learning", "Inclusion and belonging", "Useful because it includes trust, empathy, and inclusion as interconnected leadership skills.", "https://www.linkedin.com/learning/leadership-foundations-22307442"),
            ],
            "cross-cultural-leadership": [
                _course("culture-course-1", "Communicating Across Cultures", "LinkedIn Learning", "Cross-cultural communication", "A strong primer for working across different communication norms and cultural expectations.", "https://www.linkedin.com/learning/topics/cross-cultural-communication"),
                _course("culture-course-2", "Cross-Cultural Communication and Management", "Coursera", "Cross-cultural teams", "A practical course on culture, communication style, conflict, and how to co-create a team language across differences.", "https://www.coursera.org/learn/cross-cultural-communication-management"),
                _course("culture-course-3", "Leadership through Feedback", "LinkedIn Learning", "Cross-cultural feedback", "Useful because it explicitly touches on giving feedback across cultures and understanding communication patterns.", "https://www.linkedin.com/learning/leadership-through-feedback"),
            ],
            "transition-to-leadership": [
                _course("transition-course-1", "New Manager Foundations", "LinkedIn Learning", "New manager transition", "A comprehensive course for people moving into leadership and learning how to build trust, authority, and team connection.", "https://www.linkedin.com/learning/new-manager-foundations-21965262"),
                _course("transition-course-2", "Making the Move from Individual Contributor to Manager", "LinkedIn Learning", "IC to manager shift", "A direct fit for the mindset and role change involved in becoming a manager.", "https://www.linkedin.com/learning/making-the-move-from-individual-contributor-to-manager"),
                _course("transition-course-3", "Foundations of Leadership and Management", "Coursera", "Manager essentials", "Useful for grounding the transition in practical techniques for trust, change, and managerial decision-making.", "https://www.coursera.org/learn/foundations-of-leadership-and-management"),
            ],
            "giving-and-receiving-feedback": [
                _course("feedback-course-1", "Leadership through Feedback", "LinkedIn Learning", "Leadership feedback", "A strong end-to-end course on giving and receiving feedback, avoiding bias, and structuring better feedback conversations.", "https://www.linkedin.com/learning/leadership-through-feedback"),
                _course("feedback-course-2", "Giving Feedback", "Coursera", "Constructive feedback", "A practical course focused on communication, coaching, and building stronger feedback habits.", "https://www.coursera.org/learn/givingfeedback"),
                _course("feedback-course-3", "Giving Helpful Feedback", "Coursera", "Helpful communication", "A strong communication-focused course that helps make feedback clearer, more actionable, and more useful.", "https://www.coursera.org/learn/feedback"),
            ],
        }

        enriched_topics = []
        for topic in self._topics:
            extra = topic_map.get(topic.topic_id, {})
            sections = [
                TopicSection(section_id=section_id, title=title, content=content)
                for section_id, title, content in extra.get("sections", [])
            ]
            exercise_items = [
                ExerciseNoteItem(exercise_id=exercise_id, title=title, details=details)
                for exercise_id, title, details in extra.get("exercise_items", [])
            ]
            enriched_topics.append(
                topic.model_copy(
                    update={
                        "sections": sections,
                        "exercise_items": exercise_items,
                        "quiz_questions": quiz_map.get(topic.topic_id, []),
                        "quiz_result_bands": quiz_band_map.get(topic.topic_id, []),
                        "quiz_type": "self-assessment" if topic.topic_id == "leadership-styles" else "knowledge-check",
                        "course_recommendations": course_map.get(topic.topic_id, []),
                        "book_recommendations": book_map.get(topic.topic_id, []),
                    }
                )
            )
        self._topics = enriched_topics

    def _seed_defaults(self) -> None:
        default_users = [
            PortalUser(user_id="leader-alex", name="Alex Leader", role=UserRole.LEADER, email="alex.leader@wisetechglobal.com"),
            PortalUser(user_id="leader-priya", name="Priya Leader", role=UserRole.LEADER, email="priya.leader@wisetechglobal.com"),
            PortalUser(user_id="leader-marcus", name="Marcus Leader", role=UserRole.LEADER, email="marcus.leader@wisetechglobal.com"),
            PortalUser(user_id="admin-sam", name="Sam Administrator", role=UserRole.ADMINISTRATOR, email="sam.admin@wisetechglobal.com"),
            PortalUser(user_id="pl-jordan", name="Jordan People Leadership", role=UserRole.PEOPLE_LEADERSHIP, email="jordan.peopleleadership@wisetechglobal.com"),
        ]
        existing = {user.user_id: user for user in store.list_portal_users()}
        for user in default_users:
            current = existing.get(user.user_id)
            if not current or current.email != user.email or current.name != user.name or current.role != user.role:
                store.upsert_portal_user(user)
        for leader_id in ["leader-alex", "leader-priya", "leader-marcus"]:
            for topic in self._topics:
                store.grant_topic_access(leader_id, topic.topic_id)
        if not store.list_community_threads():
            self._seed_sample_community_threads()

    def _seed_sample_community_threads(self) -> None:
        for thread in self._build_sample_community_threads():
            store.insert_community_thread(thread)

    def list_topics(self) -> list[LeadershipTopic]:
        return self._topics

    def get_topic(self, topic_id: str | None) -> LeadershipTopic:
        if topic_id:
            for topic in self._topics:
                if topic.topic_id == topic_id:
                    return topic
        return self._topics[0]

    def list_users(self) -> list[PortalUser]:
        users = store.list_portal_users()
        if not users:
            self._seed_defaults()
            users = store.list_portal_users()
        return users

    def get_user(self, user_id: str | None) -> PortalUser:
        if user_id:
            user = store.get_portal_user(user_id)
            if user:
                return user
        return self.list_users()[0]

    def leader_user(self) -> PortalUser:
        return self.get_user("leader-alex")

    def administrator_user(self) -> PortalUser:
        return self.get_user("admin-sam")

    def people_leadership_user(self) -> PortalUser:
        return self.get_user("pl-jordan")

    def accessible_topics_for_user(self, user_id: str) -> list[LeadershipTopic]:
        user = store.get_portal_user(user_id)
        if not user:
            return []
        if user.role != UserRole.LEADER:
            return self._topics
        granted = set(store.get_topic_access(user_id))
        return [topic for topic in self._topics if topic.topic_id in granted]

    def search_topics_for_user(self, user_id: str, query: str) -> list[LeadershipTopic]:
        topics = self.accessible_topics_for_user(user_id)
        search = query.strip().lower()
        if not search:
            return topics

        def matches(topic: LeadershipTopic) -> bool:
            haystacks = [
                topic.title,
                topic.summary,
                *topic.topics,
                *topic.examples,
                topic.case_study,
                *(section.title for section in topic.sections),
                *(section.content for section in topic.sections),
                *(item.title for item in topic.exercise_items),
                *(item.details for item in topic.exercise_items),
            ]
            return any(search in (item or "").lower() for item in haystacks)

        return [topic for topic in topics if matches(topic)]

    def add_feedback(self, user_id: str, topic_id: str, rating: int, comments: str) -> LeaderFeedback:
        feedback = LeaderFeedback(
            feedback_id=str(uuid4()),
            user_id=user_id,
            topic_id=topic_id,
            rating=rating,
            comments=comments,
            created_at=utc_now(),
        )
        store.insert_leader_feedback(feedback)
        return feedback

    def submit_question(self, user_id: str, topic_id: str, question: str) -> TopicQuestion:
        submission = TopicQuestion(
            question_id=str(uuid4()),
            user_id=user_id,
            topic_id=topic_id,
            question=question,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        store.insert_topic_question(submission)
        return submission

    def submit_topic_suggestion(self, user_id: str, topic_name: str, details: str, need_description: str) -> TopicSuggestion:
        suggestion = TopicSuggestion(
            suggestion_id=str(uuid4()),
            user_id=user_id,
            topic_name=topic_name,
            details=details,
            need_description=need_description,
            created_at=utc_now(),
        )
        store.insert_topic_suggestion(suggestion)
        return suggestion

    def assign_topic_suggestion(self, suggestion_id: str, assignee_id: str) -> TopicSuggestion | None:
        suggestion = store.get_topic_suggestion(suggestion_id)
        if not suggestion:
            return None
        suggestion.assigned_to = assignee_id
        suggestion.status = SuggestionStatus.ASSIGNED
        store.update_topic_suggestion(suggestion)
        return suggestion

    def approve_topic_suggestion(
        self,
        suggestion_id: str,
        approver_id: str,
        approval_notes: str,
        content_notes: str,
    ) -> TopicSuggestion | None:
        suggestion = store.get_topic_suggestion(suggestion_id)
        if not suggestion:
            return None
        suggestion.approved_by = approver_id
        suggestion.approval_notes = approval_notes
        suggestion.content_notes = content_notes
        suggestion.status = SuggestionStatus.APPROVED
        store.update_topic_suggestion(suggestion)
        return suggestion

    def update_topic_suggestion_content(self, suggestion_id: str, content_notes: str) -> TopicSuggestion | None:
        suggestion = store.get_topic_suggestion(suggestion_id)
        if not suggestion:
            return None
        suggestion.content_notes = content_notes
        store.update_topic_suggestion(suggestion)
        return suggestion

    def grant_access(self, user_id: str, topic_id: str) -> None:
        store.grant_topic_access(user_id, topic_id)

    def assign_question(self, question_id: str, assignee_id: str) -> TopicQuestion | None:
        question = store.get_topic_question(question_id)
        if not question:
            return None
        question.assigned_to = assignee_id
        question.status = QuestionStatus.ASSIGNED
        question.updated_at = utc_now()
        store.update_topic_question(question)
        return question

    def answer_question(self, question_id: str, answer: str) -> TopicQuestion | None:
        question = store.get_topic_question(question_id)
        if not question:
            return None
        question.answer = answer
        question.status = QuestionStatus.ANSWERED
        question.updated_at = utc_now()
        store.update_topic_question(question)
        return question

    def list_feedback(self) -> list[LeaderFeedback]:
        return store.list_leader_feedback()

    def topic_rating_summary(self, topic_id: str) -> dict[str, float | int]:
        feedback_items = [item for item in store.list_leader_feedback() if item.topic_id == topic_id]
        count = len(feedback_items)
        average = round(sum(item.rating for item in feedback_items) / count, 1) if count else 0.0
        return {
            "average": average,
            "count": count,
        }

    def list_questions(self) -> list[TopicQuestion]:
        return store.list_topic_questions()

    def list_topic_suggestions(self) -> list[TopicSuggestion]:
        return store.list_topic_suggestions()

    def list_topic_suggestions_for_assignee(self, assignee_id: str) -> list[TopicSuggestion]:
        return [item for item in self.list_topic_suggestions() if item.assigned_to == assignee_id]

    def get_note(self, user_id: str, topic_id: str, exercise_id: str | None = None) -> LeaderTopicNote | None:
        return store.get_leader_note(user_id, topic_id, exercise_id)

    def save_note(self, user_id: str, topic_id: str, content: str, exercise_id: str | None = None) -> LeaderTopicNote:
        existing = store.get_leader_note(user_id, topic_id, exercise_id)
        note = LeaderTopicNote(
            note_id=existing.note_id if existing else str(uuid4()),
            user_id=user_id,
            topic_id=topic_id,
            exercise_id=exercise_id,
            content=content,
            updated_at=utc_now(),
        )
        store.upsert_leader_note(note)
        return note

    def list_notes_for_user(self, user_id: str) -> list[dict[str, object]]:
        notes: list[dict[str, object]] = []
        topic_lookup = {topic.topic_id: topic for topic in self._topics}
        for topic in self._topics:
            for note in store.list_leader_notes(user_id, topic.topic_id):
                note_type = "Topic note"
                note_title = topic.title
                if note.exercise_id == "case-study":
                    note_type = "Case study reflection"
                    note_title = f"{topic.title} case study"
                elif note.exercise_id:
                    exercise = next((item for item in topic.exercise_items if item.exercise_id == note.exercise_id), None)
                    note_type = "Exercise reflection"
                    note_title = exercise.title if exercise else topic.title
                notes.append(
                    {
                        "note": note,
                        "topic": topic_lookup.get(note.topic_id),
                        "note_type": note_type,
                        "note_title": note_title,
                    }
                )
        return sorted(notes, key=lambda item: item["note"].updated_at, reverse=True)

    def user_activity_dashboard(self, user_id: str) -> dict[str, object]:
        user = self.get_user(user_id)
        topic_lookup = {topic.topic_id: topic for topic in self._topics}
        user_lookup = {member.user_id: member for member in self.list_users()}

        feedback_items = [item for item in self.list_feedback() if item.user_id == user_id]
        questions = [item for item in self.list_questions() if item.user_id == user_id]
        suggestions = [item for item in self.list_topic_suggestions() if item.user_id == user_id]
        notes = self.list_notes_for_user(user_id)
        threads = self.list_community_threads()
        started_threads = [thread for thread in threads if thread.user_id == user_id]
        replied_threads = [thread for thread in threads if any(reply.user_id == user_id for reply in thread.replies)]
        followed_thread_ids = self.followed_thread_ids_for_user(user_id)
        followed_threads = [thread for thread in threads if thread.thread_id in followed_thread_ids]
        supported_threads = [thread for thread in threads if user_id in thread.liked_by]
        liked_replies = [
            {"thread": thread, "reply": reply, "author": user_lookup.get(reply.user_id)}
            for thread in threads
            for reply in thread.replies
            if user_id in reply.liked_by
        ]
        notifications = self.list_notifications_for_user(user_id)
        user_replies = [
            {"thread": thread, "reply": reply}
            for thread in threads
            for reply in thread.replies
            if reply.user_id == user_id
        ]

        recent_activity: list[dict[str, object]] = []
        for note_item in notes:
            note = note_item["note"]
            recent_activity.append(
                {
                    "timestamp": note.updated_at,
                    "label": note_item["note_type"],
                    "title": note_item["note_title"],
                    "detail": note.content[:180],
                    "link": f"/journal?topic_id={note.topic_id}",
                }
            )
        for item in feedback_items:
            topic = topic_lookup.get(item.topic_id)
            recent_activity.append(
                {
                    "timestamp": item.created_at,
                    "label": "Topic rating",
                    "title": topic.title if topic else item.topic_id,
                    "detail": f"Rated {item.rating}/5" + (f" and added feedback: {item.comments[:120]}" if item.comments else ""),
                    "link": f"/journal?topic_id={item.topic_id}",
                }
            )
        for item in questions:
            topic = topic_lookup.get(item.topic_id)
            recent_activity.append(
                {
                    "timestamp": item.updated_at,
                    "label": "Question submitted",
                    "title": topic.title if topic else item.topic_id,
                    "detail": item.question[:180],
                    "link": f"/journal?topic_id={item.topic_id}",
                }
            )
        for item in suggestions:
            recent_activity.append(
                {
                    "timestamp": item.created_at,
                    "label": "Topic suggestion",
                    "title": item.topic_name,
                    "detail": item.need_description[:180],
                    "link": "/",
                }
            )
        for thread in started_threads:
            recent_activity.append(
                {
                    "timestamp": thread.created_at,
                    "label": "Conversation started",
                    "title": thread.title,
                    "detail": thread.content[:180],
                    "link": f"/community?topic_id={thread.topic_id}" if thread.topic_id else "/community",
                }
            )
        for item in user_replies:
            recent_activity.append(
                {
                    "timestamp": item["reply"].created_at,
                    "label": "Reply posted",
                    "title": item["thread"].title,
                    "detail": item["reply"].content[:180],
                    "link": f"/community?topic_id={item['thread'].topic_id}" if item["thread"].topic_id else "/community",
                }
            )

        recent_activity = sorted(recent_activity, key=lambda item: item["timestamp"], reverse=True)[:12]

        summary = {
            "conversations_started": len(started_threads),
            "replies_posted": len(user_replies),
            "topics_rated": len(feedback_items),
            "notes_saved": len(notes),
            "followed_threads": len(followed_threads),
            "notifications_queued": len(notifications),
        }

        contributions = {
            "feedback_items": [
                {"feedback": item, "topic": topic_lookup.get(item.topic_id)}
                for item in feedback_items
            ],
            "questions": [
                {"question": item, "topic": topic_lookup.get(item.topic_id)}
                for item in questions
            ],
            "suggestions": suggestions,
            "supported_threads": supported_threads,
            "liked_replies": liked_replies,
        }

        conversations = {
            "started_threads": started_threads,
            "replied_threads": replied_threads,
            "followed_threads": followed_threads,
            "notifications": notifications[:6],
        }

        return {
            "user": user,
            "summary": summary,
            "notes": notes,
            "conversations": conversations,
            "contributions": contributions,
            "recent_activity": recent_activity,
            "user_lookup": user_lookup,
            "topic_lookup": topic_lookup,
        }

    def list_leader_community_members(self) -> list[PortalUser]:
        return [user for user in self.list_users() if user.role == UserRole.LEADER]

    def _ensure_sample_community_threads(self) -> None:
        existing_titles = {thread.title for thread in store.list_community_threads()}
        for thread in self._build_sample_community_threads():
            if thread.title not in existing_titles:
                store.insert_community_thread(thread)

    def _build_sample_community_threads(self) -> list[CommunityThread]:
        style_thread_id = str(uuid4())
        trust_thread_id = str(uuid4())
        feedback_thread_id = str(uuid4())
        return [
            CommunityThread(
                thread_id=style_thread_id,
                user_id="leader-priya",
                topic_id="leadership-styles",
                title="How are others adapting their leadership style when a strong performer starts slipping?",
                content="I have a team member who is usually very self-directed, but over the last month they have needed much more structure and follow-up. I am trying to work out whether to shift into a more coaching style or get more directive for a while.",
                liked_by=["leader-alex"],
                created_at=utc_now(),
                updated_at=utc_now(),
                replies=[
                    CommunityReply(
                        reply_id=str(uuid4()),
                        thread_id=style_thread_id,
                        user_id="leader-marcus",
                        content="I usually start with a coaching conversation first so I can understand what changed. If the context is personal or workload-related, that often tells me whether more direction or more support is actually needed.",
                        liked_by=["leader-alex"],
                        created_at=utc_now(),
                    ),
                    CommunityReply(
                        reply_id=str(uuid4()),
                        thread_id=style_thread_id,
                        user_id="leader-alex",
                        content="I have found it helps to say explicitly that I am adjusting my style for the moment rather than taking autonomy away permanently. That keeps trust intact while still giving the person more structure.",
                        liked_by=[],
                        created_at=utc_now(),
                    ),
                ],
            ),
            CommunityThread(
                thread_id=trust_thread_id,
                user_id="leader-marcus",
                topic_id="building-trust",
                title="What is one trust-building habit that has worked well in your team?",
                content="I am trying to build more consistency after a busy quarter. I would love practical ideas that are simple enough to repeat every week, not just once-off trust gestures.",
                liked_by=["leader-priya", "leader-alex"],
                created_at=utc_now(),
                updated_at=utc_now(),
                replies=[
                    CommunityReply(
                        reply_id=str(uuid4()),
                        thread_id=trust_thread_id,
                        user_id="leader-priya",
                        content="I now close every one-on-one by repeating back the one commitment I am taking away. It sounds small, but people notice when that action happens before the next check-in.",
                        liked_by=["leader-alex"],
                        created_at=utc_now(),
                    ),
                ],
            ),
            CommunityThread(
                thread_id=feedback_thread_id,
                user_id="leader-alex",
                topic_id="giving-and-receiving-feedback",
                title="How do you keep feedback clear without making the conversation feel heavy?",
                content="I want my feedback conversations to be more useful and less loaded. I am interested in phrasing or structures that help keep the conversation grounded in behaviour and impact.",
                liked_by=["leader-priya"],
                created_at=utc_now(),
                updated_at=utc_now(),
                replies=[
                    CommunityReply(
                        reply_id=str(uuid4()),
                        thread_id=feedback_thread_id,
                        user_id="leader-priya",
                        content="I have started asking permission before I give developmental feedback. It changes the tone immediately and makes the conversation feel more shared than corrective.",
                        liked_by=[],
                        created_at=utc_now(),
                    ),
                    CommunityReply(
                        reply_id=str(uuid4()),
                        thread_id=feedback_thread_id,
                        user_id="leader-marcus",
                        content="I keep coming back to one example, one impact, one next step. That structure stops me from overloading the conversation or drifting into personality language.",
                        liked_by=["leader-alex"],
                        created_at=utc_now(),
                    ),
                ],
            ),
        ]

    def create_community_thread(self, user_id: str, title: str, content: str, topic_id: str | None = None) -> CommunityThread:
        thread = CommunityThread(
            thread_id=str(uuid4()),
            user_id=user_id,
            topic_id=topic_id or None,
            title=title,
            content=content,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        store.insert_community_thread(thread)
        self.follow_thread(thread.thread_id, user_id)
        return thread

    def list_community_threads(self) -> list[CommunityThread]:
        self._ensure_sample_community_threads()
        return store.list_community_threads()

    def search_community_threads(self, query: str, *, topic_id: str | None = None) -> list[CommunityThread]:
        threads = self.list_community_threads()
        if topic_id:
            threads = [thread for thread in threads if thread.topic_id == topic_id]

        search = query.strip().lower()
        if not search:
            return threads

        topic_lookup = {topic.topic_id: topic.title for topic in self._topics}

        def matches(thread: CommunityThread) -> bool:
            haystacks = [
                thread.title,
                thread.content,
                topic_lookup.get(thread.topic_id or "", ""),
                *(reply.content for reply in thread.replies),
            ]
            return any(search in (item or "").lower() for item in haystacks)

        return [thread for thread in threads if matches(thread)]

    def add_community_reply(self, thread_id: str, user_id: str, content: str) -> CommunityThread | None:
        thread = store.get_community_thread(thread_id)
        if not thread:
            return None
        reply = CommunityReply(
            reply_id=str(uuid4()),
            thread_id=thread_id,
            user_id=user_id,
            content=content,
            created_at=utc_now(),
        )
        thread.replies.append(
            reply
        )
        self.follow_thread(thread_id, user_id)
        self._queue_thread_notifications(thread=thread, actor_user_id=user_id, reply=reply)
        thread.updated_at = utc_now()
        store.update_community_thread(thread)
        return thread

    def follow_thread(self, thread_id: str, user_id: str) -> CommunityThreadFollow:
        existing = store.get_community_thread_follow(thread_id, user_id)
        if existing:
            return existing
        follow = CommunityThreadFollow(
            follow_id=str(uuid4()),
            thread_id=thread_id,
            user_id=user_id,
            created_at=utc_now(),
        )
        store.upsert_community_thread_follow(follow)
        return follow

    def unfollow_thread(self, thread_id: str, user_id: str) -> None:
        existing = store.get_community_thread_follow(thread_id, user_id)
        if existing:
            store.delete_community_thread_follow(existing.follow_id)

    def toggle_thread_follow(self, thread_id: str, user_id: str) -> bool:
        existing = store.get_community_thread_follow(thread_id, user_id)
        if existing:
            store.delete_community_thread_follow(existing.follow_id)
            return False
        self.follow_thread(thread_id, user_id)
        return True

    def is_following_thread(self, thread_id: str, user_id: str) -> bool:
        return store.get_community_thread_follow(thread_id, user_id) is not None

    def follower_count(self, thread_id: str) -> int:
        return len([item for item in store.list_community_thread_follows() if item.thread_id == thread_id])

    def followed_thread_ids_for_user(self, user_id: str) -> set[str]:
        return {item.thread_id for item in store.list_community_thread_follows() if item.user_id == user_id}

    def list_notifications_for_user(self, user_id: str) -> list[CommunityNotification]:
        return [item for item in store.list_community_notifications() if item.user_id == user_id]

    def _queue_thread_notifications(self, thread: CommunityThread, actor_user_id: str, reply: CommunityReply) -> None:
        followers = [item for item in store.list_community_thread_follows() if item.thread_id == thread.thread_id]
        actor = store.get_portal_user(actor_user_id)
        actor_name = actor.name if actor else "A leader"
        for follow in followers:
            if follow.user_id == actor_user_id:
                continue
            user = store.get_portal_user(follow.user_id)
            if not user or not user.email:
                continue
            notification = CommunityNotification(
                notification_id=str(uuid4()),
                thread_id=thread.thread_id,
                user_id=follow.user_id,
                destination=user.email,
                subject=f"LeadWise thread update: {thread.title}",
                preview=f"{actor_name} replied: {reply.content[:140]}",
                created_at=utc_now(),
            )
            store.insert_community_notification(notification)

    def toggle_thread_like(self, thread_id: str, user_id: str) -> CommunityThread | None:
        thread = store.get_community_thread(thread_id)
        if not thread:
            return None
        if user_id in thread.liked_by:
            thread.liked_by.remove(user_id)
        else:
            thread.liked_by.append(user_id)
        thread.updated_at = utc_now()
        store.update_community_thread(thread)
        return thread

    def toggle_reply_like(self, thread_id: str, reply_id: str, user_id: str) -> CommunityThread | None:
        thread = store.get_community_thread(thread_id)
        if not thread:
            return None
        for reply in thread.replies:
            if reply.reply_id == reply_id:
                if user_id in reply.liked_by:
                    reply.liked_by.remove(user_id)
                else:
                    reply.liked_by.append(user_id)
                thread.updated_at = utc_now()
                store.update_community_thread(thread)
                return thread
        return None


portal = LeadershipBasicsPortal()
