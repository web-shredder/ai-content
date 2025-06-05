import streamlit as st
import openai
from datetime import datetime
import json
import io
import time
from docx import Document
import markdown
import base64

# Page configuration
st.set_page_config(
    page_title="Momentic AI Content Team",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Momentic branding
st.markdown("""
<style>
    /* Main theme colors */
    .stApp {
        background-color: #FDFDFB;
    }
    
    /* Rounded containers */
    .stForm, .stExpander {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Green accent for buttons */
    .stButton > button {
        background-color: #2ECC71;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #27AE60;
        box-shadow: 0 4px 8px rgba(46, 204, 113, 0.3);
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #000000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
    
    /* Status messages */
    .status-message {
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        background-color: #F8F9FA;
        border-left: 4px solid #2ECC71;
    }
    
    /* Progress bar customization */
    .stProgress > div > div > div > div {
        background-color: #2ECC71;
    }
    
    /* Score badge */
    .score-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        margin: 10px 0;
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

# Model mapping
MODEL_MAP = {
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
    "GPT-4.0": "gpt-4",
    "GPT-4.1": "gpt-4-turbo",
    "GPT-4.5": "gpt-4o"
}

# Agent system prompts
AGENT_PROMPTS = {
    "Strategist": """You are an AI Content Strategist at Momentic. Your role is to develop content strategy ensuring it meets audience needs and includes key messages. 
    Provide: 1) A refined title, 2) A detailed content outline with sections, 3) Strategic angle and narrative approach, 4) Tone and voice recommendations.
    Format your response clearly with labeled sections.""",
    
    "Specialist Writer": """You are an AI Content Writer at Momentic. Given the strategy and outline, write a full, engaging draft following the provided structure. 
    Write in the specified tone and voice, incorporating all key messages naturally. Create compelling, well-structured content with proper markdown formatting.""",
    
    "SEO Specialist": """You are an AI SEO Specialist at Momentic. Optimize the content for search engines without changing the core message. 
    Integrate keywords naturally, ensure proper heading structure, suggest meta descriptions, and improve SEO elements. Return the full optimized content.""",
    
    "Head of Content": """You are the Head of Content at Momentic. Polish the draft for brand alignment, flow, and compliance. 
    Ensure tone consistency, emphasize key messages, check compliance requirements, and improve overall structure. Return the full refined content.""",
    
    "Editor-in-Chief": """You are the Editor-in-Chief at Momentic. Review the content for final approval. 
    Check: grammar, clarity, engagement, accuracy, SEO, compliance.
    Provide your verdict in this exact format:
    APPROVAL: [Approved/Needs Revision]
    SCORE: [X/10]
    COMMENTS: [Your detailed feedback]
    FINAL_TITLE: [The final recommended title]"""
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
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling {agent_name}: {str(e)}")
        return None

def run_content_pipeline(inputs, model, api_key, status_container, progress_bar):
    """Run the full 5-agent content creation pipeline"""
    
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
    
    # Stage 1: Strategist
    start_time = datetime.now()
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
    
    strategy = call_agent("Strategist", strategist_prompt, model, api_key)
    if not strategy:
        return None
    
    results["strategy"] = strategy
    progress_bar.progress(0.2)
    
    # Stage 2: Specialist Writer
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
    
    draft = call_agent("Specialist Writer", writer_prompt, model, api_key)
    if not draft:
        return None
    
    results["draft"] = draft
    progress_bar.progress(0.4)
    
    # Stage 3: SEO Specialist
    status_container.info(f"🔍 {datetime.now():%H:%M:%S} - **SEO Specialist** is optimizing for search...")
    
    seo_prompt = f"""
    Optimize this content for SEO. Keywords to target: {keywords}
    
    Content to optimize:
    {draft}
    
    Return the full content with SEO improvements applied.
    """
    
    seo_content = call_agent("SEO Specialist", seo_prompt, model, api_key)
    if not seo_content:
        return None
    
    results["seo_content"] = seo_content
    progress_bar.progress(0.6)
    
    # Stage 4: Head of Content
    status_container.info(f"📝 {datetime.now():%H:%M:%S} - **Head of Content** is refining for brand alignment...")
    
    head_prompt = f"""
    Refine this content for brand alignment and compliance.
    Brand voice: {brand_voice or 'Professional, data-driven, friendly'}
    Compliance requirements: {compliance}
    
    Content to refine:
    {seo_content}
    
    Return the full refined content.
    """
    
    polished = call_agent("Head of Content", head_prompt, model, api_key)
    if not polished:
        return None
    
    results["polished"] = polished
    progress_bar.progress(0.8)
    
    # Stage 5: Editor-in-Chief
    status_container.info(f"✅ {datetime.now():%H:%M:%S} - **Editor-in-Chief** is reviewing for final approval...")
    
    editor_prompt = f"""
    Review this final content for approval.
    Original topic: {topic}
    Content type: {content_type}
    
    Content to review:
    {polished}
    """
    
    editor_review = call_agent("Editor-in-Chief", editor_prompt, model, api_key)
    if not editor_review:
        return None
    
    results["editor_review"] = editor_review
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
        
    except:
        results["approval"] = "Approved"
        results["score"] = "8/10"
        results["comments"] = "Content meets quality standards."
        results["final_title"] = topic
        results["final_content"] = polished
    
    status_container.success(f"✨ {datetime.now():%H:%M:%S} - Content generation complete!")
    
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
        b64 = base64.b64encode(content.encode()).decode()
        href = f'<a href="data:text/markdown;base64,{b64}" download="{filename}">📥 {button_text}</a>'
        st.markdown(href, unsafe_allow_html=True)
        
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
        b64 = base64.b64encode(full_html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}">📥 {button_text}</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    elif file_format == "json":
        json_content = json.dumps(st.session_state.current_content, indent=2)
        b64 = base64.b64encode(json_content.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">📥 {button_text}</a>'
        st.markdown(href, unsafe_allow_html=True)

# Main app
def main():
    st.title("✨ Momentic AI Content Team")
    st.markdown("### Your virtual team of AI content specialists")
    
    # Sidebar for API key
    with st.sidebar:
        st.markdown("### 🔑 Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", help="Your API key is not stored")
        
        if st.session_state.current_content:
            st.markdown("### 📊 Current Session")
            st.markdown(f"**Title:** {st.session_state.current_content.get('final_title', 'N/A')}")
            st.markdown(f"**Score:** {st.session_state.current_content.get('score', 'N/A')}")
            st.markdown(f"**Status:** {st.session_state.current_content.get('approval', 'N/A')}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Content", "💬 Chat with Agents", "📚 Version History", "ℹ️ Help"])
    
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
                    ["GPT-3.5 Turbo", "GPT-4.0", "GPT-4.1", "GPT-4.5"],
                    index=1
                )
                
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
            
            submitted = st.form_submit_button("🚀 Generate Content", use_container_width=True)
        
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
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            # Run the pipeline
            results = run_content_pipeline(inputs, model, api_key, status_container, progress_bar)
            
            if results:
                # Store in session state
                st.session_state.current_content = results
                st.session_state.history.append({
                    "version": len(st.session_state.history) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "inputs": inputs,
                    "results": results
                })
                
                # Display results
                st.markdown("---")
                st.markdown("## 📄 Generated Content")
                
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
                        st.success(f"✅ {results['approval']}")
                    else:
                        st.warning(f"⚠️ {results['approval']}")
                
                with col2:
                    if results.get('comments'):
                        st.info(f"💭 Editor's Note: {results['comments']}")
                
                # Content preview
                with st.expander("📖 View Full Content", expanded=True):
                    st.markdown(results['final_content'])
                
                # Download options
                st.markdown("### 💾 Download Content")
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
                    st.button("📥 Word (.docx)", disabled=True, help="Coming soon")
                
                with col4:
                    # Note: PDF requires additional libraries - simplified for demo
                    st.button("📥 PDF", disabled=True, help="Coming soon")
                
                with col5:
                    create_download_button(
                        results,
                        f"{results['final_title'].replace(' ', '_')}.json",
                        "JSON",
                        "json"
                    )
                
                # Revision section
                st.markdown("### 🔄 Request Revisions")
                with st.form("revision_form"):
                    feedback = st.text_area(
                        "Describe the changes you'd like",
                        placeholder="e.g., Make the introduction shorter and add a stronger call-to-action at the end..."
                    )
                    
                    if st.form_submit_button("Apply Revisions"):
                        if feedback:
                            with st.spinner("Applying your revisions..."):
                                revision_result = apply_revision(
                                    results['final_content'],
                                    feedback,
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
                                        "revision_feedback": feedback,
                                        "results": st.session_state.current_content.copy()
                                    })
                                    
                                    st.success("✅ Revisions applied successfully!")
                                    st.experimental_rerun()
    
    with tab2:
        if not api_key:
            st.warning("Please enter your OpenAI API key to use agent chat.")
            return
            
        st.markdown("### 💬 Chat with AI Agents")
        
        if not st.session_state.current_content:
            st.info("Generate content first to chat with the AI agents about it.")
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
    
    with tab3:
        st.markdown("### 📚 Content Version History")
        
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
                    
                    if 'editor_review' in version['results']:
                        st.markdown("**Editor Review:**")
                        st.text(version['results']['editor_review'])
    
    with tab4:
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Enter your OpenAI API Key** in the sidebar (it's not stored)
        2. **Fill out the content request form** with your requirements
        3. **Select an AI model** (GPT-4 recommended for best quality)
        4. **Click Generate Content** and watch your AI team work!
        
        ### 🤖 The AI Team
        
        Your content goes through 5 specialist AI agents:
        
        1. **Strategist** - Plans the content strategy and outline
        2. **Specialist Writer** - Drafts the full content
        3. **SEO Specialist** - Optimizes for search engines
        4. **Head of Content** - Ensures brand alignment
        5. **Editor-in-Chief** - Final review and approval
        
        ### 💡 Tips for Best Results
        
        - Be specific with your topic and key messages
        - Include relevant keywords for SEO optimization
        - Upload reference materials for more accurate content
        - Use the revision feature to fine-tune the output
        - Chat with individual agents for detailed insights
        
        ### 🎨 Momentic Brand Guidelines
        
        This app follows Momentic's design principles:
        - Clean, professional interface
        - Green accent color (#2ECC71) for CTAs
        - High contrast for readability
        - Rounded, modern UI components
        """)

if __name__ == "__main__":
    main()
