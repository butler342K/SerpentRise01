import pickle
from colorama import Fore, Style, init
import os
import prompt
import re
from note import NoteBook

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

class Email(Field):
    def __init__(self, email):
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")
        email = email.strip()
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            raise ValueError("Invalid email format.")
        self.value = email

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
        self.email = None
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
    def add_email(self, email):
        self.email = Email(email)

    def find_email(self):
        return self.email.value if self.email else None

    def edit_email(self, new_email):
        if not self.email:
            raise ValueError("Email is not set. Please add an email first.")
        self.email = Email(new_email)

    def remove_email(self):
        if not self.email:
            raise ValueError("Email is not set.")
        self.email = None
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        email_str = ""
        if hasattr(self, 'email') and self.email:
            email_str = f", email: {self.email.value}"
        birthday_str = ""
        if self.birthday:
            birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
        return f"Contact name: {self.name.value}, phones: {phones_str}{email_str}{birthday_str}"
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
            add-email <name> <email>
            show-email <name>
            edit-email <name> <new_email>
            remove-email <name>
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
def handle_add_email(args, book):
    name, email = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_email(email)
    return "Email added."

@input_error
def handle_show_email(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.email is None:
        return "Email is not set."
    return f"{name}'s email: {record.email.value}"

@input_error
def handle_edit_email(args, book):
    name, new_email = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_email(new_email)
    return "Email updated."

@input_error
def handle_remove_email(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.remove_email()
    return "Email removed."

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
        if hasattr(record, 'email') and record.email and keyword in record.email.value.lower():
            results.append(str(record))
    
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
    notes = NoteBook()

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
        elif command == "add-email":
            print(handle_add_email(args, book))
        elif command == "show-email":
            print(handle_show_email(args, book))
        elif command == "edit-email":
            print(handle_edit_email(args, book))
        elif command == "remove-email":
            print(handle_remove_email(args, book))
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
                # --- Note commands ---
        elif command == "add-note":
            if len(args) < 2:
                print("Usage: add-note <contact_name> <text>")
            else:
                contact_name = args[0]
                text = ' '.join(args[1:])
                note = notes.add_note(contact_name, text)
                print(f"Note added for {contact_name}: {note}")
        elif command == "list-notes":
            if not args:
                print("Usage: list-notes <contact_name>")
            else:
                contact_name = args[0]
                all_notes = notes.list_notes(contact_name)
                if not all_notes:
                    print(f"No notes for {contact_name}.")
                else:
                    print(f"Notes for {contact_name}:")
                    for idx, note in enumerate(all_notes, 1):
                        print(f"{idx}. {note}")
        elif command == "search-note":
            if len(args) < 2:
                print("Usage: search-note <contact_name> <keyword>")
            else:
                contact_name = args[0]
                keyword = ' '.join(args[1:])
                found = notes.search_notes(contact_name, keyword)
                if not found:
                    print(f"No notes found for {contact_name} with keyword '{keyword}'.")
                else:
                    print(f"Found notes for {contact_name}:")
                    for idx, note in enumerate(found, 1):
                        print(f"{idx}. {note}")
        elif command == "edit-note":
            if len(args) < 3:
                print("Usage: edit-note <contact_name> <number> <new_text>")
            else:
                contact_name = args[0]
                try:
                    idx = int(args[1]) - 1
                    new_text = ' '.join(args[2:])
                    if notes.edit_note(contact_name, idx, new_text):
                        print("Note updated.")
                    else:
                        print("Note not found.")
                except ValueError:
                    print("Invalid note number.")
        elif command == "delete-note":
            if len(args) < 2:
                print("Usage: delete-note <contact_name> <number>")
            else:
                contact_name = args[0]
                try:
                    idx = int(args[1]) - 1
                    if notes.delete_note(contact_name, idx):
                        print("Note deleted.")
                    else:
                        print("Note not found.")
                except ValueError:
                    print("Invalid note number.")
        # --- End note commands ---
        elif command == "help":
            pass
        elif command == "about":
            print(f"{Fore.LIGHTBLACK_EX}Produced by Serpent Rise Team©")
            #TODO
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()



