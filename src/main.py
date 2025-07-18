import pickle
from colorama import Fore, Style, init
import os
import prompt
import re
from notes import NotesBook, Note
import notes
from bot_help import print_help

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            # Check if the book has the necessary attributes
            for record in book.data.values():
                if not hasattr(record, 'address'):
                    record.address = None
                if not hasattr(record, 'email'):
                    record.email = None
                if not hasattr(record, 'birthday'):
                    record.birthday = None
            return book
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

class Address(Field):
    def __init__(self, value):
        if not value.strip():
            self.value = None
            return
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Address is too short.")
        if re.search(r"[<>@#$%^&*]", value):
            raise ValueError("Address contains invalid characters.")
        self.value = value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = None
        self.birthday = None
        self.notes = []
        self.address = None
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
    def add_address(self, address):
        self.address = Address(address)
    def edit_address(self, new_address):
        if not self.address:
            raise ValueError("Address is not set. Please add an address first.")
        self.address = Address(new_address)
    def remove_address(self):
        if not self.address:
            raise ValueError("Address is not set.")
        self.address = None
    def find_address(self):
        return self.address.value if self.address else None
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    def to_string(self, notes_book):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "no phones"
        email_str = f", email: {self.email.value}" if self.email else ""
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        address_str = f", address: {self.address.value}" if self.address else ""
        notes = notes_book.get_notes(self.name.value)
        if notes:
            notes_list = []
            for note in notes:
                note_tags = f"{Fore.BLUE} {', '.join(f'#{tag}' for tag in note.tags)}" if note.tags else f"{Fore.LIGHTBLACK_EX}no tags{Fore.RESET}"
                notes_list.append(f"{Fore.LIGHTBLACK_EX}[{note.id[:8]}]{Fore.RESET} {note.text} {note_tags}")
            notes_str = f"\n    {Fore.GREEN}Notes:{Fore.RESET}\n    " + "\n    ".join(notes_list)
        else:
            notes_str = f"\n    {Fore.GREEN}Notes:{Fore.RESET} no notes"

        return f"Contact name: {self.name.value}, phones: {phones_str}{email_str}{birthday_str}{address_str}{notes_str}"

        # == show full information about contact ==   
        # return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, Birthday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'Not set'}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
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
            create_new = input("No saved data found. Start with an empty address book? [Y/N] ")
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
            add-address <name> <address>
            show-address <name>
            edit-address <name> <new_address>
            remove-address <name>
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
def show_all(book: AddressBook, notes_book: NotesBook):
    if not book.data:
        print("No contacts available.")
        return
    print("📗 All contacts: 📗\n")
    for name, record in book.data.items():
        print(record.to_string(notes_book)) 

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
def handle_add_address(args, book):
    if len(args) < 2:
        return "Please provide a name and address."

    name = args[0]
    address = ' '.join(args[1:])  # <--- join remaining parts into the address string

    record = book.find(name)
    if record is None:
        return "Contact not found."

    record.add_address(address)
    return "Address added."

@input_error
def handle_show_address(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.address is None:
        return "Address is not set."
    return f"{name}'s address: {record.address.value}"

@input_error
def handle_edit_address(args, book):
    if len(args) < 2:
        return "Please provide a name and new address."

    name = args[0]
    new_address = ' '.join(args[1:])  # join the rest

    record = book.find(name)
    if record is None:
        return "Contact not found."

    record.edit_address(new_address)
    return "Address updated."

@input_error
def handle_remove_address(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.remove_address()
    return "Address removed."


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
        if hasattr(record, 'address') and record.address and keyword in record.address.value.lower():
            results.append(str(record))
    
    if results:
        return "\n".join(results)
    else:
        return "No matching contacts found."

@input_error
def handle_add_note(args, book: AddressBook, notes_book: NotesBook):
    if len(args) < 2:
        return "Please provide a contact name and note text."

    contact, *note_parts = args
    record = book.find(contact)

    if record is None:
        return f"Contact '{contact}' not found."

    tags = []
    text = []
    for part in note_parts:
        if part.startswith("#"):
            tags.append(part[1:])
        else:
            text.append(part)

    if not text:
        return "Note text cannot be empty."

    note = Note(" ".join(text), tags)
    notes_book.add_note(contact, note)

    return "Note added."



@input_error
def handle_show_all_notes(notes_book: NotesBook):
    notes = notes_book.get_notes(contact)
    if not notes:
        return f"{contact} has no notes."
    return "\n".join(str(note) for note in notes)

@input_error
def handle_show_notes(args, notes_book: NotesBook):
    contact = args[0]
    notes = notes_book.get_notes(contact)
    if not notes:
        return f"{contact} has no notes."
    return "\n".join(str(note) for note in notes)

@input_error
def handle_search_notes(args, notes_book):
    tag = args[0]
    found = notes_book.search_by_tag(tag)
    if not found:
        return "No notes found with this tag."
    return "\n".join(f"{contact}: {note}" for contact, note in found)

@input_error
def handle_edit_note(args, notes_book):
    contact, note_id, *new_parts = args
    tags = []
    text = []
    for part in new_parts:
        if part.startswith("#"):
            tags.append(part[1:])
        else:
            text.append(part)
    if not text:
        return "New note text cannot be empty."
    success = notes_book.edit_note(contact, note_id, " ".join(text), tags)
    return "Note updated." if success else "Note not found."

@input_error
def handle_remove_note(args, notes_book):
    contact, note_id = args
    notes_book.delete_note(contact, note_id)
    return "Note deleted."



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
    notes_book = notes.load_data()

    while True:
        user_input = prompt.session.prompt(f"Enter a command >>> ", completer=prompt.completer, complete_while_typing=False)
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "quit"]:
            save_data(book)
            notes.save_data(notes_book)
            print("Data saved. Exiting the assistant bot.")
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add-contact":
            print(add_contact(args, book))
        elif command in ["change-contact", "edit-contact", "edit-phone"]:
            print(change_contact(args, book))
        elif command == "delete-contact":
            print(delete_contact(args, book))
        elif command == "search":
            print(search_contacts(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book, notes_book)
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
        elif command == "add-note":
            print(handle_add_note(args, book, notes_book))
        elif command == "show-notes":
            print(handle_show_notes(args, notes_book))
        elif command == "search-notes":
            print(handle_search_notes(args, notes_book))
        elif command == "edit-note":
            print(handle_edit_note(args, notes_book))
        elif command == "remove-note":
            print(handle_remove_note(args, notes_book))
        elif command == "add-address":
            print(handle_add_address(args, book))
        elif command == "show-address":
            print(handle_show_address(args, book))
        elif command == "edit-address":
            print(handle_edit_address(args, book))
        elif command == "remove-address":
            print(handle_remove_address(args, book))
        elif command == "save":
            book.save(args)
            notes.save_data(notes_book)
            print("Data saved.")
        elif command == "load":
            book = book.load(args)
            print("Data loaded.")
        elif command == "help":
            print_help()
        elif command == "about":
            print(" ")
            print(f"{Fore.GREEN}Pretty Notes Bot")
            print(f"{Fore.LIGHTBLACK_EX}Version: 1.0.0")
            print(f"{Fore.LIGHTBLACK_EX}Produced by Serpent Rise Team©")
            print(f"{Fore.LIGHTBLACK_EX}Support: slack.com/project-group_12")
            print(" ")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()



