class Phone:
    def __init__(self, id):
        self._id = id
        self._number = None
        self._tools = {}
        self._notes = {}

    @property
    def id(self):
        return self._id

    @property
    def number(self):
        return self._number

    @property
    def tools(self):
        return self._tools

    @property
    def notes(self):
        return self._notes

    @number.setter
    def number(self, number):
        self._number = number

    def get_tool_by_name(self, name):
        for tool in self._tools:
            if self._tools[tool].label == name:
                return self._tools[tool]

        return None

    def add_note(self, note):
        self._notes[note.id] = note
        
    def add_tool(self, tool):
        self._tools[tool.id] = tool

    def remove_tool(self, tool):
        self._tools(tool)

class Tool:
    def __init__(self, id, instance_id, label):
        self._id = id
        self._instance_id = instance_id
        self._label = label

    @property
    def id(self):
        return self._id

    @property
    def instance_id(self):
        return self._instance_id

    @property
    def label(self):
        return self._label

class Note:
    def __init__(self, title, id, content, presigned_url):
        self._title = title
        self._id = id
        self._content = content
        self._presigned_url = presigned_url

    @property
    def id(self):
        return self._id

    @property
    def presigned_url(self):
        return self._presigned_url

    @property
    def title(self):
        return self._title
    
    #@content.setter
    #def content(self, content):
    #    self._content = content