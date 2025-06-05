import streamlit as st
import openai
from datetime import datetime
import json
import io
import time
from docx import Document
import markdown
import base64
import re

# Page configuration
st.set_page_config(
    page_title="Momentic AI Content Team",
    page_icon="https://cdn.prod.website-files.com/6213ddd7bd3eb80dfdbf1d95/667f2c081ec54c1767cb4265_momentic-favicon-32.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Momentic branding
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #f7f6ed;
    }
    body {font-size:0.875rem!important;}
    li {margin:0!important;}
    
    /* Rounded containers */
    .stForm, .stExpander {
        background-color: #FFFFFF;
        border-radius: 0.75rem;
        padding: 1.25rem 2.25rem;
    }
    
    /* Green accent for buttons */
    .stButton > button {
        background-color: #18ff4e;
        color: #141517;
        border-radius: 1.25rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        opacity: 0.7;
        box-shadow: 0 4px 8px rgba(46, 204, 113, 0.3);
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #141517;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 1.25rem;
        border: 1px solid #141517;
    }
    
    /* Status messages */
    .status-message {
        padding: 1.25rem 2.25rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        background-color: #f7f6ed;
        border-left: 4px solid #c9ff18;
    }
    
    /* Progress bar customization */
    .stProgress > div > div > div > div {
        background-color: #18ff4e;
    }
    
    /* Score badge */
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 1.25rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .score-high {
        background-color: #D4EDDA;
        color: #155724;
    }
    
    .score-medium {
        background-color: #FFF3CD;
        color: #856404;
    }
    
    .score-low {
        background-color: #F8D7DA;
        color: #721C24;
    }

    /* Content preview container */
    .content-preview {
        max-width: 50rem;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_content" not in st.session_state:
    st.session_state.current_content = None
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Strategist": [],
        "Specialist Writer": [],
        "SEO Specialist": [],
        "Head of Content": [],
        "Editor-in-Chief": []
    }
if "last_model" not in st.session_state:
    st.session_state.last_model = "4o"
if "agent_status" not in st.session_state:
    st.session_state.agent_status = {
        "Strategist": "Pending",
        "Specialist Writer": "Pending",
        "SEO Specialist": "Pending",
        "Head of Content": "Pending",
        "Editor-in-Chief": "Pending",
    }

# Model mapping
MODEL_MAP = {
    "4.1": "gpt-4.1-2025-04-14",
    "4o": "gpt-4o-2024-08-06",
    "o3": "o3-2025-04-16"
}

# Enhanced Agent System Prompts

AGENT_PROMPTS = {
    "Strategist": """You are the Lead Content Strategist at Momentic, with deep expertise in B2B SaaS content strategy and technical audience engagement. You've studied how developers and technical decision-makers consume content, and you understand what makes them trust and engage with a brand.

    Your strategic foundation:
    - People trust expertise demonstrated through understanding, not claims
    - Clarity beats cleverness, but depth builds authority
    - Every piece must solve a real problem for a real person
    - Great content feels like advice from a helpful, knowledgeable colleague
    
    Strategic approach:
    - Analyze the target audience's specific pain points, technical sophistication, and decision-making criteria
    - Identify the unique angle that will differentiate this content from generic tech content
    - Map content to the buyer's journey stage and specific use cases
    - Balance immediate practical value with long-term thought leadership
    
    Deliverables:
    1) **Refined Title**: Create 3 title variations - one SEO-optimized, one curiosity-driven, one value-focused. Recommend the best.
    2) **Strategic Positioning**: Define the content's unique angle, key differentiators, and competitive advantage
    3) **Detailed Content Architecture**:
       - Hook strategy (first 150 words that earn attention)
       - Section flow with smooth transition logic
       - Information density distribution (where to go deep vs. high-level)
       - Engagement tactics (examples, visuals, interactive elements)
    4) **Voice & Tone Blueprint**:
       - Technical sophistication level (1-5 scale with specific markers)
       - Professional yet human tone balance
       - Trust-building credibility markers
       - Common pitfalls to avoid (buzzwords, jargon, condescension)
    
    Remember: You're setting up the team for success. Be specific, practical, and always keep the reader's needs at the center.

When you finish, add a section titled 'Recommended Next Steps:' followed by a bullet list of actionable suggestions.""",
    
    "Specialist Writer": """You are Momentic's Senior Technical Content Writer, specializing in making complex technical concepts accessible without dumbing them down. You have a background in software development and understand that great technical writing respects the reader's intelligence while ensuring clarity.

    Your writing principles:
    - Start with a hook that shows you understand the reader's world
    - Use the "show, then tell" approach - concrete examples before abstract concepts
    - Write like a helpful colleague, not a textbook
    - Build narrative momentum even in technical content
    - Every paragraph should make the reader want the next one
    
    Writing approach:
    1) **Opening**: Craft a first paragraph that immediately demonstrates value and understanding
    2) **Structure**: Follow the strategic outline while maintaining natural, conversational flow
    3) **Technical Depth**: Include enough detail to be genuinely useful, not just informative
    4) **Engagement**: Vary paragraph lengths, ask strategic questions, reveal insights progressively
    5) **Evidence**: Support all claims with specific examples, real data, or concrete scenarios
    6) **Conclusion**: End with actionable next steps, not just summary
    
    Style guidelines:
    - Active voice unless passive serves clarity
    - Short sentences for key points, longer for context
    - Explain technical terms inline without condescension
    - Professional but conversational - like explaining to a smart colleague
    - Use "you" to speak directly to the reader
    - Avoid buzzwords and corporate jargon entirely
    
    Your goal: Create content that a senior developer would actually bookmark and share with their team.

When you finish, add a section titled 'Recommended Next Steps:' followed by a bullet list of actionable suggestions.""",
        
    "SEO Specialist": """You are Aurora-SEO at Momentic, a future-proof search strategist and relevance engineer specializing in driving organic impact across classic SERPs and AI surfaces (AI Overviews, AI Mode, ChatGPT, Perplexity).
    
    Core Identity:
    - Mission: Drive measurable organic impact across traditional and AI-powered search surfaces
    - Mindset: Treat search as a probabilistic system governed by LLM reasoning chains, not just keyword matching
    - Ethic: Prioritize user trust, factual accuracy, and long-term brand equity
    
    Your RAISE-R Workflow:
    1) **Request-clarify**: Understand the content's goal and target metrics
    2) **Audit current surface**: Analyze SERP/AI Mode snapshots and competing passages
    3) **Infer fan-out landscape**: Generate 6+ synthetic queries spanning related, comparative, and entity-expanded types
    4) **Score semantic gaps**: Identify where content fails to align with search intent
    5) **Engineer relevance**: Optimize for both traditional SEO and AI snippet capture
    6) **Review & report**: Provide actionable improvements with expected impact
    
    Optimization Approach:
    - **Snippet Sculpting**: Position key value props in first 160 characters for AI snippet capture
    - **Semantic Structure**: Create modular chunks that answer in <320 chars with clear entity anchors
    - **Multi-modal Optimization**: Ensure images, videos, and code blocks reinforce main claims
    - **Citation Engineering**: Structure content to maximize AI system citations
    - **Zero-Click Strategy**: Optimize for influence even without direct clicks
    
    Technical Implementation:
    - Natural keyword integration that serves user intent
    - Structured data only when genuinely helpful
    - Passage indexing optimization for AI retrieval
    - Clear entity linking and semantic triples
    - Accessibility compliance (alt text, ARIA landmarks)
    
    Output Requirements:
    - Concise, actionable recommendations
    - Bullet points over prose
    - Flag uncertainty rather than fabricate metrics
    - Include measurement hooks for citation frequency and answer prominence
    
    Never sacrifice readability for traditional SEO metrics. The best content serves users first and search engines second.

When you finish, add a section titled 'Recommended Next Steps:' followed by a bullet list of actionable suggestions.""",
    
    "Head of Content": """You are Momentic's Head of Content with 15+ years in B2B tech content leadership. You've built content programs that establish market authority while driving real business results. You review content through both strategic and practical lenses.

    Your review framework:
    
    **Strategic Alignment**:
    - Does this reinforce Momentic's position as a trusted technical authority?
    - Are we demonstrating genuine expertise without arrogance?
    - Is our unique perspective coming through clearly?
    - Will this content build long-term brand equity?
    
    **Reader Value**:
    - Does every section deliver on the title's promise?
    - Are we solving a real problem or just adding noise?
    - Is the advice practical and actionable?
    - Would our target reader thank us for this content?
    
    **Message Clarity**:
    - Are key points impossible to miss?
    - Do we address likely objections naturally?
    - Is our value proposition clear but not heavy-handed?
    - Are transitions smooth and logical?
    
    **Quality Standards**:
    - All claims substantiated with evidence
    - Technical accuracy verified
    - Consistent voice that builds trust
    - Polish that reflects our standards
    
    Enhancement priorities:
    1) Strengthen weak arguments with better evidence or remove them
    2) Amplify unique insights only Momentic could provide
    3) Ensure voice consistency - helpful colleague, not salesperson
    4) Add CTAs that feel genuinely helpful, never pushy
    5) Polish for memorability - what's the one thing readers will remember?
    
    Your goal: Elevate good content to exceptional. Make it something you'd be proud to put your name on.

When you finish, add a section titled 'Recommended Next Steps:' followed by a bullet list of actionable suggestions.""",
    
    "Editor-in-Chief": """You are Momentic's Editor-in-Chief, the final guardian of content quality and brand reputation. You've edited thousands of technical articles and have developed an instinct for what truly serves technical audiences.

    Your review criteria:
    
    **Technical Excellence** (0-10):
    - Accuracy of all technical claims
    - Appropriate depth without overwhelming
    - Quality of code examples and demonstrations
    - Logical flow of technical arguments
    
    **Reader Value** (0-10):
    - Does the hook immediately demonstrate understanding?
    - Consistent value delivery throughout
    - Practical, actionable insights
    - Memorable takeaways they'll actually use
    
    **Brand Building** (0-10):
    - Strengthens Momentic's authority authentically
    - Clear differentiation from generic content
    - Builds trust through demonstrated expertise
    - Advances our thought leadership naturally
    
    **Professional Polish** (0-10):
    - Grammar and style consistency
    - Clarity of expression throughout
    - Appropriate professional tone
    - Ready for publication without embarrassment
    
    Non-negotiable standards:
    - No unsubstantiated claims
    - No buzzword bingo or corporate jargon
    - No condescension or oversimplification
    - No SEO tactics that hurt readability
    - No generic insights anyone could write
    
    Provide your verdict:
    APPROVAL: [Approved/Needs Minor Revision/Needs Major Revision]
    OVERALL_SCORE: [X/40]
    BREAKDOWN: Technical: [X/10] | Value: [X/10] | Brand: [X/10] | Polish: [X/10]
    
    STANDOUT STRENGTHS:
    - [What makes this exceptional]
    
    REVISION REQUIREMENTS:
    - [Specific issues that must be fixed]
    
    STRATEGIC IMPACT:
    - [How this advances our content goals]
    
    FINAL_TITLE: [The polished, publication-ready title]
    FINAL_SLUG: [SEO-optimized URL slug]
    
    Editor's instinct: Would YOU save this article? Would you share it with a colleague?

When you finish, add a section titled 'Recommended Next Steps:' followed by a bullet list of actionable suggestions."""
}

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            # Note: In production, you'd use PyPDF2 or pdfplumber
            return "PDF content extraction would go here"
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Note: In production, you'd properly extract from DOCX
            return "DOCX content extraction would go here"
        else:
            return "Unsupported file type"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def call_agent(agent_name, prompt, model, api_key, context=""):
    """Make API call to OpenAI for an agent"""
    try:
        openai.api_key = api_key
        
        messages = [
            {"role": "system", "content": AGENT_PROMPTS[agent_name]},
            {"role": "user", "content": f"{context}\n\n{prompt}"}
        ]
        
        response = openai.ChatCompletion.create(
            model=MODEL_MAP[model],
            messages=messages,
            temperature=0.7,
            max_tokens=10000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling {agent_name}: {str(e)}")
        return None

def parse_next_steps(output):
    """Split agent output into main content and bullet list of next steps"""
    if "Recommended Next Steps:" in output:
        content, steps_part = output.split("Recommended Next Steps:", 1)
        steps = [
            line.strip("- ").strip()
            for line in steps_part.strip().splitlines()
            if line.strip().startswith("-")
        ]
        return content.strip(), steps
    return output.strip(), []

def parse_queries(text: str) -> list[str]:
    """Extract search queries from SEO Specialist output."""

    queries: list[str] = []
    bullet_pattern = re.compile(r"^\s*(?:[-*]|\d+\.)\s*(.+)")

    for line in text.splitlines():
        match = bullet_pattern.match(line.strip())
        if match:
            query = match.group(1).strip()
            if query:
                queries.append(query)

    return queries



def refresh_current_session(placeholder):
    """Update the sidebar session info with agent statuses."""
    placeholder.empty()
    with placeholder.container():

        st.markdown("### Current Session")
        if st.session_state.get("current_content"):
            st.markdown(f"**Title:** {st.session_state.current_content.get('final_title', 'N/A')}")
            st.markdown(f"**Score:** {st.session_state.current_content.get('score', 'N/A')}")
            st.markdown(f"**Status:** {st.session_state.current_content.get('approval', 'N/A')}")
        st.markdown("#### Agent Status")
        for agent, status in st.session_state.agent_status.items():
            st.markdown(f"- **{agent}**: {status}")

def run_content_pipeline(inputs, model, api_key, status_container, progress_bar, session_placeholder):
    """Run the full 5-agent content creation pipeline

    Parameters
    ----------
    status_container : st.container
        Sidebar container used to display stage status messages.

    session_placeholder : st.empty
        Sidebar placeholder showing current session details.
    """
    
    # Extract inputs
    content_type = inputs["content_type"]
    topic = inputs["topic"]
    audience = inputs["audience"]
    length = inputs["length"]
    key_messages = inputs["key_messages"]
    brand_voice = inputs["brand_voice"]
    keywords = inputs["keywords"]
    compliance = inputs["compliance"]
    references = inputs["references"]
    results = {}
    next_steps = {}

    st.session_state.current_content = {}
    for agent in st.session_state.agent_status:
        st.session_state.agent_status[agent] = "Queued"

    refresh_current_session(session_placeholder)
    
    # Stage 1: Strategist
    start_time = datetime.now()
    st.session_state.agent_status["Strategist"] = "In progress"

    refresh_current_session(session_placeholder)

    status_container.info(f"🎯 {start_time:%H:%M:%S} - **Strategist** is planning content strategy...")
    
    strategist_prompt = f"""
    Content Type: {content_type}
    Topic: {topic}
    Target Audience: {audience}
    Length: {length}
    Key Messages: {key_messages}
    Brand Voice: {brand_voice or 'Professional, data-driven, friendly'}
    Reference Materials: {references[:500] + '...' if len(references) > 500 else references}
    
    Create a comprehensive content strategy with outline.
    """
    
    strategy_raw = call_agent("Strategist", strategist_prompt, model, api_key)
    if not strategy_raw:
        return None
    strategy, steps = parse_next_steps(strategy_raw)
    results["strategy"] = strategy
    st.session_state.current_content["strategy"] = strategy
    next_steps["Strategist"] = steps
    st.session_state.agent_status["Strategist"] = "Completed"
    refresh_current_session(session_placeholder)

    progress_bar.progress(0.2)
    
    # Stage 2: Specialist Writer
    st.session_state.agent_status["Specialist Writer"] = "In progress"
    refresh_current_session(session_placeholder)
    status_container.info(f"✍️ {datetime.now():%H:%M:%S} - **Specialist Writer** is drafting content...")
    
    writer_prompt = f"""
    Based on this strategy:
    {strategy}
    
    Write the full content for a {content_type} about {topic}.
    Target audience: {audience}
    Length: {length}
    Key messages to include: {key_messages}
    Voice: {brand_voice or 'Professional, data-driven, friendly'}
    """
    
    draft_raw = call_agent("Specialist Writer", writer_prompt, model, api_key)
    if not draft_raw:
        return None
    draft, steps = parse_next_steps(draft_raw)
    results["draft"] = draft
    st.session_state.current_content["draft"] = draft
    next_steps["Specialist Writer"] = steps
    st.session_state.agent_status["Specialist Writer"] = "Completed"
    refresh_current_session(session_placeholder)
    progress_bar.progress(0.4)
    
    # Stage 3: SEO Specialist
    st.session_state.agent_status["SEO Specialist"] = "In progress"
    refresh_current_session(session_placeholder)
    status_container.info(f"🔍 {datetime.now():%H:%M:%S} - **SEO Specialist** is optimizing for search...")
    
    seo_prompt = f"""
    Optimize this content for SEO. Keywords to target: {keywords}
    
    Content to optimize:
    {draft}
    
    Return the full content with SEO improvements applied.
    """
    
    seo_raw = call_agent("SEO Specialist", seo_prompt, model, api_key)
    if not seo_raw:
        return None
    seo_content, steps = parse_next_steps(seo_raw)
    results["seo_content"] = seo_content
    st.session_state.current_content["seo_content"] = seo_content
    results["queries"] = parse_queries(seo_content)
    next_steps["SEO Specialist"] = steps
    st.session_state.agent_status["SEO Specialist"] = "Completed"
    refresh_current_session(session_placeholder)
    progress_bar.progress(0.6)
    
    # Stage 4: Head of Content
    st.session_state.agent_status["Head of Content"] = "In progress"
    refresh_current_session(session_placeholder)
    status_container.info(f"📝 {datetime.now():%H:%M:%S} - **Head of Content** is refining for brand alignment...")
    
    head_prompt = f"""
    Refine this content for brand alignment and compliance.
    Brand voice: {brand_voice or 'Professional, data-driven, friendly'}
    Compliance requirements: {compliance}
    
    Content to refine:
    {seo_content}
    
    Return the full refined content.
    """
    
    polished_raw = call_agent("Head of Content", head_prompt, model, api_key)
    if not polished_raw:
        return None
    polished, steps = parse_next_steps(polished_raw)
    results["polished"] = polished
    st.session_state.current_content["polished"] = polished
    next_steps["Head of Content"] = steps
    st.session_state.agent_status["Head of Content"] = "Completed"
    refresh_current_session(session_placeholder)
    progress_bar.progress(0.8)
    
    # Stage 5: Editor-in-Chief
    st.session_state.agent_status["Editor-in-Chief"] = "In progress"
    refresh_current_session(session_placeholder)
    status_container.info(f"✅ {datetime.now():%H:%M:%S} - **Editor-in-Chief** is reviewing for final approval...")
    
    editor_prompt = f"""
    Review this final content for approval.
    Original topic: {topic}
    Content type: {content_type}
    
    Content to review:
    {polished}
    """
    
    editor_raw = call_agent("Editor-in-Chief", editor_prompt, model, api_key)
    if not editor_raw:
        return None
    editor_review, steps = parse_next_steps(editor_raw)
    results["editor_review"] = editor_review
    st.session_state.current_content["editor_review"] = editor_review
    next_steps["Editor-in-Chief"] = steps
    st.session_state.agent_status["Editor-in-Chief"] = "Completed"
    refresh_current_session(session_placeholder)
    progress_bar.progress(1.0)
    
    # Parse editor review
    try:
        lines = editor_review.split('\n')
        approval = "Approved"
        score = "8/10"
        comments = ""
        final_title = topic
        
        for line in lines:
            if "APPROVAL:" in line:
                approval = line.split("APPROVAL:")[1].strip()
            elif "SCORE:" in line:
                score = line.split("SCORE:")[1].strip()
            elif "COMMENTS:" in line:
                comments = line.split("COMMENTS:")[1].strip()
            elif "FINAL_TITLE:" in line:
                final_title = line.split("FINAL_TITLE:")[1].strip()
        
        results["approval"] = approval
        results["score"] = score
        results["comments"] = comments
        results["final_title"] = final_title
        results["final_content"] = polished
        results["next_steps"] = next_steps
        
    except:
        results["approval"] = "Approved"
        results["score"] = "8/10"
        results["comments"] = "Content meets quality standards."
        results["final_title"] = topic
        results["final_content"] = polished
        results["next_steps"] = next_steps
    
    status_container.success(f"✨ {datetime.now():%H:%M:%S} - Content generation complete!")
    refresh_current_session(session_placeholder)
    
    return results

def apply_revision(content, feedback, model, api_key):
    """Apply user feedback to revise content"""
    
    revision_prompt = f"""
    Apply the following user feedback to revise this content:
    
    Feedback: {feedback}
    
    Current content:
    {content}
    
    Provide the full revised content and then add:
    APPROVAL: [Approved/Needs Revision]
    SCORE: [X/10]
    """
    
    revised = call_agent("Editor-in-Chief", revision_prompt, model, api_key)
    
    if revised:
        # Parse the response
        content_parts = revised.split("APPROVAL:")
        revised_content = content_parts[0].strip()
        
        approval = "Approved"
        score = "9/10"
        
        if len(content_parts) > 1:
            meta_parts = content_parts[1]
            if "Approved" in meta_parts:
                approval = "Approved"
            elif "Needs Revision" in meta_parts:
                approval = "Needs Revision"
            
            if "SCORE:" in meta_parts:
                score = meta_parts.split("SCORE:")[1].strip().split('\n')[0]
        
        return {
            "content": revised_content,
            "approval": approval,
            "score": score
        }
    
    return None

def create_download_button(content, filename, button_text, file_format):
    """Create download button for different file formats"""

    if file_format == "md":
        st.download_button(
            label=button_text,
            data=content,
            file_name=filename,
            mime="text/markdown",
        )

    elif file_format == "html":
        html_content = markdown.markdown(content)
        full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{filename}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1, h2, h3 {{ color: #333; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        st.download_button(
            label=button_text,
            data=full_html,
            file_name=filename,
            mime="text/html",
        )

    elif file_format == "json":
        json_content = json.dumps(content, indent=2)
        st.download_button(
            label=button_text,
            data=json_content,
            file_name=filename,
            mime="application/json",
        )

def display_generated_content(results, model, api_key, session_placeholder):
    """Display generated content and enable revision workflow

    Parameters
    ----------
    session_placeholder : st.empty
        Sidebar placeholder used to show session details
    """
    st.markdown("---")
    st.markdown("## Generated Content")

    # Title
    st.markdown(f"### {results['final_title']}")

    # Status and score
    col1, col2 = st.columns([1, 3])
    with col1:
        score_value = int(results['score'].split('/')[0])
        score_class = "high" if score_value >= 8 else "medium" if score_value >= 6 else "low"
        st.markdown(
            f'<div class="score-badge score-{score_class}">Score: {results["score"]}</div>',
            unsafe_allow_html=True
        )

        if results['approval'] == "Approved":
            st.success(f" {results['approval']}")
        else:
            st.warning(f" {results['approval']}")

    with col2:
        if results.get('comments'):
            st.info(f"💭 Editor's Note: {results['comments']}")

    # Content preview and downloads
    with st.container():
        st.markdown('<div class="content-preview">', unsafe_allow_html=True)

        with st.expander(" View Full Content", expanded=True):
            st.markdown(results['final_content'])
            
        if results.get('queries'):
            st.markdown("### Suggested Search Queries")
            for q in results['queries']:
                st.markdown(f"- {q}")

            dot = "digraph G {root [label=\"" + results['final_title'] + "\"];"
            for i, q in enumerate(results['queries']):
                node = f"q{i}"
                dot += f"root -> {node}; {node} [label=\"{q}\"];"
            dot += "}"
            st.graphviz_chart(dot)

        st.markdown("### Download Content")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            create_download_button(
                results['final_content'],
                f"{results['final_title'].replace(' ', '_')}.md",
                "Markdown",
                "md"
            )

        with col2:
            create_download_button(
                results['final_content'],
                f"{results['final_title'].replace(' ', '_')}.html",
                "HTML",
                "html"
            )

        with col3:
            # Note: DOCX requires python-docx - simplified for demo
            st.button("Word (.docx)", disabled=True, help="Coming soon")

        with col4:
            # Note: PDF requires additional libraries - simplified for demo
            st.button("PDF", disabled=True, help="Coming soon")

        with col5:
            create_download_button(
                results,
                f"{results['final_title'].replace(' ', '_')}.json",
                "JSON",
                "json"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Revision section
    st.markdown("### Request Updates")
    with st.form("revision_form"):
        selected_steps = []
        st.markdown("#### Recommended Next Steps")
        if results.get('next_steps'):
            for agent, steps in results['next_steps'].items():
                if steps:
                    st.markdown(f"**{agent}**")
                    for i, step in enumerate(steps):
                        if st.checkbox(step, key=f"{agent}_{i}"):
                            selected_steps.append(step)

        feedback_extra = st.text_area(
            "Additional instructions",
            placeholder="Add any extra notes...",
        )

        if st.form_submit_button("Request updates"):
            compiled = "\n".join(selected_steps)
            if feedback_extra:
                compiled = compiled + ("\n" if compiled else "") + feedback_extra
            if compiled:
                with st.spinner("Applying your revisions..."):
                    revision_result = apply_revision(
                        results['final_content'],
                        compiled,
                        model,
                        api_key
                    )

                    if revision_result:
                        # Update current content
                        st.session_state.current_content['final_content'] = revision_result['content']
                        st.session_state.current_content['approval'] = revision_result['approval']
                        st.session_state.current_content['score'] = revision_result['score']

                        # Add to history
                        st.session_state.history.append({
                            "version": len(st.session_state.history) + 1,
                            "timestamp": datetime.now().isoformat(),
                            "revision_feedback": compiled,
                            "results": st.session_state.current_content.copy()
                        })

                        refresh_current_session(session_placeholder)

                        st.success("Revisions applied successfully!")
                        st.experimental_rerun()

# Main app
def main():
    st.title("Momentic AI Content Team")
    st.markdown("Your virtual team of AI content specialists")
    
    # Sidebar for API key
    with st.sidebar:
        st.markdown("### Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", help="Your API key is not stored")

        session_placeholder = st.empty()
        refresh_current_session(session_placeholder)

        # Container to display pipeline status messages
        status_container = st.container()

        chat_box = st.expander("💬 Chat with AI Agents", expanded=True)

        with chat_box:
            if not api_key:
                st.warning("Please enter your OpenAI API key to use agent chat.")
            elif not st.session_state.current_content:
                st.info("Generate content first to chat with the AI agents about it.")
            else:
                selected_agent = st.selectbox(
                    "Select an agent to chat with:",
                    ["Strategist", "Specialist Writer", "SEO Specialist", "Head of Content", "Editor-in-Chief"],
                    key="chat_agent_select"
                )

                chat_container = st.container()
                with chat_container:
                    for message in st.session_state.chats[selected_agent]:
                        if message["role"] == "user":
                            st.chat_message("user").markdown(message["content"])
                        else:
                            st.chat_message("assistant").markdown(message["content"])

                user_input = st.chat_input(f"Ask {selected_agent} a question...", key="sidebar_chat_input")

                if user_input:
                    st.session_state.chats[selected_agent].append({"role": "user", "content": user_input})
                    with st.spinner(f"{selected_agent} is thinking..."):
                        context = f"""
                        Current content being discussed:
                        Title: {st.session_state.current_content.get('final_title', 'N/A')}
                        Score: {st.session_state.current_content.get('score', 'N/A')}

                        Content preview:
                        {st.session_state.current_content.get('final_content', '')[:500]}...
                        """
                        response = call_agent(selected_agent, user_input, st.session_state.last_model, api_key, context)

                        if response:
                            st.session_state.chats[selected_agent].append({"role": "assistant", "content": response})
                            st.experimental_rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["Create Content", "Version History", "Help"])

    
    with tab1:
        if not api_key:
            st.warning("👈 Please enter your OpenAI API key in the sidebar to begin.")
            return
        
        # Content request form
        with st.form("content_request"):
            st.markdown("### Content Request Form")
            
            col1, col2 = st.columns(2)
            
            with col1:
                content_type = st.selectbox(
                    "Content Type",
                    ["Blog Post", "Social Media Caption", "Email Newsletter", "Press Release", "Product Description", "Landing Page Copy"]
                )
                
                topic = st.text_input(
                    "Topic/Title",
                    placeholder="e.g., Benefits of Sustainable Packaging"
                )
                
                audience = st.text_input(
                    "Target Audience",
                    placeholder="e.g., Tech-savvy consumers aged 20-30"
                )
                
                length = st.selectbox(
                    "Content Length",
                    ["Short (~300 words)", "Medium (600-800 words)", "Long (1200+ words)"]
                )
            
            with col2:
                model = st.selectbox(
                    "AI Model",
                    ["4.1", "4o", "o3"],
                    index=1
                )
                st.session_state.last_model = model
                
                keywords = st.text_input(
                    "SEO Keywords (comma-separated)",
                    placeholder="e.g., sustainable packaging, eco-friendly"
                )
                
                brand_voice = st.text_input(
                    "Brand Voice Override (optional)",
                    placeholder="e.g., Casual and humorous"
                )
                
                compliance = st.text_input(
                    "Compliance Requirements",
                    placeholder="e.g., No medical claims"
                )
            
            key_messages = st.text_area(
                "Key Messages/Points",
                placeholder="List the main points that must be included...",
                height=100
            )
            
            uploaded_files = st.file_uploader(
                "Reference Materials (optional)",
                accept_multiple_files=True,
                type=['txt', 'pdf', 'docx', 'md']
            )
            
            submitted = st.form_submit_button("Get started, team!", use_container_width=True)
        
        # Process form submission
        if submitted and topic:
            # Process uploaded files
            references = ""
            if uploaded_files:
                for file in uploaded_files:
                    references += f"\n\n--- {file.name} ---\n"
                    references += extract_text_from_file(file)
            
            # Prepare inputs
            inputs = {
                "content_type": content_type,
                "topic": topic,
                "audience": audience,
                "length": length,
                "key_messages": key_messages,
                "brand_voice": brand_voice,
                "keywords": keywords,
                "compliance": compliance,
                "references": references
            }
            
            # Create containers for status and progress
            status_container.empty()
            progress_bar = st.progress(0)
            
            # Run the pipeline
            results = run_content_pipeline(inputs, model, api_key, status_container, progress_bar, session_placeholder)

            if results:
                # Store in session state
                st.session_state.current_content = results.copy()
                st.session_state.history.append({
                    "version": len(st.session_state.history) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "inputs": inputs,
                    "results": st.session_state.current_content.copy()
                })
                
                display_generated_content(results, model, api_key, session_placeholder)
        elif st.session_state.current_content:
            display_generated_content(st.session_state.current_content, model, api_key, session_placeholder)
    
        if not api_key:
            st.warning("Please enter your OpenAI API key to use agent chat.")
            return
            
        st.markdown("### 💬 Talk with the team")
        
        if not st.session_state.current_content:
            st.info("Generate content first to talk with the team about it.")
            return
        
        # Agent selector
        selected_agent = st.selectbox(
            "Select an agent to chat with:",
            ["Strategist", "Specialist Writer", "SEO Specialist", "Head of Content", "Editor-in-Chief"]
        )
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chats[selected_agent]:
                if message["role"] == "user":
                    st.chat_message("user").markdown(message["content"])
                else:
                    st.chat_message("assistant").markdown(message["content"])
        
        # Chat input
        user_input = st.chat_input(f"Ask {selected_agent} a question...")
        
        if user_input:
            # Add user message to history
            st.session_state.chats[selected_agent].append({
                "role": "user",
                "content": user_input
            })
            
            # Get agent response
            with st.spinner(f"{selected_agent} is thinking..."):
                # Build context
                context = f"""
                Current content being discussed:
                Title: {st.session_state.current_content.get('final_title', 'N/A')}
                Score: {st.session_state.current_content.get('score', 'N/A')}
                
                Content preview:
                {st.session_state.current_content.get('final_content', '')[:500]}...
                """
                
                # Call agent
                response = call_agent(selected_agent, user_input, model, api_key, context)
                
                if response:
                    st.session_state.chats[selected_agent].append({
                        "role": "assistant",
                        "content": response
                    })
                    st.experimental_rerun()

    with tab2:
        st.markdown("### Content History")
        
        if not st.session_state.history:
            st.info("No content history yet. Generate some content to see version history.")
            return
        
        # Display versions in reverse chronological order
        for i, version in enumerate(reversed(st.session_state.history)):
            version_num = len(st.session_state.history) - i
            timestamp = datetime.fromisoformat(version['timestamp'])
            
            with st.expander(f"Version {version_num} - {timestamp:%Y-%m-%d %H:%M:%S}"):
                if 'revision_feedback' in version:
                    st.markdown(f"**Revision Applied:** {version['revision_feedback']}")
                
                st.markdown(f"**Title:** {version['results'].get('final_title', 'N/A')}")
                st.markdown(f"**Score:** {version['results'].get('score', 'N/A')}")
                st.markdown(f"**Status:** {version['results'].get('approval', 'N/A')}")
                
                if version['results'].get('comments'):
                    st.markdown(f"**Editor Comments:** {version['results']['comments']}")
                
                st.markdown("**Content Preview:**")
                st.markdown(version['results'].get('final_content', '')[:500] + "...")
                
                # Stage outputs (if available)
                if st.checkbox(f"Show detailed stage outputs for Version {version_num}"):
                    if 'strategy' in version['results']:
                        st.markdown("**Strategist Output:**")
                        st.text(version['results']['strategy'])

                    if 'draft' in version['results']:
                        st.markdown("**Draft Content:**")
                        st.text(version['results']['draft'])

                    if 'seo_content' in version['results']:
                        st.markdown("**SEO Optimized Content:**")
                        st.text(version['results']['seo_content'])

                    if 'polished' in version['results']:
                        st.markdown("**Refined Content:**")
                        st.text(version['results']['polished'])

                    if 'editor_review' in version['results']:
                        st.markdown("**Editor Review:**")
                        st.text(version['results']['editor_review'])
    
    with tab3:
        st.markdown("""
        ### Getting Started
        
        1. **Enter your OpenAI API Key** in the sidebar (it's not stored)
        2. **Fill out the content request form** with your requirements
        3. **Select an AI model** (GPT-4 recommended for best quality)
        4. **Click Generate Content** and watch your AI team work!
        
        ### The AI Team
        
        Your content goes through 5 specialist AI agents:
        
        1. **Strategist** - Plans the content strategy and outline
        2. **Specialist Writer** - Drafts the full content
        3. **SEO Specialist** - Optimizes for search engines
        4. **Head of Content** - Ensures brand alignment
        5. **Editor-in-Chief** - Final review and approval
        
        ### Tips for Best Results
        
        - Be specific with your topic and key messages
        - Include relevant keywords for SEO optimization
        - Upload reference materials for more accurate content
        - Use the revision feature to fine-tune the output
        - Talk with the team members for detailed insights
        
        """)

if __name__ == "__main__":
    main()
