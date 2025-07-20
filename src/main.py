import pickle
from colorama import Fore, Style, init
import os
import prompt
import re
from notes import NotesBook, Note
import notes
from bot_help import print_help
from datetime import datetime, timedelta
from errors import (
    InvalidInputError, ContactNotFoundError, EmailNotSetError,
    AddressNotSetError, PhoneNotFoundError, AddressBookError
)
from pretty_table2 import draw_table
from prettytable import HRuleStyle, PrettyTable

def save_data(book, filename="addressbook.pkl"):
    """
    Save the address book to a file.

    Args:
        book (AddressBook): The address book to save.
        filename (str): File name to store the data. Defaults to "addressbook.pkl".
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """
    Load the address book from a file.

    Args:
        filename (str): File name to load the data from. Defaults to "addressbook.pkl".

    Returns:
        AddressBook: Loaded address book or new empty one if file not found.
    """
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            # Check for missing attributes and initialize them
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


class Field:
    """
    Base class for fields in a contact record (e.g., Name, Phone).
    """

    def __init__(self, value):
        """
        Initialize a field with a given value.

        Args:
            value (str): The field value.
        """
        self.value = value

    def __str__(self):
        """
        String representation of the field.

        Returns:
            str: The string value of the field.
        """
        return str(self.value)


class Name(Field):
    """
    Represents a contact's name.
    """

    def __init__(self, value):
        """
        Initialize a Name with validation.

        Args:
            value (str): Contact's name.

        Raises:
            ValueError: If the name is empty.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string.")
        self.value = value.strip()


class Phone(Field):
    """
    Represents a contact's phone number.
    """

    def __init__(self, phone):
        """
        Initialize a Phone with validation.

        Args:
            phone (str): The phone number.

        Raises:
            ValueError: If phone is not a string of 10 digits.
        """
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("Phone must be a non-empty string.")
        value = phone.strip()
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if len(value) != 10:
            raise ValueError("Phone number must be 10 digits long.")
        self.value = value


class Email(Field):
    """
    Represents a contact's email.
    """

    def __init__(self, email):
        """
        Initialize an Email with validation.

        Args:
            email (str): Email address.

        Raises:
            ValueError: If email is invalid.
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string.")
        email = email.strip()
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            raise ValueError("Invalid email format.")
        self.value = email


class Birthday(Field):
    """
    Represents a contact's birthday.
    """

    def __init__(self, value):
        """
        Initialize a Birthday with date validation.

        Args:
            value (str): Date in DD.MM.YYYY format.

        Raises:
            ValueError: If date is invalid or out of range.
        """
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
    """
    Represents a contact's address.
    """

    def __init__(self, value):
        """
        Initialize an Address with validation.

        Args:
            value (str): The address.

        Raises:
            ValueError: If address is too short or contains invalid characters.
        """
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
    """
    Represents a contact record in the address book.

    Attributes:
        name (Name): Contact's name.
        phones (list): List of Phone objects.
        email (Email): Contact's email (optional).
        birthday (Birthday): Contact's birthday (optional).
        notes (list): Notes associated with the contact (optional, stored externally).
        address (Address): Contact's address (optional).
    """

    def __init__(self, name):
        """
        Initialize a Record with the given name.

        Args:
            name (str): Contact's name.
        """
        self.name = Name(name)
        self.phones = []
        self.email = None
        self.birthday = None
        self.notes = []
        self.address = None

    def add_phone(self, phone):
        """
        Add a new phone number to the contact.

        Args:
            phone (str): Phone number to add.
        """
        if self.find_phone(phone):
            print(f"Phone {phone} already exists for {self.name.value}. Not adding.")
            return
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        """
        Remove a phone number from the contact.

        Args:
            phone (str): Phone number to remove.
        """
        phone_to_remove = Phone(phone)
        self.phones = [p for p in self.phones if p.value != phone_to_remove.value]

    def find_phone(self, phone):
        """
        Find a phone number in the contact's phone list.

        Args:
            phone (str): Phone number to find.

        Returns:
            str: The found phone number or None if not found.
        """
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("Phone must be a non-empty string.")
        phone = phone.strip()
        if any(p.value == phone for p in self.phones):
            return phone
        return None

    def edit_phone(self, old_phone, new_phone):
        """
        Edit a phone number by replacing old with new.

        Args:
            old_phone (str): Existing phone number to replace.
            new_phone (str): New phone number to set.

        Raises:
            ValueError: If old_phone is not found.
        """
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Phone number not found.")

    def add_email(self, email):
        """
        Add or update the contact's email.

        Args:
            email (str): Email address.
        """
        self.email = Email(email)

    def find_email(self):
        """
        Get the contact's email.

        Returns:
            str: Email value or None if not set.
        """
        return self.email.value if self.email else None

    def edit_email(self, new_email):
        """
        Edit the contact's email.

        Args:
            new_email (str): New email to set.

        Raises:
            ValueError: If email is not previously set.
        """
        if not self.email:
            raise ValueError("Email is not set. Please add an email first.")
        self.email = Email(new_email)

    def remove_email(self):
        """
        Remove the contact's email.

        Raises:
            ValueError: If email is not set.
        """
        if not self.email:
            raise ValueError("Email is not set.")
        self.email = None

    def add_address(self, address):
        """
        Add or update the contact's address.

        Args:
            address (str): The address.
        """
        self.address = Address(address)

    def edit_address(self, new_address):
        """
        Edit the contact's address.

        Args:
            new_address (str): New address to set.

        Raises:
            ValueError: If address is not previously set.
        """
        if not self.address:
            raise ValueError("Address is not set. Please add an address first.")
        self.address = Address(new_address)

    def remove_address(self):
        """
        Remove the contact's address.

        Raises:
            ValueError: If address is not set.
        """
        if not self.address:
            raise ValueError("Address is not set.")
        self.address = None

    def find_address(self):
        """
        Get the contact's address.

        Returns:
            str: Address value or None if not set.
        """
        return self.address.value if self.address else None

    def add_birthday(self, birthday):
        """
        Add or update the contact's birthday.

        Args:
            birthday (str): Birthday in format DD.MM.YYYY.
        """
        self.birthday = Birthday(birthday)

    def to_string(self, notes_book=None):
        """
        Return a string with full contact information.

        Args:
            notes_book (NotesBook, optional): NotesBook instance to fetch notes for this contact.

        Returns:
            str: Formatted contact details including phones, email, birthday, address, and notes.
        """
        notes_str = ""
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "no phones"
        email_str = f", email: {self.email.value}" if self.email else ""
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        address_str = f", address: {self.address.value}" if self.address else ""

        if notes_book:
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



class AddressBook(UserDict):
    """
    Represents an address book that stores contacts (Record instances).

    Inherits from:
        UserDict: A dictionary-like class for custom data structures.
    """

    def add_record(self, record: Record):
        """
        Add a new record (contact) to the address book.

        Args:
            record (Record): The contact to add.

        Raises:
            TypeError: If the provided object is not a Record.
        """
        if not isinstance(record, Record):
            raise TypeError("Only Record instances can be added.")
        self.data[record.name.value] = record

    def find(self, name):
        """
        Find a contact by name (case-insensitive).

        Args:
            name (str): Contact name to search for.

        Returns:
            Record: The found contact, or None if not found.

        Raises:
            ValueError: If the name is empty or not a string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        name_lower = name.strip().lower()
        for record_name, record in self.data.items():
            if record_name.lower() == name_lower:
                return record
        return None

    def delete(self, name):
        """
        Delete a contact from the address book.

        Args:
            name (str): Contact name to delete.

        Raises:
            ValueError: If the name is empty or not a string.
            KeyError: If the contact is not found.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        name = name.strip()
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact '{name}' not found.")

    def get_upcoming_birthday(self, period_days=7):
        """
        Get a list of contacts with upcoming birthdays.

        Args:
            period_days (int, optional): Number of days to look ahead. Default is 7.

        Returns:
            list: List of Record objects with upcoming birthdays.

        Raises:
            ValueError: If a birthday is not a Birthday instance.
        """
        self.period_days = period_days
        today = datetime.today()
        upcoming_birthdays = []

        for user in self.data.values():
            if not user.birthday:
                continue
            if not isinstance(user.birthday, Birthday):
                raise ValueError("Birthday must be an instance of Birthday class.")
            if not user.birthday.value:
                continue

            birthday = user.birthday.value
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days
            if days_until_birthday <= self.period_days:
                # Move to Monday if birthday is on weekend
                if datetime.weekday(birthday_this_year) == 5:
                    birthday_this_year += timedelta(days=2)
                elif datetime.weekday(birthday_this_year) == 6:
                    birthday_this_year += timedelta(days=1)
                upcoming_birthdays.append(user)

        return upcoming_birthdays

    def save(self, args):
        """
        Save the address book to a file.

        Args:
            args (list): Optional list containing filename as the first element.

        If no filename is provided, defaults to "addressbook.pkl".
        """
        filename = None
        if len(args) > 0:
            filename, *_ = args[0]
        if not filename:
            filename = "addressbook.pkl"
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    def load(self, args):
        """
        Load an address book from a file.

        Args:
            args (list): Optional list containing filename as the first element.

        Returns:
            AddressBook: Loaded address book object or new empty one if file not found.
        """
        if len(args) > 0:
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
    """
    Decorator to handle exceptions for user input and return friendly error messages.

    Args:
        func (function): Function to wrap.

    Returns:
        function: Wrapped function with error handling.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (InvalidInputError, ContactNotFoundError, EmailNotSetError, AddressNotSetError, PhoneNotFoundError, AddressBookError) as e:
            return str(e)
        except Exception as e:
            return f"{Fore.RED}Error occurred: {e}"
    return inner

def parse_input(user_input):
    """
    Parse user input into command and arguments.

    Args:
        user_input (str): Full command line input.

    Returns:
        tuple: command and list of arguments.
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    """
    Add a new contact or update existing one with additional phones.

    Args:
        args (list): List containing name and optional phone numbers.
        book (AddressBook): The address book to add the contact to.

    Returns:
        str: Confirmation message.
    """
    if not args:
        raise InvalidInputError("Please provide a name for the contact.")
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
    """
    Delete a contact by name.

    Args:
        args (list): List containing contact name.
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message or error.
    """
    if not args:
        raise InvalidInputError("Please provide a name to delete.")
    name, *_ = args
    if not name:
        raise InvalidInputError("Please provide a name to delete.")
    try:
        book.delete(name)
        return f"Contact '{name}' deleted."
    except KeyError:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

@input_error
def change_contact(args, book: AddressBook):
    """
    Change a contact's phone number.

    Args:
        args (list): [name, old_phone, new_phone]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 3:
        raise InvalidInputError("Please provide name, old phone, and new phone.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    user_phone = record.find_phone(old_phone)
    if user_phone is None:
        raise PhoneNotFoundError("Phone number not found.")
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    """
    Show phone numbers of a contact.

    Args:
        args (list): List containing contact name.
        book (AddressBook): The address book.

    Returns:
        str: Contact details.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    return record.to_string()

@input_error
def show_all(book: AddressBook, notes_book: NotesBook):
    """
    Display all contacts and their associated notes in a table.

    Args:
        book (AddressBook): The address book.
        notes_book (NotesBook): The notes book.
    """
    if not book.data:
        print("No contacts available.")
        return
    print(f"{Fore.GREEN}\U0001F4D7 All contacts: \U0001F4D7{Fore.RESET}")
    headers = [...]
    data = []
    for name, record in book.data.items():
        phones = ...
        email = ...
        birthday = ...
        address = ...
        note_str = " - "
        tag_str = " - "
        if notes_book:
            notes = notes_book.get_notes(record.name.value)
            if notes:
                notes_list = []
                tags_list = []
                for note in notes:
                    tags_list.append(...)
                    notes_list.append(f"📘 {note.text}")
                note_str = "\n".join(notes_list)
                tag_str = "\n".join(tags_list)
        data.append([...])
    table = draw_table(headers, data)
    print(table)

@input_error
def handle_add_email(args, book):
    """
    Add email to a contact.

    Args:
        args (list): [name, email]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 2:
        raise InvalidInputError("Please provide a name and email.")
    name, email = args
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.add_email(email)
    return "Email added."

@input_error
def handle_show_email(args, book):
    """
    Show contact's email.

    Args:
        args (list): [name]
        book (AddressBook): The address book.

    Returns:
        str: Email information.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    if record.email is None:
        raise EmailNotSetError("Email is not set.")
    return f"{name}'s email: {record.email.value}"

@input_error
def handle_edit_email(args, book):
    """
    Edit contact's email.

    Args:
        args (list): [name, new_email]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 2:
        raise InvalidInputError("Please provide a name and new email.")
    name, new_email = args
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.edit_email(new_email)
    return "Email updated."

@input_error
def handle_remove_email(args, book):
    """
    Remove email from contact.

    Args:
        args (list): [name]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.remove_email()
    return "Email removed."

@input_error
def add_birthday(args, book: AddressBook):
    """
    Add birthday to contact.

    Args:
        args (list): [name, birthday]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 2:
        raise InvalidInputError("Please provide a name and birthday.")
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def contact_birthday(args, book: AddressBook):
    """
    Show contact's birthday.

    Args:
        args (list): [name]
        book (AddressBook): The address book.

    Returns:
        str: Birthday information.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    if record.birthday is None:
        raise AddressBookError("Birthday not set.")
    birthday = record.birthday.value
    return f"{record.name.value}'s birthday is on {birthday.strftime('%d.%m.%Y')}."

@input_error
def upcoming_birthdays(args, book: AddressBook):
    """
    Show upcoming birthdays.

    Args:
        args (list): [days] (optional)
        book (AddressBook): The address book.
    """
    days = 7
    if len(args) > 0:
        try:
            days = int(args[0])
        except ValueError:
            raise InvalidInputError("Days must be an integer.")
    upcoming_birthdays = book.get_upcoming_birthday(days)
    if not upcoming_birthdays:
        print("No upcoming birthdays.")
        return
    print("🎉 Upcoming birthdays: 🎉")
    for record in upcoming_birthdays:
        birthday = record.birthday.value
        print(f"{record.name.value}: {birthday.strftime('%d.%m')}")

@input_error
def handle_add_address(args, book):
    """
    Add address to contact.

    Args:
        args (list): [name, address]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 2:
        raise InvalidInputError("Please provide a name and address.")
    name = args[0]
    address = ' '.join(args[1:])
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.add_address(address)
    return "Address added."

@input_error
def handle_show_address(args, book: AddressBook):
    """
    Show contact's address.

    Args:
        args (list): [name]
        book (AddressBook): The address book.

    Returns:
        str: Address information.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    if record.address is None:
        raise AddressNotSetError("Address is not set.")
    return f"{name}'s address: {record.address.value}"

@input_error
def handle_edit_address(args, book):
    """
    Edit contact's address.

    Args:
        args (list): [name, new_address]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if len(args) < 2:
        raise InvalidInputError("Please provide a name and new address.")
    name = args[0]
    new_address = ' '.join(args[1:])
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.edit_address(new_address)
    return "Address updated."

@input_error
def handle_remove_address(args, book):
    """
    Remove contact's address.

    Args:
        args (list): [name]
        book (AddressBook): The address book.

    Returns:
        str: Confirmation message.
    """
    if not args:
        raise InvalidInputError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError("Contact not found.")
    record.remove_address()
    return "Address removed."

@input_error
def search_contacts(args, book: AddressBook, notes_book: NotesBook):
    """
    Search contacts by name, phone, email, or address.

    Args:
        args (list): [keyword]
        book (AddressBook): The address book.
        notes_book (NotesBook): The notes book.

    Returns:
        str: Search results.
    """
    if not args:
        raise InvalidInputError("Please provide a search keyword.")

    keyword = args[0].lower()
    results = []

    for record in book.data.values():
        if keyword in record.name.value.lower():
            results.append(record.to_string(notes_book))
            continue
        for phone in record.phones:
            if keyword in phone.value:
                results.append(record.to_string(notes_book))
                break
        if hasattr(record, 'email') and record.email and keyword in record.email.value.lower():
            results.append(record.to_string(notes_book))
        if hasattr(record, 'address') and record.address and keyword in record.address.value.lower():
            results.append(record.to_string(notes_book))

    if results:
        return "\n".join(results)
    else:
        return "No matching contacts found."

@input_error
def handle_add_note(args, book: AddressBook, notes_book: NotesBook):
    """
    Add a note with optional tags to a contact.

    Args:
        args (list): [name, note_text, #tags...]
        book (AddressBook): The address book.
        notes_book (NotesBook): The notes book.

    Returns:
        str: Confirmation message.
    """
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
    """
    Display all notes from all contacts in a formatted table.

    Args:
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Formatted table of all notes.
    """
    notes = notes_book.get_all_notes()
    if not notes:
        return f"The notebook has no notes."
    print(f"{Fore.GREEN}📘 All notes: 📘{Fore.RESET}")
    headers = [
        f"{Fore.LIGHTGREEN_EX}id{Fore.RESET}",
        f"{Fore.LIGHTGREEN_EX}Name{Fore.RESET}",
        f"{Fore.LIGHTGREEN_EX}Note{Fore.RESET}",
        f"{Fore.LIGHTGREEN_EX}Tags{Fore.RESET}",
    ]
    data = []
    for contact, notes_list in notes.items():
        for note in notes_list:
            tags = f"{Fore.BLUE} {', '.join(f'#{tag}' for tag in note.tags)}{Fore.RESET}" if note.tags else f"{Fore.LIGHTBLACK_EX}no tags{Fore.RESET}"
            data.append([
                f"{Fore.LIGHTBLACK_EX}{note.id[:8]}{Fore.RESET}",
                f"{Fore.LIGHTMAGENTA_EX}{contact}{Fore.RESET}",
                f"{note.text}",
                tags
            ])
    table = draw_table(headers, data)
    return table

@input_error
def handle_show_notes(args, notes_book: NotesBook):
    """
    Display all notes for a specific contact.

    Args:
        args (list): [contact_name]
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Notes list or message if no notes.
    """
    contact = args[0]
    notes = notes_book.get_notes(contact)
    if not notes:
        return f"{contact} has no notes."
    return "\n".join(str(note) for note in notes)

@input_error
def handle_search_notes(args, notes_book):
    """
    Search notes by tag.

    Args:
        args (list): [tag]
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Notes matching the tag or message if not found.
    """
    tag = args[0]
    found = notes_book.search_by_tag(tag)
    if not found:
        return "No notes found with this tag."
    return "\n".join(f"{Fore.LIGHTMAGENTA_EX}{contact}{Fore.RESET}: {note}" for contact, note in found)

@input_error
def handle_search_notes_text(args, notes_book):
    """
    Search notes by text content.

    Args:
        args (list): [keyword(s)]
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Notes matching the text or message if not found.
    """
    if not args:
        return "Please provide a search keyword."

    keyword = ' '.join(args)
    found = notes_book.search_by_text(keyword)
    if not found:
        return "No notes found with this text."
    return "\n".join(f"{contact}: {note}" for contact, note in found)

@input_error
def handle_edit_note(args, notes_book):
    """
    Edit a note's text and tags for a specific contact.

    Args:
        args (list): [contact_name, note_id, new_text, #tags...]
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Update confirmation or error if note not found.
    """
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
    """
    Remove a note from a contact.

    Args:
        args (list): [contact_name, note_id]
        notes_book (NotesBook): The notes manager.

    Returns:
        str: Confirmation message.
    """
    contact, note_id = args
    notes_book.delete_note(contact, note_id)
    return "Note deleted."

def print_welcome():
    """
    Print the welcome message with ASCII art when the bot starts.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
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
    print(" "*18, f" {Fore.GREEN}{Style.BRIGHT}Welcome to TermiBook Assistant Bot!")
    print(" ")
    print(" "*15, f" {Fore.GREEN}{Style.BRIGHT}Type '{Fore.RED}help{Fore.GREEN}' for a list of commands.")
    print(" ")

# Assistant Bot for Address Book Management
def main():
    """
    Main function to run the TermiBook Assistant Bot.

    This function initializes the terminal assistant, loads the saved data (contacts and notes),
    and enters an infinite loop waiting for user commands. It supports various commands to manage:
    - Contacts (add, edit, delete, search, view phones, emails, addresses, birthdays)
    - Notes (add, edit, delete, search by tag or text)
    - Data persistence (save, load)
    - Help and information display.

    Commands are entered via a prompt with autocompletion.
    The bot continues running until the user types 'exit', 'close', or 'quit'.
    """
    init(autoreset=True)  # Initialize colorama for colored output
    print_welcome()
    # Load the address book data from file or create a new one
    book = load_data()
    notes_book = notes.load_data()

    while True:
        user_input = prompt.session.prompt("Enter a command >>> ", completer=prompt.completer, complete_while_typing=False)
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
            print(search_contacts(args, book, notes_book))
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
        elif command == "all-notes":
            print(handle_show_all_notes(notes_book))
        elif command == "search-notes":
            print(handle_search_notes(args, notes_book))
        elif command == "search-notes-text":
            print(handle_search_notes_text(args, notes_book))
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
            notes_book = notes.load_data()
            print("Data loaded.")
        elif command == "help":
            print_help()
        elif command == "about":
            print(" ")
            print(f"{Fore.GREEN}TermiBook Bot")
            print(f"{Fore.LIGHTBLACK_EX}Version: 1.0.0")
            print(f"{Fore.LIGHTBLACK_EX}Produced by Serpent Rise Team©")
            print(f"{Fore.LIGHTBLACK_EX}Support: slack.com/project-group_12")
            print(" ")
        else:
            print(f"{Fore.RED}Invalid command.")


if __name__ == "__main__":
    main()