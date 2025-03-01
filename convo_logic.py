import json
import requests
import logging
import os
from dotenv import load_dotenv
from decisionTree import decisionTree
from user import (
    load_user_history,
    save_user_history,
    add_entry_to_history,
    update_user_info,
)

# --------------------------------------------------------------------
# 1. Load Environment Variables
# --------------------------------------------------------------------
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_url = os.getenv("GEMINI_API_URL", "https://api.gemini.com/v1/chat/completions")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A global variable for the conversation state in your decision tree
predictionState = "root"

def generate_gemini_response(prompt):
    """
    Example function to call a hypothetical Gemini ChatCompletion-like API.
    Adjust the request format to match the real API once published.
    """
    if not gemini_api_key:
        logger.error("Gemini API key not found. Please set GEMINI_API_KEY in your .env.")
        return None

    if not gemini_api_url:
        logger.error("Gemini API URL not found. Please set GEMINI_API_URL in your .env.")
        return None

    headers = {
        "Authorization": f"Bearer {gemini_api_key}",
        "Content-Type": "application/json",
    }

    # Hypothetical payload. In practice, Gemini might use a different structure.
    data = {
        "model": "gemini-advanced-1",  # or some model name when available
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    logger.info("Sending request to Gemini API...")
    response = requests.post(gemini_api_url, headers=headers, json=data)

    logger.info(f"Gemini response status: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Failed Gemini request: {response.text}")
        return None

    try:
        gemini_data = response.json()
        # Hypothetical location of the text.  
        return gemini_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing Gemini response: {e}")
        return None


def interpret_response(user_response, question_node):
    """
    Use Gemini to interpret user_response. 
    Return one of the valid keys or 'invalid'.
    """
    options = list(question_node.keys())
    options.remove("question")

    prompt = f"""
    Given the user response: "{user_response}"
    And the question: "{question_node['question']}"
    Interpret the response and categorize it into one of the following options: {', '.join(options)}
    If the response doesn't properly address the question, return "invalid".
    
    Please return only one option from the list above, not multiple options.
    """

    interpreted_response = generate_gemini_response(prompt)
    if not interpreted_response:
        return "invalid"

    interpreted_response = interpreted_response.strip().lower()
    if interpreted_response in options:
        return interpreted_response
    elif "," in interpreted_response:
        # If multiple options are returned, take the first one
        first_option = interpreted_response.split(",")[0].strip()
        return first_option if first_option in options else "invalid"

    return "invalid"


def update_user_history(question, answer, user_history):
    """
    Update the user_history with any relevant info from the question/answer. 
    This might parse age, name, etc., from the Gemini response.
    """
    # 1) Extract structured user info
    extract_prompt = f"""
    Given the question: "{question}"
    And the user's response: "{answer}"
    Extract the following information: fname, lname, age, gender, height, weight.
    Return the extracted information in the format:
    {{
      "fname": <fname>,
      "lname": <lname>,
      "age": <age>,
      "gender": <gender>,
      "height": <height>,
      "weight": <weight>
    }}
    If any information is not available, return null for that field.
    """

    gemini_response = generate_gemini_response(extract_prompt)
    try:
        extracted_info = json.loads(gemini_response)
        for key, value in extracted_info.items():
            if value is not None:
                update_user_info(user_history, key, value)
    except (json.JSONDecodeError, TypeError):
        logger.error("Failed to parse Gemini JSON for user info.")

    # 2) Generate bullet points
    bullet_prompt = f"""
    Given the question: "{question}"
    And the user's response: "{answer}"
    Create a concise bullet point summary of the key information in the response. Avoid redundancy.
    """

    bullet_response = generate_gemini_response(bullet_prompt)
    if bullet_response:
        # Attempt to split into bullet points by lines
        lines = [line.strip() for line in bullet_response.strip().split("\n") if line.strip()]
        if isinstance(lines, list):
            add_entry_to_history(user_history, lines)
        else:
            logger.warning("Gemini bullet response not a list.")
            add_entry_to_history(user_history, [f"Summary error: {bullet_response}"])
    else:
        logger.warning("No bullet response from Gemini.")
        add_entry_to_history(user_history, [f"Error processing: {answer}"])

    return user_history


def rephrase_question(original_question, user_response, invalid_response=False, user_history=None):
    """
    Rephrase the question for clarity or indicate the response was invalid.
    """
    if user_history is None:
        user_history = {"entries": []}

    # Gather user history for context
    user_history_list = []
    for entry in user_history["entries"]:
        for date, info in entry.items():
            user_history_list.extend([f"- {i}" for i in info])

    if "current_call" in user_history:
        user_history_list.extend([f"- Current Call: {call}" for call in user_history["current_call"]])

    # Additional user info
    user_history_list.extend([
        f"- Age: {user_history.get('age', 'N/A')}",
        f"- Gender: {user_history.get('gender', 'N/A')}",
        f"- Name: {user_history.get('fname', '')} {user_history.get('lname', '')}",
        f"- Weight: {user_history.get('weight', 'N/A')}",
        f"- Height: {user_history.get('height', 'N/A')}",
    ])
    user_history_formatted = "\n".join(user_history_list)

    if invalid_response:
        context = f"""
        The user responded: "{user_response}", which was invalid for the question: "{original_question}"

        You need to:
        1. Politely inform the user their response is invalid.
        2. Rephrase the original question to guide them properly.
        3. Keep it concise.

        User history:
        {user_history_formatted}
        """
    else:
        context = f"""
        Rephrase the following question to better align with the user's history and keep it concise:
        
        Original Question: "{original_question}"
        User history:
        {user_history_formatted}
        """

    gemini_reply = generate_gemini_response(context)
    return gemini_reply.strip('"') if gemini_reply else "Could not rephrase."


def gpt_call(user_response, phone_number):
    """
    The main logic, but now using Gemini in place of OpenAI. 
    """
    global predictionState

    # Load user history
    user_history = load_user_history(phone_number)

    current_node = decisionTree[predictionState]
    current_question = current_node["question"]
    interpreted_response = interpret_response(user_response, current_node)

    if interpreted_response == "invalid":
        rephrased_question = rephrase_question(current_question, user_response, True, user_history)
        return rephrased_question

    # Update user history
    user_history = update_user_history(current_question, user_response, user_history)
    save_user_history(phone_number, user_history)

    if interpreted_response in current_node:
        predictionState = current_node[interpreted_response]
    else:
        return f"I couldn't understand your response. {current_question}"

    # Check if new state is a leaf
    if predictionState not in decisionTree:
        return f"Based on your answers, you may have {predictionState}. Consult a medical professional."

    # Otherwise, ask next question
    next_question = decisionTree[predictionState]["question"]
    rephrased_question = rephrase_question(next_question, user_response, False, user_history)
    return rephrased_question


def terminal():
    """
    Simple CLI for testing. If you run this file directly (python conversation_logic.py),
    you'll have a console-based conversation with Gemini as the AI.
    """
    print("Welcome to the medical diagnosis assistant (Gemini-based).")
    print("Please answer the following questions.")

    phone_number = input("Please enter your phone number: ")
    user_history = load_user_history(phone_number)

    # Start with root question
    from decisionTree import decisionTree
    root_question = decisionTree["root"]["question"]
    rephrased_question = rephrase_question(root_question, "", False, user_history)
    print(rephrased_question)

    user_input = input("Your answer: ")
    while True:
        response = gpt_call(user_input, phone_number)
        print(response)

        if "Based on your answers" in response:
            break

        user_input = input("Your answer: ")

    print("\nYour user history:")
    print(json.dumps(user_history, indent=2))


if __name__ == "__main__":
    terminal()
