from colorama import Fore, Style, init

init(autoreset=True)

def print_help():
    """
    Display the list of available commands and their descriptions in the assistant bot.

    This function prints a formatted help menu showing all possible commands 
    supported by the assistant bot, including commands for managing contacts, 
    notes, birthdays, addresses, and data persistence.

    The output is colorized using the `colorama` library for better readability 
    in the terminal.

    Example output:
        hello               - Greet the assistant
        add-contact <name>  - Add a new contact

    No parameters are required.
    """
    print(" ")
    print(f"{Fore.CYAN}{Style.BRIGHT}=================== Assistant Bot Help ==================={Style.RESET_ALL}\n")
    commands = [
        ("hello", "Greet the assistant"),
        ("add-contact <name> [<phone1>] [<phone2>] ...", "Add a new contact. Name is required, phones are optional. You can add multiple phones at once."),
        ("change-contact <name> <old_phone> <new_phone>", "Change a contact's phone number"),
        ("delete-contact <name>", "Delete a contact"),
        ("search <keyword>", "Search contacts by name, phone, or email"),
        ("search-notes <tag>", "Search notes by tag"),
        ("search-notes-text <keyword>", "Search notes by text only"),
        ("phone <name>", "Show contact info"),
        ("all", "Show all contacts and notes"),
        ("all-notes", "Show all notes from all contacts"),
        ("add-email <name> <email>", "Add email to contact"),
        ("show-email <name>", "Show contact's email"),
        ("edit-email <name> <new_email>", "Edit contact's email"),
        ("remove-address <name>", "Remove contact's address"),
        ("add-address <name> <address>", "Add address to contact"),
        ("show-address <name>", "Show contact's address"),
        ("edit-address <name> <new_address>", "Edit contact's address"),
        ("add-note <name> <note_text>", "Add a note to contact"),
        ("edit-note <name> <note_id> <new_text> [<tags>]", "Edit a contact's note. Note ID is the first 8 characters of the note ID."),
        ("remove-note <name> <note_id>", "Remove a contact's note. Note ID is the first 8 characters of the note ID."),
        ("show-notes <name>", "Show contact's notes"),
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
