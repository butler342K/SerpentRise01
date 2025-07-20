class InvalidInputError(Exception):
    """
    Raised when the user provides invalid input to the assistant bot.

    Typically used for incorrect command formats or missing required arguments.
    """
    pass

class ContactNotFoundError(Exception):
    """
    Raised when a requested contact is not found in the address book.

    This exception helps to handle lookup errors gracefully.
    """
    pass

class EmailNotSetError(Exception):
    """
    Raised when attempting to edit or remove an email that has not been set for a contact.

    Prevents operations on non-existent email fields.
    """
    pass

class AddressNotSetError(Exception):
    """
    Raised when attempting to edit or remove an address that has not been set for a contact.

    Prevents operations on non-existent address fields.
    """
    pass

class PhoneNotFoundError(Exception):
    """
    Raised when attempting to edit or remove a phone number that does not exist for a contact.

    Helps to handle operations on invalid phone data.
    """
    pass

class AddressBookError(Exception):
    """
    Base class for all custom exceptions related to the Address Book.

    Can be used for generic address book errors when a more specific exception is not available.
    """
    pass
