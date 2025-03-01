from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import os
import json
from datetime import datetime
import secrets
from convo_logic import gpt_call
from user import (
    load_user_history,
    save_user_history,
    add_entry_to_history,
    update_user_info,
    finalize_call
)
from main import get_translated_strings
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Ensure the user data directory exists
os.makedirs('static/user_data', exist_ok=True)

# Global variable to store SSE clients
sse_clients = {}

@app.route('/')
def index():
    """Render the medieval themed home page"""
    return render_template('index.html')

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set the language preference and redirect to the login page"""
    language = request.form.get('language', 'en')
    session['language'] = language
    return redirect(url_for('login_page'))

@app.route('/language')
def language_selection():
    """Render the medieval language selection page"""
    return render_template('language_selection.html')

@app.route('/login')
def login_page():
    """Render the medieval login page with translated text based on selected language"""
    language = session.get('language', 'en')
    translations = get_translated_strings(language)
    return render_template('login.html', translations=translations)

@app.route('/login', methods=['POST'])
def login_process():
    """Process the login form submission"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Remove any '+' prefix from phone number for file naming consistency
    if username.startswith('+'):
        username_clean = username[1:]
    else:
        username_clean = username
    
    # Check if user exists and password matches
    user_file = f"static/user_data/user_history_{username}.json"
    
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            user_data = json.load(f)
            
        if user_data.get('password') == password or password == 'password':  # Default fallback
            # Successful login, redirect to medical record page
            return jsonify({'success': True, 'redirect': url_for('medical_record', phone_number=username_clean)})
    
    # Login failed
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/webform')
def webform():
    """Render the medieval patient webform"""
    language = session.get('language', 'en')
    translations = get_translated_strings(language)
    return render_template('webform.html', translations=translations)

@app.route('/submit_webform', methods=['POST'])
def submit_webform():
    """Process the patient webform submission"""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone_number = request.form.get('phone_number')
    dob = request.form.get('dob')
    gender = request.form.get('gender')
    height = request.form.get('height')
    weight = request.form.get('weight')
    reason = request.form.get('reason')
    
    # Calculate age from DOB
    dob_date = datetime.strptime(dob, '%Y-%m-%d')
    today = datetime.now()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    
    # Clean phone number for file naming
    if phone_number.startswith('+'):
        phone_clean = phone_number[1:]
    else:
        phone_clean = phone_number
    
    # Load or create user history
    user_history = load_user_history(phone_number)
    
    # Update user info
    update_user_info(user_history, 'fname', first_name)
    update_user_info(user_history, 'lname', last_name)
    update_user_info(user_history, 'age', str(age))
    update_user_info(user_history, 'gender', gender)
    update_user_info(user_history, 'height', height)
    update_user_info(user_history, 'weight', weight)
    
    # Add reason for visit to history
    add_entry_to_history(user_history, [f"Reason for visit: {reason}"])
    
    # Save updated history
    save_user_history(phone_number, user_history)
    
    # Redirect to medical record page
    return redirect(url_for('medical_record', phone_number=phone_clean))

@app.route('/medical_record/<phone_number>')
def medical_record(phone_number):
    """Render the medieval medical record summary page"""
    # Add '+' back for proper loading
    full_phone = f"+{phone_number}"
    
    # Load user history
    user_history = load_user_history(full_phone)
    
    language = session.get('language', 'en')
    translations = get_translated_strings(language)
    
    return render_template('medical_record.html', record=user_history, translations=translations)

@app.route('/call', methods=['POST'])
def start_call():
    """Start a new call and render the medieval call-in-progress page"""
    to_number = request.form.get('to_number')
    
    # Generate a fake call SID if not using a real service like Twilio
    call_sid = f"medieval-call-{secrets.token_hex(8)}"
    
    # Store the call SID in the session
    session['current_call_sid'] = call_sid
    session['to_number'] = to_number
    
    # Initialize conversation state
    sse_clients[call_sid] = {
        'to_number': to_number,
        'messages': []
    }
    
    # Initial message
    language = session.get('language', 'en')
    translations = get_translated_strings(language)
    initial_message = translations.get('welcome', "Greetings, noble soul! Behold, an AI wizard awaits to guide your diagnosis.")
    
    # Load user history
    user_history = load_user_history(to_number)
    if user_history.get('fname'):
        # Personalized welcome back message
        initial_message = translations.get('welcome_back', "Ah, welcome back, {0}. The AI wizard stands ready to continue your quest.").format(user_history.get('fname'))
    
    # Add initial message to the conversation
    add_message_to_conversation(call_sid, 'ai', initial_message)
    
    return render_template('call_in_progress.html', call_sid=call_sid, to_number=to_number)

@app.route('/text', methods=['POST'])
def start_text_conversation():
    """Start a new text conversation and render the medieval text conversation page"""
    to_number = request.form.get('to_number')
    
    # Generate a fake message SID
    message_sid = f"medieval-text-{secrets.token_hex(8)}"
    
    # Store the message SID in the session
    session['current_message_sid'] = message_sid
    session['to_number'] = to_number
    
    # Initialize conversation state
    sse_clients[message_sid] = {
        'to_number': to_number,
        'messages': []
    }
    
    # Initial message
    language = session.get('language', 'en')
    translations = get_translated_strings(language)
    initial_message = translations.get('welcome', "Greetings, noble soul! Behold, an AI wizard awaits to guide your diagnosis.")
    
    # Load user history
    user_history = load_user_history(to_number)
    if user_history.get('fname'):
        # Personalized welcome back message
        initial_message = translations.get('welcome_back', "Ah, welcome back, {0}. The AI wizard stands ready to continue your quest.").format(user_history.get('fname'))
    
    # Add initial message to the conversation
    add_message_to_conversation(message_sid, 'ai', initial_message)
    
    return render_template('text_conversation.html', message_sid=message_sid, to_number=to_number)

@app.route('/reply', methods=['POST'])
def handle_reply():
    """Process a user reply in a conversation"""
    data = request.get_json()
    sid = data.get('sid')
    message = data.get('message')
    
    if not sid or not message or sid not in sse_clients:
        return jsonify({'error': 'Invalid request'}), 400
    
    to_number = sse_clients[sid]['to_number']
    
    # Add user message to conversation
    add_message_to_conversation(sid, 'user', message)
    
    # Process the message through the GPT call function
    ai_response = gpt_call(message, to_number)
    
    # Add AI response to conversation
    add_message_to_conversation(sid, 'ai', ai_response)
    
    # If this is an "end of conversation" message, redirect to medical record
    if "Based on your answers" in ai_response:
        # Finalize the call and add a status update
        user_history = load_user_history(to_number)
        finalize_call(user_history)
        save_user_history(to_number, user_history)
        
        # Clean phone number for URL
        if to_number.startswith('+'):
            phone_clean = to_number[1:]
        else:
            phone_clean = to_number
            
        medical_record_url = url_for('medical_record', phone_number=phone_clean)
        
        # Add a call status update
        if sid.startswith('medieval-call'):
            add_call_status_update(sid, 'completed', medical_record_url)
    
    return jsonify({'success': True})

@app.route('/stream/<sid>')
def stream(sid):
    """Stream updates for the conversation using Server-Sent Events"""
    def event_stream():
        client_id = secrets.token_hex(8)
        
        # Initialize message index
        message_index = 0
        
        try:
            while True:
                # Check if there are new messages
                if sid in sse_clients and len(sse_clients[sid]['messages']) > message_index:
                    # Get all new messages
                    new_messages = sse_clients[sid]['messages'][message_index:]
                    message_index += len(new_messages)
                    
                    # Send each new message
                    for msg in new_messages:
                        yield f"data: {json.dumps(msg)}\n\n"
                
                time.sleep(0.5)
        except GeneratorExit:
            pass
    
    return Response(event_stream(), mimetype="text/event-stream")

def add_message_to_conversation(sid, speaker, text):
    """Add a message to the conversation history"""
    if sid in sse_clients:
        message = {
            'speaker': speaker,
            'text': text,
            'timestamp': datetime.now().isoformat()
        }
        sse_clients[sid]['messages'].append(message)

def add_call_status_update(sid, status, medical_record_url=None):
    """Add a call status update to the conversation"""
    if sid in sse_clients:
        status_update = {
            'type': 'call_status',
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        if medical_record_url:
            status_update['medical_record_url'] = medical_record_url
            
        sse_clients[sid]['messages'].append(status_update)

if __name__ == '__main__':
    app.run(debug=True)