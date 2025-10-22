import uvicorn
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent

DEFINE_ESSAY_TOOL = """
{
    "type": "function",
    "function": {
        "name": "write_essay",
        "description": "Write an essay from a draft",
        "parameters": {
            "type": "object",
            "properties": {
                "draft": {
                    "type": "string",
                    "description": "The draft of the essay to write"
                }
            },
            "required": ["draft"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "accepted": {
                    "type": "boolean",
                    "description": "if the human approved the draft"
                }
            },
            "required": ["accepted"]
        }
    }
}
"""


essay_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="essay_agent",
    instruction=f"""
    You are a human-in-the-loop essay writing assistant that helps write essays with human oversight and approval.

    **Your Primary Role:**
    - Generate short ~100 word esssay drafts for any topic the user requests.
    - Facilitate human review and modification of generated draft
    - When a human approves a draft, return it as text.

    **When a user asks you to write an essay:**
    - ALWAYS come up with a short (roughly 100 word) draft of an essay on the topic.
    - ALWAYS submit the draft to the `write_essay` tool.
    - When the user requests the essay, do not respond with the essay directly before it is approved. Always use the write_essay tool.

    ** PROVIDING THE APPROVED ESSAY TO THE USER: **
    - When the user approves the essay, *ALWAYS* respond with "HERE IS THE ESSAY: <essay>".
    - When the user rejects the essay, *ALWAYS* respond with "REJECTED".

    TOOL_REFERENCE: {DEFINE_ESSAY_TOOL}
    """,
)

# adk_sample_agent = ADKAgent(
#     adk_agent=sample_agent, app_name="essay_demo", user_id="demo_user"
# )

# # Create FastAPI app
# app = FastAPI(title="ADK Middleware Essay Tool Agent")
# # Add the ADK endpoint
# add_adk_fastapi_endpoint(app, adk_sample_agent, path="/")
# uvicorn.run(app, host="localhost", port=8000)