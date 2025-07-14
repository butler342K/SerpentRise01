import pickle
import colorama

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
    def get_upcoming_birthday(self):
        period_days = 7  # period for upcoming birthdays
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
            # if birthday was before today, set it to next year
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days
            if days_until_birthday <= period_days:
                if datetime.weekday(birthday_this_year) == 5:  # if birthday is on Saturday, move it to Monday
                    birthday_this_year += timedelta(days=2)
                elif datetime.weekday(birthday_this_year) == 6:  # if birthday is on Sunday, move it to Monday
                    birthday_this_year += timedelta(days=1)
                congratulation_date = datetime.strftime(birthday_this_year, '%Y.%m.%d')
                upcoming_birthdays.append(user)
        return upcoming_birthdays
    
    def save(self, args):
        filename, *_ = args
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
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

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
def upcoming_birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthday()
    if not upcoming_birthdays:
        print("No upcoming birthdays.")
    print("🎉 Upcoming birthdays: 🎉")
    for record in upcoming_birthdays:
        birthday = record.birthday.value
        print(f"{record.name.value}: {birthday.strftime('%d.%m')}") #  Show only day and month

def main():
    # book = AddressBook()
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Data saved. Exiting the assistant bot.")
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(contact_birthday(args, book))
        elif command == "birthdays":
            upcoming_birthdays(book)
        elif command == "save":
            book.save(args)
            print("Data saved.")
        elif command == "load":
            book = book.load(args)
            print("Data loaded.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()



