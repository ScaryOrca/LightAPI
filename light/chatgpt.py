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
    note_id = session.add_note(session.phones[phone].get_tool_by_name("Notes"), phone, " ", "ChatGPT" + "\u200b")
    print("ChatGPT successfully installed.")    

    return session.phones[phone].notes[note_id]

def main(session, phone):
    bot = ChatGPT()
    note = install(session, phone)
    last_reply = ""
    
    while True:
        note_text = session.get_note(note.presigned_url)
        new_reply = note_text.strip().split("\n")[-1]

        if new_reply != last_reply:
            print("New prompt detected.")
            print("New reply: " + new_reply + "\nLast Reply: " + last_reply)
            response = bot.ask(new_reply)
            note_text = note_text + "\n\n" + response
            session.update_note(note, note_text)
            last_reply = response.strip().split("\n")[-1]
            time.sleep(3)
        else:
            print("No new questions.")
            time.sleep(3)

if __name__ == "__main__":
    main(session, phone)