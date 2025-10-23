"""Shared State feature."""

from __future__ import annotations

from dotenv import load_dotenv

import json
from enum import Enum
from typing import Dict, List, Any, Optional, TypedDict
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# ADK imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from google.adk.tools import FunctionTool, ToolContext, AgentTool
from google.genai.types import Content, Part , FunctionDeclaration
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from data.genz_translator import GenZTranslator
from essay_agent import essay_agent

load_dotenv()

class TranslationData(TypedDict):
    original_text: str
    translated_text: str

class TranslationResponse(TypedDict, total=False):
    status: str
    message: str
    data: Optional[TranslationData]

class TranslationsState(BaseModel):
    """List of the translations being written."""
    translations: list[str] = Field(
        default_factory=list,
        description='The list of translated sentences',
    )


def get_genz_translation(
    user_input: str
) -> TranslationResponse:
    """
    Translates user input into gen-z lingua.

    Args:
        "new_translations": {
            "type": "string",
            "description": "The user input that needs translation",
        }

    Returns:
        Dict containing original input and translated text in the data field
    """
    try:
        initiate_translator = GenZTranslator()
        translated_text = initiate_translator.translate_to_genz(user_input)
        print(f"\n translated_text: {translated_text}")
        return {
            "status": "success",
            "message": "Translated successfully",
            "data": {
                "original_text": user_input,
                "translated_text": translated_text
            }
        }

    except Exception as e:
        return {"status": "error", "message": f"Error obtaining translation: {str(e)}"}

def get_english_translation(
    user_input: str
) -> TranslationResponse:
    """
    Translates user input from gen-z lingua to english.

    Args:
        "new_translations": {
            "type": "string",
            "description": "The user input that needs translation",
        }

    Returns:
        Dict containing original input and translated text in the data field
    """
    try:
        initiate_translator = GenZTranslator()
        translated_text = initiate_translator.translate_to_english(user_input)
        print(f"\n translated_text: {translated_text}")
        return {
            "status": "success",
            "message": "Translated successfully",
            "data": {
                "original_text": user_input,
                "translated_text": translated_text
            }
        }

    except Exception as e:
        return {"status": "error", "message": f"Error obtaining translation: {str(e)}"}

def set_translations(
    tool_context: ToolContext,
    new_translations: list[str]
) -> Dict[str, str]:
    """
    Set the list of translations using the provided new list.

    Args:
        "new_translations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The new list of translations to maintain",
        }

    Returns:
        Dict indicating success status and message
    """
    try:
        # Put this into a state object just to confirm the shape
        new_state = { "translations": new_translations}
        tool_context.state["translations"] = new_state["translations"]
        return {"status": "success", "message": "Translations updated successfully"}

    except Exception as e:
        return {"status": "error", "message": f"Error updating translations: {str(e)}"}


def choose_translation_direction(
    text: str
) -> Dict[str, str]:
    """
    This function triggers the human-in-the-loop UI for choosing translation direction.
    The actual logic is handled on the frontend.

    Args:
        text: The text to be translated

    Returns:
        Dict containing the chosen direction ("to_genz" or "to_english")
    """
    # This is a tool that will be used by the agent to get user input
    # The frontend will handle the actual UI and return the user's choice
    # The response will be automatically returned to the agent
    return {"direction": "to_genz"}  # This return value will be overridden by the frontend response

def on_before_agent(callback_context: CallbackContext):
    """
    Initialize translations state if it doesn't exist.
    """

    if "translations" not in callback_context.state:
        # Initialize with default recipe
        default_translations =     []
        callback_context.state["translations"] = default_translations

    return None

# --- Define the Callback Function ---
#  modifying the agent's system prompt to incude the current state of the translations list
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "TranslationsAgent":
        translations_json = "No translations yet"
        if "translations" in callback_context.state and callback_context.state["translations"] is not None:
            try:
                translations_json = json.dumps(callback_context.state["translations"], indent=2)
            except Exception as e:
                translations_json = f"Error serializing translations: {str(e)}"
        # --- Modification Example ---
        # Add a prefix to the system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
        prefix = f"""You are a helpful assistant for maintaining a list of translations.
        This is the current state of the list of translations: {translations_json}
        When you modify the list of translations (wether to add, remove, or modify one or more translations), use the set_translations tool to update the list."""
        # Ensure system_instruction is Content and parts list exists
        if not isinstance(original_instruction, types.Content):
            # Handle case where it might be a string (though config expects Content)
            original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
        if not original_instruction.parts:
            original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist

        # Modify the text of the first part
        modified_text = prefix + (original_instruction.parts[0].text or "")
        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

    return None



# --- Define the Callback Function ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Stop the consecutive tool calling of the agent"""
    agent_name = callback_context.agent_name
    # --- Inspection ---
    if agent_name == "TranslationsAgent":
        original_text = ""
        if llm_response.content and llm_response.content.parts:
            # Assuming simple text response for this example
            if  llm_response.content.role=='model' and llm_response.content.parts[0].text:
                original_text = llm_response.content.parts[0].text
                callback_context._invocation_context.end_invocation = True

        elif llm_response.error_message:
            return None
        else:
            return None # Nothing to modify
    return None


translations_agent = LlmAgent(
        name="TranslationsAgent",
        model="gemini-2.5-flash",
        instruction=f"""
        When a user asks you to do anything regarding translations, you MUST use the set_translations tool.

        IMPORTANT RULES ABOUT TRANSLATIONS AND THE SET_TRANSLATIONS TOOL:
        1. Always use the set_translations tool for any translations-related requests
        2. Always pass the COMPLETE LIST of translations to the set_translations tool. If the list had 5 translations and you removed one, you must pass the complete list of 4 remaining translations.
        3. You can use existing translations if one is relevant to the user's request, but you can also create new translations as required. To create new translations, you MUST first use the get_genz_translation tool to generate the Gen Z version of the provided text.
        4. Be creative and helpful in ensuring translations are complete and practical, but rely on the get_genz_translation tool for generating the Gen Z lingo.
        5. After using the tool, provide a brief summary of what you created, removed, or changed

        IMPORTANT RULES ABOUT TRANSLATIONS:
        When a user provides a text to translate, you MUST:
        1. First use the choose_translation_direction tool to ask the user for the translation direction by passing the text to translate
        2. Wait for the response which will be in the format {{"direction": "to_genz"}} or {{"direction": "to_english"}}
        3. Based on the direction:
           - If "to_genz", use get_genz_translation tool with the original text
           - If "to_english", use get_english_translation tool with the original text
        4. After obtaining the translation response, create a new translation entry in the format:
           - For Gen Z: "Original: [original_text] Gen Z: [translated_text]"
           - For English: "Original: [original_text] English: [translated_text]"
        5. Add this new translation to the existing translations list using set_translations
        6. Always maintain the complete list of translations when using set_translations

        Examples of when to use the translations tools:
        - "Translate this for me: 'The soap is clean'" → First use choose_translation_direction with the text "The soap is clean". If the user chooses "to_genz", then use get_genz_translation. If the user chooses "to_english", then use get_english_translation. After getting the translation, use set_translations to update the list.

        Do your best to ensure translations plausibly make sense and maintain the original meaning.

        IMPORTANT RULES ABOUT ESSAY WRITING AND THE ESSAY_AGENT TOOL:
        **When a user asks you to write an essay:**
        - ALWAYS come up with a short (roughly 100 word) draft of an essay on the topic.
        - ALWAYS submit the draft to the `write_essay` tool.
        - When the user requests the essay, do not respond with the essay directly before it is approved. Always use the write_essay tool.

        ** PROVIDING THE APPROVED ESSAY TO THE USER: **
        - When the user approves the essay, *ALWAYS* respond with "HERE IS THE ESSAY: <essay>".
        - When the user rejects the essay, *ALWAYS* respond with "REJECTED".
        """,
        tools=[get_genz_translation, get_english_translation, set_translations, AgentTool(essay_agent), choose_translation_direction],
        before_agent_callback=on_before_agent,
        before_model_callback=before_model_modifier,
        after_model_callback = simple_after_model_modifier
    )

# Create ADK middleware agent instance
adk_translations_agent = ADKAgent(
    adk_agent=translations_agent,
    app_name="translations_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Translations Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_translations_agent, path="/")

if __name__ == "__main__":
    import os
    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
