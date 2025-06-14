# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using newer GPT-4 based models.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

   If you encounter `ModuleNotFoundError: No module named 'networkx'`,
   double-check that the requirements were installed successfully.

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Available AI models

The model selector offers three options that map to the corresponding OpenAI endpoints:

| Option | Model name |
| ------ | ---------- |
| `4.1`  | `gpt-4.1-2025-04-14` |
| `4o`   | `gpt-4o-2024-08-06` |
| `o3`   | `o3-2025-04-16` |

Choose whichever model best meets your quality and speed requirements when generating or revising content.

### Planning Mode

When you only need a strategic brief, enable **Planning Mode** in the app. This runs just the Strategist, SEO Specialist and Head of Content agents to deliver a content plan with up to three related topic fanouts.

The SEO Specialist now runs before any drafting begins so you can review keyword opportunities up front.
In both regular and Planning Mode it lists suggested search queries under a **Search Queries** heading with a fan-out graph.
Each bullet follows the `<Type>: <query> - <note>` format. The note after the dash explains why the query matters and is displayed in a separate **Reason** column. The table highlights type mismatches and shows cosine similarity scores. You can download the full list as a CSV file for further analysis.
If fewer than 20 queries are supplied, the app displays a warning so you can rerun the SEO agent.

### Reference Sharing Across Agents

Uploaded files and all form inputs are stitched together into a context block that gets sent to **every** AI agent. This keeps the Strategist, SEO Specialist, Specialist Writer, Head of Content and Editor-in-Chief on the same page. The combined context also appears in the chat prompts so you can see exactly what they're working from.
The app also loads the Markdown files in the `knowledge/` folder and appends them to that shared context so every agent consistently references the brand messaging, style guide and editorial process.
