import pickle
from colorama import Fore, Style, init
import os
import prompt

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 
    
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string.")
        self.value = value.strip()

class Phone(Field):
    def __init__(self, phone):
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("Phone must be a non-empty string.")
        value = phone.strip()
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        self.value = value
        if len(value) != 10:
            raise ValueError("Phone number must be 10 digits long.")

from datetime import datetime, date, timedelta        

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
            if self.value.year < 1900 or self.value > datetime.now():
                raise ValueError("Year must be between 1900 and the current year.")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Invalid date format. Use DD.MM.YYYY")
            else:
                raise ValueError(str(e))

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def add_phone(self, phone):
        if self.find_phone(phone):
            print(f"Phone {phone} already exists for {self.name.value}. Not adding.")
            return
        self.phones.append(Phone(phone))
    def remove_phone(self, phone):
        phone_to_remove = Phone(phone)
        self.phones = [p for p in self.phones if p.value != phone_to_remove.value]
    def find_phone(self, phone):
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("Phone must be a non-empty string.")
        phone = phone.strip()
        if any(p.value == phone for p in self.phones):
            return phone
        return None
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Phone number not found.")
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        # == show full information about contact ==   
        # return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, Birthday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'Not set'}"


class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise TypeError("Only Record instances can be added.")
        self.data[record.name.value] = record
    def find(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        if name.strip() not in self.data:
            return None
        return self.data[name.strip()]
    def delete(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        name = name.strip()
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact '{name}' not found.")   
    def get_upcoming_birthday(self, period_days=7):
        self.period_days = period_days # period for upcoming birthdays
        today = datetime.today()
        upcoming_birthdays = []

        for user in self.data.values():
            if not user.birthday:
                continue
            # Ensure birthday is a datetime object
            if not isinstance(user.birthday, Birthday):
                raise ValueError("Birthday must be an instance of Birthday class.")
            if not user.birthday.value:
                continue
            # Calculate the next birthday
            birthday = user.birthday.value
            birthday_this_year = birthday.replace(year=today.year)  
            # if birthday was before today, set it to next yeara
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days
            if days_until_birthday <= self.period_days:
                if datetime.weekday(birthday_this_year) == 5:  # if birthday is on Saturday, move it to Monday
                    birthday_this_year += timedelta(days=2)
                elif datetime.weekday(birthday_this_year) == 6:  # if birthday is on Sunday, move it to Monday
                    birthday_this_year += timedelta(days=1)
                congratulation_date = datetime.strftime(birthday_this_year, '%Y.%m.%d')
                upcoming_birthdays.append(user)
        return upcoming_birthdays
    
    def save(self, args):
        filename = None
        if len(args) > 0:
            filename, *_ = args[0]
        if not filename:
            filename = "addressbook.pkl"
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    def load(self, args):
        if len(args) >0:
            filename, *_ = args
        else:
            filename = "addressbook.pkl"
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            create_new = input("No saved data found. Start with an empty address book? [Y/N]")
            if create_new.lower() == 'y':
                return AddressBook()
            else:
                print("Staying with the current address book.")
                return self

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return """Invalid input. Format: 
            add <name> <phone_number>
            change <name> <old_phone> <new_phone>
            phone <name>
            add-birthday <name> <DD.MM.YYYY>
            show-birthday <name>
            birthdays
            all"""
        except IndexError: # not used now
            return "Invalid input. Format: phone <name>."
        except KeyError: # not used now
            return "Contact not found."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if len(args) > 1:
        for phone in args[1:]:
            record.add_phone(phone)
    return message

@input_error
def delete_contact(args, book: AddressBook):
    name = None
    if len(args) == 0:
        return "Please provide a name to delete."
    name, *_ = args
    if not name:
        return "Please provide a name to delete."
    try:
        book.delete(name)
        return f"Contact '{name}' deleted."
    except KeyError as e:
        return str(e)

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    user_phone = record.find_phone(old_phone)
    if user_phone is None:
        return "Phone number not found."
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return record

@input_error
def show_all(book: AddressBook):
    if not book.data:
        print("No contacts available.")
        return
    print("📗 All contacts: 📗\n")
    for name, record in book.data.items():
        print(record)  

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def contact_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday is None:
        return "Birthday not set."
    birthday = record.birthday.value
    return f"{record.name.value}'s birthday is on {birthday.strftime('%d.%m.%Y')}."

@input_error
def upcoming_birthdays(args, book: AddressBook):
    days = 7  # Default period for upcoming birthdays
    if len(args) > 0:
        days = int(args[0])
    upcoming_birthdays = book.get_upcoming_birthday(days)
    if not upcoming_birthdays:
        print("No upcoming birthdays.")
    print("🎉 Upcoming birthdays: 🎉")
    for record in upcoming_birthdays:
        birthday = record.birthday.value
        print(f"{record.name.value}: {birthday.strftime('%d.%m')}") #  Show only day and month

@input_error
def search_contacts(args, book: AddressBook):
    if not args:
        return "Please provide a search keyword."

    keyword = args[0].lower()
    results = []

    for record in book.data.values():
        if keyword in record.name.value.lower():
            results.append(str(record))
            continue
        for phone in record.phones:
            if keyword in phone.value:
                results.append(str(record))
                break

    if results:
        return "\n".join(results)
    else:
        return "No matching contacts found."



def print_welcome():
    if os.name == 'nt':
        os.system('cls')
    else:
        # For Unix-like systems (Linux, macOS)
        os.system('clear')
    cobra = r"""

                /^\/^\
                _|__|  O|
        \/     /~     \_/ \
        \____|__________/  \
                \_______      \
                        `\     \                 \
                        |     |                  \
                        /      /                    \
                        /     /                       \\
                    /      /                         \ \
                    /     /                            \  \
                /     /             _----_            \   \
                /     /           _-~      ~-_         |   |
                (      (        _-~    _--_    ~-_     _/   |
                \      ~-____-~    _-~    ~-_    ~-_-~    /
                    ~-_           _-~          ~-_       _-~
                    ~--______-~                ~-___-~
        """
    print(f"{Fore.GREEN}{Style.BRIGHT}{cobra}")
    print(" "*18, f" {Fore.GREEN}{Style.BRIGHT}Welcome to the Assistant Bot!")
    print(" ")
    print(" "*15, f" {Fore.GREEN}{Style.BRIGHT}Type '{Fore.RED}help{Fore.GREEN}' for a list of commands.")
    print(" ")

# Assistant Bot for Address Book Management
def main():
    init(autoreset=True) # Initialize colorama for colored output
    print_welcome() 
    # Load the address book data from file or create a new one
    book = load_data()

    while True:
        user_input = prompt.session.prompt("Enter a command >>> ", completer=prompt.completer, complete_while_typing=False)
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "quit"]:
            save_data(book)
            print("Data saved. Exiting the assistant bot.")
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add-contact":
            print(add_contact(args, book))
        elif command == "change-contact":
            print(change_contact(args, book))
        elif command == "delete-contact":
            print(delete_contact(args, book))
        elif command == "search":
            print(search_contacts(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(contact_birthday(args, book))
        elif command == "birthdays":
            upcoming_birthdays(args, book)
        elif command == "save":
            book.save(args)
            print("Data saved.")
        elif command == "load":
            book = book.load(args)
            print("Data loaded.")
        elif command == "help":
            print_help()
        elif command == "about":
            print(f"{Fore.LIGHTBLACK_EX}Produced by Serpent Rise Team©")
            #TODO
        else:
            print("Invalid command.")

def print_help():
    print(f"{Fore.CYAN}{Style.BRIGHT}=== Assistant Bot Help ==={Style.RESET_ALL}\n")
    commands = [
        ("hello", "Greet the assistant"),
        ("add-contact <name> [<phone1>] [<phone2>] ...", "Add a new contact. Name is required, phones are optional. You can add multiple phones at once."),
        ("change-contact <name> <old_phone> <new_phone>", "Change a contact's phone number"),
        ("delete-contact <name>", "Delete a contact"),
        ("phone <name>", "Show contact info"),
        ("all", "Show all contacts"),
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
    print(f"\n{Fore.CYAN}{Style.BRIGHT}========================={Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()




