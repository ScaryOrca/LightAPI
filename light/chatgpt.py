#!/usr/bin/env python

from chatgpt_wrapper import ChatGPT
import time

def install(session, phone):
    installed = False
    
    # We first need to see if this tool has already been installed.
    for note in session.phones[phone].notes:
        if session.phones[phone].notes[note].title == "ChatGPT" + "\u200b":
            return session.phones[phone].notes[note]

    print("ChatGPT not installed, installing now...")
    # Adding empty notes causes strange behavior.
    note_id = session.add_note(session.phones[phone].get_tool_by_name("Notes"), phone, "Enter prompts below this line", "ChatGPT" + "\u200b")
    print("ChatGPT successfully installed.")

    return session.phones[phone].notes[note_id]

def main(session, phone):
    bot = ChatGPT()

    # ChatGPT should already be installed, but we run the install function
    # anyway. If it's already installed, then the install function will return
    # the note we need.
    note = install(session, phone)
    last_reply = "Enter prompts below this line"
    
    print("Running, waiting for prompts...")

    while True:
        presigned_url = session.get_presigned_get_url(note)
        note_text = session.get_note(presigned_url)
        new_reply = note_text.strip().split("\n")[-1]
        
        if new_reply == "/clear":
            print("Clearing note.")
            session.update_note(note, "Enter prompts below this line")
            last_reply = "Enter prompts below this line"
        elif new_reply != last_reply:
            print("New prompt detected.")
            print("New reply: " + new_reply + "\nLast Reply: " + last_reply)
            response = bot.ask(new_reply)
            note_text = note_text + "\n\n" + response + "\n\n"
            session.update_note(note, note_text)
            last_reply = response.strip().split("\n")[-1]
            time.sleep(3)
        else:
            time.sleep(3)

if __name__ == "__main__":
    main(session, phone)