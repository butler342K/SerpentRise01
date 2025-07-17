from colorama import Fore, Style, init

init(autoreset=True)

def print_help():
    print(" ")
    print(f"{Fore.CYAN}{Style.BRIGHT}=================== Assistant Bot Help ==================={Style.RESET_ALL}\n")
    commands = [
        ("hello", "Greet the assistant"),
        ("add-contact <name> [<phone1>] [<phone2>] ...", "Add a new contact. Name is required, phones are optional. You can add multiple phones at once."),
        ("change-contact <name> <old_phone> <new_phone>", "Change a contact's phone number"),
        ("delete-contact <name>", "Delete a contact"),
        ("search <keyword>", "Search contacts by name, phone, or email"),
        ("phone <name>", "Show contact info"),
        ("all", "Show all contacts"),
        ("add-email <name> <email>", "Add email to contact"),
        ("show-email <name>", "Show contact's email"),
        ("edit-email <name> <new_email>", "Edit contact's email"),
        ("remove-email <name>", "Remove contact's email"),
        ("add-birthday <name> <DD.MM.YYYY>", "Add birthday to contact"),
        ("show-birthday <name>", "Show contact's birthday"),
        ("birthdays [days]", "Show upcoming birthdays"),
        ("save [filename]", "Save address book"),
        ("load [filename]", "Load address book"),
        ("about", "Show info about the app"),
        ("exit | close | quit", "Exit the assistant"),
        ("help", "Show this help message")
    ]
    pad = 50
    for cmd, desc in commands:
        parts = []
        i = 0
        while i < len(cmd):
            if cmd[i] == '<':
                end = cmd.find('>', i)
                if end != -1:
                    parts.append(Fore.CYAN + Style.BRIGHT + cmd[i:end+1] + Style.RESET_ALL)
                    i = end + 1
                    continue
            if cmd[i] == '[':
                end = cmd.find(']', i)
                if end != -1:
                    parts.append(Fore.CYAN + Style.BRIGHT + cmd[i:end+1] + Style.RESET_ALL)
                    i = end + 1
                    continue
            parts.append(Fore.GREEN + cmd[i] + Style.RESET_ALL)
            i += 1
        colored_cmd = ''.join(parts)
        real_len = len(cmd)
        spaces = ' ' * max(2, pad - real_len)
        print(f"{colored_cmd}{spaces}{Fore.YELLOW}- {desc}{Style.RESET_ALL}")
    print(" ")
    print(f"{Fore.CYAN}{Style.BRIGHT}="*60, f"{Style.RESET_ALL}\n")



