class Note:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class NoteBook:
    def __init__(self):
        self.notes = {}

    def add_note(self, contact_name, text):
        note = Note(text)
        if contact_name not in self.notes:
            self.notes[contact_name] = []
        self.notes[contact_name].append(note)
        return note

    def list_notes(self, contact_name):
        return self.notes.get(contact_name, [])

    def search_notes(self, contact_name, keyword):
        return [note for note in self.notes.get(contact_name, []) if keyword.lower() in note.text.lower()]

    def edit_note(self, contact_name, index, new_text):
        notes = self.notes.get(contact_name, [])
        if 0 <= index < len(notes):
            notes[index].text = new_text
            return True
        return False

    def delete_note(self, contact_name, index):
        notes = self.notes.get(contact_name, [])
        if 0 <= index < len(notes):
            del notes[index]
            return True
        return False
