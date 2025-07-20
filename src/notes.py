import pickle
import uuid
from colorama import Fore, Style, init

class Note:
    """
    Represents a single note with optional tags.

    Attributes:
        id (str): Unique identifier for the note.
        text (str): The text content of the note.
        tags (list): Optional list of tags associated with the note.
    """    
    def __init__(self, text, tags=None):
        self.id = str(uuid.uuid4())
        self.text = text
        self.tags = tags if tags else []

    def __str__(self):
        tags_str = f"{Fore.BLUE} {', '.join(f'#{tag}' for tag in self.tags)}" if self.tags else ""
        return f"{Fore.LIGHTBLACK_EX}[{self.id[:8]}] {Fore.RESET}{self.text} {tags_str}"

class NotesBook:
    """
    Manages a collection of notes attached to contacts.

    Notes are stored as a dictionary where the key is the contact name,
    and the value is a list of Note instances.
    """    
    def __init__(self):
        self.data = {}  # key: contact name, value: list of Note

    def add_note(self, contact, note):
        if contact not in self.data:
            self.data[contact] = []
        self.data[contact].append(note)

    def edit_note(self, contact, note_id, new_text, new_tags):
        for note in self.data.get(contact, []):
            if note.id.startswith(note_id):
                note.text = new_text
                note.tags = new_tags
                return True
        return False

    def delete_note(self, contact, note_id):
        notes = self.data.get(contact, [])
        self.data[contact] = [n for n in notes if not n.id.startswith(note_id)]

    def search_by_tag(self, tag):
        results = []
        for contact, notes in self.data.items():
            for note in notes:
                if tag.lower() in (t.lower() for t in note.tags):
                    results.append((contact, note))
        return results
    
    def search_by_text(self, keyword):
        results = []
        for contact, notes in self.data.items():
            for note in notes:
                if keyword.lower() in note.text.lower():
                    results.append((contact, note))
        return results

    def get_notes(self, contact):
        """
        Retrieve all notes for a specific contact.

        Args:
            contact (str): The contact name.

        Returns:
            list: List of notes for the given contact.
        """
        return self.data.get(contact, [])
    
    def get_all_notes(self):
        """
        Retrieve all notes from all contacts.

        Returns:
            dict: Dictionary of contact names mapping to lists of notes.
        """
        return self.data
        
def save_data(book, filename="notesbook.pkl"):
    """
    Save the NotesBook to a file using pickle serialization.

    Args:
        book (NotesBook): The notes book to save.
        filename (str): The file name to save to. Defaults to 'notesbook.pkl'.
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="notesbook.pkl"):
    """
    Load a NotesBook from a file, or create a new one if the file is missing or incompatible.

    Args:
        filename (str): The file to load from. Defaults to 'notesbook.pkl'.

    Returns:
        NotesBook: The loaded NotesBook instance or a new empty one.
    """
    try:
        with open(filename, "rb") as f:
            note = pickle.load(f)
            if not hasattr(note, 'search_by_text'):
                return NotesBook()
            return note
    except FileNotFoundError:
        return NotesBook()
    
