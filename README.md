# SerpentRise01
Personal assistant bot "TermiBook"

## Install
```bash
# скачати додаток з репозиторію
git clone https://github.com/butler342K/SerpentRise01.git
cd SerpentRise01

# створити віртуальне оточення
python -m venv .venv
source .venv/bin/activate       # для Linux/macOS
.venv\Scripts\activate          # для Windows

pip install -e .               # встановить усі потрібні залежності
# або
pip install -r requeriments.txt

## Run
termibook                      # запуск з будь-якого місця у віртуальному середовищі

## Help
type "help" to show full command list


## Опис роботи додатку
hello                                             - Greet the assistant
add-contact <name> [<phone1>] [<phone2>] ...      - Add a new contact. Name is required, phones are optional. You can add multiple phones at once.
change-contact <name> <old_phone> <new_phone>     - Change a contact's phone number
delete-contact <name>                             - Delete a contact
search <keyword>                                  - Search contacts by name, phone, or email
search-notes <tag>                                - Search notes by tag
search-notes-text <keyword>                       - Search notes by text only
phone <name>                                      - Show contact info
all                                               - Show all contacts and notes
all-notes                                         - Show all notes from all contacts
add-email <name> <email>                          - Add email to contact
show-email <name>                                 - Show contact's email
edit-email <name> <new_email>                     - Edit contact's email
remove-address <name>                             - Remove contact's address
add-address <name> <address>                      - Add address to contact
show-address <name>                               - Show contact's address
edit-address <name> <new_address>                 - Edit contact's address
add-note <name> <note_text>                       - Add a note to contact
edit-note <name> <note_id> <new_text> [<tags>]    - Edit a contact's note. Note ID is the first 8 characters of the note ID.
remove-note <name> <note_id>                      - Remove a contact's note. Note ID is the first 8 characters of the note ID.
show-notes <name>                                 - Show contact's notes
remove-email <name>                               - Remove contact's email
add-birthday <name> <DD.MM.YYYY>                  - Add birthday to contact
show-birthday <name>                              - Show contact's birthday
birthdays [days]                                  - Show upcoming birthdays
save [filename]                                   - Save address book
load [filename]                                   - Load address book
about                                             - Show info about the app
exit | close | quit                               - Exit the assistant
