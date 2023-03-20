# LightAPI

LightAPI is a command line tool to access the Light Phone dashboard and build
text-based custom tools.

## Installation

TODO

## Nested Tools

The Light Phone has no API for building custom tools. However, we can leverage
the Notes tool as a way to receive input and output information. Included in
this repository are a few tools to demonstrate what you can do.

### ChatGPT

With the help of the [ChatGPT Wrapper](https://github.com/mmabrouk/chatgpt-wrapper) library, we can interact with ChatGPT from
the Notes tool.

#### Usage

After installing the ChatGPT tool and running the backend from the command line,
you'll see a new note in your Notes tool titled "ChatGPT". With the backend
running, you can type any prompt you want and the backend will send it off to
ChatGPT. After receiving a reply, the ChatGPT tool will add the reply to the 
bottom of the note, after your last prompt. The Notes tool doesn't refresh the
note live, so you'll need to back out of the note and go back in to view any
new replies.

#### Commands

The ChatGPT tool comes with a few commands:

* `/clear`: Clears the note out. If the note gets too big, it can be helpful to
clear everything out. 

### 2FA

TODO

### SSH

TODO

### Weather

TODO

## TODO

TODO