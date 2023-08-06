import streamlit as st
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# Load secrets
SLACK_USER_TOKEN = st.secrets["slack"]["SLACK_USER_TOKEN"]
BOT_USER_ID = st.secrets["slack"]["BOT_USER_ID"]

client = WebClient(token=SLACK_USER_TOKEN)

def send_message(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        return response['ts']
    except SlackApiError as e:
        st.error(f"Error sending message: {e}")

def fetch_messages(channel, last_message_timestamp):
    response = client.conversations_history(channel=channel, oldest=last_message_timestamp)
    return [msg['text'] for msg in response['messages'] if msg['user'] == BOT_USER_ID]

def get_new_messages(channel, last_message_timestamp):
    while True:
        messages = fetch_messages(channel, last_message_timestamp)
        if messages and not messages[-1].endswith('Typing…_'):
            return messages[-1]
        time.sleep(5)


def find_direct_message_channel(user_id):
    try:
        response = client.conversations_open(users=user_id)
        return response['channel']['id']
    except SlackApiError as e:
        st.error(f"Error opening DM channel: {e}")

def format_story(new_message):
    # Split the story into parts
    parts = new_message.split('\n')

    # Create an HTML string to format the story
    story_html = "<div style='text-align: right; direction: rtl; font-family: Arial, sans-serif; border: 2px solid #e3e3e3; padding: 20px; border-radius: 10px;'>"
    story_html += "<h2 style='color: #4a90e2;'>Claude's Social Story:</h2>"

    for part in parts:
        if part.startswith('- '):
            story_html += f"<h3 style='color: #333;'>{part[2:]}</h3>"
        else:
            story_html += f"<p>{part}</p>"

    story_html += "</div>"

    return story_html

def main():
    # Streamlit app
    # Title of the app
    st.header('Social Story Generator 🧩')

    # Display the model name on the Streamlit app
    st.write(f"🧠 Using model: claude_2")
    
        
    # Collect user inputs
    gender = st.selectbox("Gender of the child:", ["male", "female"], key="gender_selectbox")
    name = st.text_input("Child's Name:")
    age = st.number_input("Child's Age:", min_value=2)
    situation = st.text_input("Describe the situation:")

    # Predefined prompt
    prompt = f"""
    As an AI language model embodying the roles of Carol Gray, Psychologist, Therapist, Special Education Teacher, Speech and Language Therapist, Occupational Therapist, Autism Specialist, and Behavior Analyst, your task is to create a social story strictly in the first-person perspective for a {gender} child named {name}, who is {age} years old, about {situation}. 

    The story must be written in correct Hebrew language suitable for kids. It must adhere to Carol Gray's Social Stories 10.2 criteria and be age-appropriate. It should use a positive and patient tone, provide clear guidance on social cues and appropriate responses, and be reassuring and supportive. The story should describe more than it directs, and it should answer relevant 'wh' questions that describe context, including WHERE, WHEN, WHO, WHAT, HOW, and WHY.

    Ensure the language, sentence length, and complexity of the story are suitable for a {age}-year-old child. If {age} is between 2 and 4, use simple sentences (1-3 per page) with basic vocabulary. The directives should be clear, concrete actions. Familiar scenarios or elements should be included. If {age} is between 5 and 7, use 3-5 sentences per page with expanded vocabulary. Introduce a wider range of situations. If {age} is over 8, use detailed paragraphs with advanced vocabulary and descriptions. Discuss abstract thoughts and emotions.

    Here's the structure you should follow:

    - Title: A clear title that reflects the content of the story. For example, 'Going to the Dentist'.
    - Introduction: The introduction should introduce the topic. For example, 'I sometimes need to go to the dentist to keep my teeth healthy.'
    - Body: The body should describe the situation in detail, including:
        - Descriptive sentences: These should state facts or set the scene. For example, 'The dentist's office is a place where I go to keep my teeth clean and healthy.'
        - Perspective sentences: These should describe my reactions, feelings, or thoughts. For example, 'I feel happy when I sit still in the chair.'
        - Problem sentences: These should identify the problem or challenge. For example, 'Sometimes, I might feel scared when the dentist is checking my teeth.'
        - Coping sentences: These should suggest coping strategies or positive affirmations. For example, 'I can squeeze my toy when I feel scared.'
        - Directive sentences: These should suggest appropriate responses or behaviors. For example, 'I can try to sit still and open my mouth wide when the dentist asks me to.'
        - Affirmative sentences: These should reinforce a key point or express a shared value or belief. For example, 'Going to the dentist is important because it helps keep my teeth clean and healthy.'
    - Conclusion: The conclusion should summarize the story and reinforce the desired behavior. For example, 'Even though going to the dentist can be scary, I know it's important for keeping my teeth healthy. I can do it!'

    Please format the output story as follows:
    - Title: [Title of the story]
    - Introduction: [Introduction of the story]
    - Body: 
        - Descriptive sentences: [Descriptive sentences]
        - Perspective sentences: [Perspective sentences]
        - Problem sentences: [Problem sentences]
        - Coping sentences: [Coping sentences]
        - Directive sentences: [Directive sentences]
        - Affirmative sentences: [Affirmative sentences]
    - Conclusion: [Conclusion of the story]
    """

    # Send the prompt to Claude
    if st.button('Create Social Story'):
        # Spinner to show while waiting for Claude's response
        with st.spinner("Generating Social Story..."):
            dm_channel_id = find_direct_message_channel(BOT_USER_ID)
            if not dm_channel_id:
                st.error("Could not find DM channel with the bot.")
                return

            last_message_timestamp = send_message(dm_channel_id, prompt)
            new_message = get_new_messages(dm_channel_id, last_message_timestamp)
            
            # Replacing newline characters with HTML line breaks
            new_message_html = new_message.replace("\n", "<br>")

        # Formatting the output with HTML
        story_output = f"<div style='text-align: right; direction: rtl; border: 2px solid #f0f0f0; padding: 15px; border-radius: 10px; font-family: Arial; font-size: 14px;'>\
                        <h2>Claude's Social Story:</h2><br>{new_message_html}\
                        </div>"

        st.markdown(story_output, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

