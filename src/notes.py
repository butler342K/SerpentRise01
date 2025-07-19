import pickle
import uuid
from colorama import Fore, Style, init

class Note:
    def __init__(self, text, tags=None):
        self.id = str(uuid.uuid4())
        self.text = text
        self.tags = tags if tags else []

    def __str__(self):
        tags_str = f"{Fore.BLUE} {', '.join(f'#{tag}' for tag in self.tags)}" if self.tags else ""
        return f"{Fore.LIGHTBLACK_EX}[{self.id[:8]}] {Fore.RESET}{self.text} {tags_str}"

class NotesBook:
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
                if tag in note.tags:
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
        return self.data.get(contact, [])
        
def save_data(book, filename="notesbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="notesbook.pkl"):
    try:
        with open(filename, "rb") as f:
            note = pickle.load(f)
            if not hasattr(note, 'search_by_text'):
                return NotesBook()
            return note
    except FileNotFoundError:
        return NotesBook()
    
