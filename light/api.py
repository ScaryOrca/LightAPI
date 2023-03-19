import requests
from phone import Note
from phone import NestedTool
from phone import Phone
from phone import Tool

# API Routes
API_ADD_TOOL = "https://production.lightphonecloud.com/api/device_tools"
API_DELETE_TOOL = "https://production.lightphonecloud.com/api/device_tools"
API_DEVICES = "https://production.lightphonecloud.com/api/devices"
API_LOGIN = "https://production.lightphonecloud.com/api/authorizations"
API_NOTES = "https://production.lightphonecloud.com/api/notes?device_tool_id="
API_CREATE_NOTE = "https://production.lightphonecloud.com/api/notes"
API_PRESIGNED_GET_URL = "https://production.lightphonecloud.com/api/notes/"
API_PRESIGNED_PUT_URL = "https://production.lightphonecloud.com/api/notes/"
API_TOOLS = "https://production.lightphonecloud.com/api/tools"
API_UPDATE_NOTE = ""

class LightApi:
    def __init__(self):
        self._token = None
        self._phones = {}
        self._tools = {}

    @property
    def phones(self):
        return self._phones

    @property
    def tools(self):
        return self._tools

    def login(self, email, password):
        payload = {"email": email, "password": password}
        headers = {"content-type": "application/vnd.api+json"}
        login_request = requests.post(API_LOGIN, headers=headers, json=payload)
        login_json = login_request.json()

        if "errors" not in login_json.keys():
            # Find session token
            for include in login_json["included"]:
                if include["type"] == "tokens":
                    self._token = include["attributes"]["token"]
                    break

            # Get list of tools available to install
            self._get_all_tools()
            
            # Setup phones
            devices_request_headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json"}
            devices_request = requests.get(API_DEVICES, headers=devices_request_headers)
            devices_json = devices_request.json()

            for phone in devices_json["data"]:
                self._phones[phone["id"]] = Phone(phone["id"]);

            # Add tools and set phone number(s)
            for include in devices_json["included"]:
                if include["type"] == "device_tools":
                    tool = Tool(include["relationships"]["tool"]["data"]["id"], include["id"], self._tools[include["relationships"]["tool"]["data"]["id"]]["label"])
                    self._phones[include["relationships"]["device"]["data"]["id"]].add_tool(tool)
                elif include["type"] == "sims":
                    self._phones[include["relationships"]["device"]["data"]["id"]].number = include["attributes"]["phone_number"]

            for phone in self._phones:
                self.get_notes(phone, self._phones[phone].get_tool_by_name("Notes"))

            self._get_nested_tools()

        return login_json

    def delete_tool(self, tool):
        headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json"}
        res = requests.delete(API_DELETE_TOOL + '/' + tool.instance_id, headers=headers)

        # TODO: Update phone state. We can either loop through every phone until
        # we find the tool with the same instance ID, and then remove that tool,
        # or we can require the phone's ID when calling this function.

    def add_tool(self, phone_id, tool_id):
        headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json", "content-type": "application/vnd.api+json"}
        payload = {
            "data": {
                "attributes": {
                    "config": {},
                    "device_id": phone_id,
                    "tool_id": tool_id,
                },
                "type": "device_tools"
            }
        }

        res = requests.post(API_ADD_TOOL, headers=headers, json=payload)

        # If tool was successfully removed, we should update the state.
        if res.status_code == 201:
            res_json = res.json()
            new_tool = Tool(res_json["data"]["relationships"]["tool"]["data"]["id"], res_json["data"]["id"], self._tools[res_json["data"]["relationships"]["tool"]["data"]["id"]]["label"])
            self._phones[phone_id].add_tool(new_tool)
            
        
    def add_note(self, tool, phone_id, text, title):
        headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json", "content-type": "application/vnd.api+json"}
        payload = {
            "data": {
                "attributes": {
                    "device_tool_id": tool.instance_id,
                    "filename": "note.txt",
                    "title": title
                },
                "type": "notes"
            }
        }

        # Creating notes is a two-step process.
        note_request = requests.post(API_CREATE_NOTE, headers=headers, json=payload)
        note_json = note_request.json()
        presigned_url = note_json["included"][0]["attributes"]["presigned_url"]
        new_note = Note(title, note_json["included"][0]["id"], text, presigned_url)
        self._phones[phone_id].add_note(new_note)
        self.update_note(self._phones[phone_id].notes[note_json["included"][0]["id"]], text, presigned_url)

        return note_json["included"][0]["id"]

    def get_notes(self, phone_id, tool):
        headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json"}
        notes_request = requests.get(API_NOTES + tool.instance_id, headers=headers)
        notes_json = notes_request.json()
        notes = {}

        for note in notes_json["data"]:
            title = ""
            content = ""
            presigned_url_request = requests.get(API_PRESIGNED_GET_URL + note["id"] + "/generate_presigned_get_url", headers=headers)
            presigned_url_json = presigned_url_request.json()
            
            notes[note["id"]] = {}
            notes[note["id"]]["id"] = note["id"]
            notes[note["id"]]["url"] = presigned_url_json["presigned_get_url"]

            # If this note doesn't have a title, we should set the title as the
            # first 17 characters of the note.
            if note["attributes"]["title"] == "Untitled":
                # Since we have to fetch the note's content for the title, we'll
                # go ahead and save it.
                content = self.get_note(presigned_url_json["presigned_get_url"])
                title = (content[:17] + "...") if len(content) > 17 else content
                title = title.replace("\n", " ")
            else:
                title = note["attributes"]["title"]

            new_note = Note(title, note["id"], content, notes[note["id"]]["url"])
            self._phones[phone_id].add_note(new_note)        
        
    def get_note(self, presigned_url):
        headers = {"content-type": "text/plain", "origin": "https://dashboard.thelightphone.com", "referer": "https://dashboard.thelightphone.com/", "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site", "accept": "*/*", "accept-encoding": "gzip, deflate, br", "sec-fetch-dest": "empty", "authority": "light-two-api-production.nyc3.digitaloceanspaces.com", "user-agent": "light", "accept-language": "en-US,en;q=0.9"}
        note_request = requests.get(presigned_url, headers=headers)

        return note_request.text

    def _get_all_tools(self):
        available_tools_headers = {"authorization": "Bearer" + self._token, "accept": "application/vnd.api+json"}
        available_tools_request = requests.get(API_TOOLS, headers=available_tools_headers)
        available_tools_json = available_tools_request.json()

        for tool in available_tools_json["data"]:
            self._tools[tool["id"]] = {"label": tool["attributes"]["title"]}

    def _get_nested_tools(self):
        # Loop through every phone and figure out which nested tools are
        # installed. Nested tools are identified by the last character of their
        # title, "\u200b", a zero-width space.
        for phone in self._phones:
            for note in self._phones[phone].notes:
                if self._phones[phone].notes[note].title.endswith("\u200b"):
                    new_nested_tool = NestedTool(self._phones[phone].notes[note].title, self._phones[phone].notes[note].title.replace("\u200b", ""))
                    self._phones[phone].add_nested_tool(new_nested_tool)
        
    def update_note(self, note, text, presigned_url = None):            
        if not presigned_url:
            headers = {"authorization": "Bearer " + self._token, "accept": "application/vnd.api+json"}
            presigned_url_request = requests.get(API_PRESIGNED_PUT_URL + note.id + "/generate_presigned_put_url", headers=headers)
            presigned_url_json = presigned_url_request.json()
            presigned_url = presigned_url_json["presigned_put_url"]

        requests.put(presigned_url, data=text)
        
