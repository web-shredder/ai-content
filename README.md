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
