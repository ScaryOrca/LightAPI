#!/usr/bin/env python3

from getpass import getpass
from phone import Phone
from phone import Tool
from api import LightApi
import chatgpt    

def phone_action_menu():
    print("1) Add Tool")
    print("2) Remove Tool")
    print("3) Add Nested Tool")
    print("4) Remove Nested Tool")
    print("5) Manage Notes")
    print("*) Back")

def nested_tools_menu():
    pass
    
def install_nested_tool():
    pass

if __name__ == "__main__":
    current_phone = None
    valid_selection = False
    current_menu = "select_phone"
    session = LightApi()
    phones = {}

    # Retry login until successful
    while True and current_menu != "exit":
        email = getpass(prompt="Email: ")
        password = getpass()
        login_result = session.login(email, password)
        print("")

        if "errors" in login_result:
            print("Error: " + login_result["errors"][0]["detail"])
        else:
            while True and current_menu != "exit":
                #chatgpt.main(session, next(iter(session.phones)))

                # Phone selection menu
                valid_selection = False
                while current_menu == "select_phone":
                    # Setup phones
                    for idx, phone in enumerate(session.phones):
                        phones[idx] = {"id": phone, "number": session.phones[phone].number}

                    while not valid_selection:
                        for idx, phone in enumerate(phones):
                            print(str(idx + 1) + ") " + phones[phone]['number'])

                        print("*) Exit")
                        current_phone = input("Select a phone: ")
                        print("")

                        if current_phone.isdigit() and int(current_phone) >= 1 and int(current_phone) <= len(phones):
                            valid_selection = True
                            current_menu = "select_phone_action"
                        elif current_phone == "*":
                            valid_selection = True
                            current_menu = "exit"

                # Action selection menu
                valid_selection = False
                current_action = 0

                while current_menu == "select_phone_action":
                    while not valid_selection:
                        phone_action_menu()

                        current_action = input("Select an option: ")
                        print("")

                        if current_action.isdigit() and int(current_action) >= 1 and int(current_action) <= 5:
                            valid_selection = True
                            current_menu = "action"
                        elif current_action == "*":
                            current_menu = "select_phone"

                # Add tool
                if current_action == "1":
                    valid_selection = False
                    selection = ""

                    while selection != "*":
                        # We need to figure out which tools aren't yet added.
                        uninstalled_tools = session.tools.copy()
                        uninstalled_tools_numbered = {}

                        for tool in session.phones[phones[int(current_phone) - 1]["id"]].tools:
                            uninstalled_tools.pop(tool)

                        for idx, tool in enumerate(uninstalled_tools):
                            print(str(idx + 1) + ") " + uninstalled_tools[tool]["label"])
                            uninstalled_tools_numbered[idx + 1] = tool

                        print("*) Back")
                        selection = input("Select tool: ")
                        print("")
                        
                        if selection.isdigit() and int(selection) >= 1 and int(selection) <= len(uninstalled_tools):
                            valid_selection = True
                            session.add_tool(session.phones[phones[int(current_phone) -1]["id"]].id, uninstalled_tools_numbered[int(selection)])
                        elif selection == "*":
                            current_menu = "select_phone_action"
                        else:
                            print("Invalid selection")

                # Remove tool
                elif current_action == "2":
                    installed_tools = {}
                    selection = "0"
                    valid_selection = False

                    while selection != "*":
                        for idx, tool in enumerate(session.phones[phones[int(current_phone) - 1]["id"]].tools):
                            print(str(idx + 1) + ") " + session.tools[tool]["label"])
                            installed_tools[idx] = tool

                        print("*) Back")
                        selection = input("Select tool: ")
                        print("")

                        if selection.isdigit() and int(selection) >= 1 and int(selection) <= len(session.phones[phones[int(current_phone) - 1]["id"]].tools):
                            valid_selection = True
                            session.delete_tool(session.phones[phones[int(current_phone) - 1]["id"]].tools[installed_tools[int(selection) - 1]])
                        elif selection == "*":
                            current_menu = "select_phone_action"
                        else:
                            print("Invalid selection")

