# Pretty Notes Assistant Bot 🐍📒

**Pretty Notes Assistant Bot** is an interactive command-line assistant that combines an **Address Book** and **Note Manager** in one tool.  
It allows you to store and manage contacts, phone numbers, emails, addresses, birthdays, and notes with tags — all from the terminal!

Developed by **Serpent Rise Team©**.

---

## 🚀 Features

* 📇 Manage contacts: add, delete, edit  
* 📞 Manage multiple phone numbers per contact  
* 📧 Manage emails and addresses  
* 🎂 Track birthdays and upcoming birthday reminders  
* 📝 Attach notes to contacts with optional tags  
* 🔍 Search contacts and notes  
* 💾 Save/load data between sessions  
* 🎨 Colorful terminal interface (via `colorama`)

---

## 🛠️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/butler342K/SerpentRise01.git
```

### 2️⃣ Change to the Project Directory

```bash
cd SerpentRise01
```

### 3️⃣ Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

### 4️⃣ Activate the Virtual Environment

* **On Windows:**

```bash
.venv\Scripts\activate
```

* **On macOS/Linux:**

```bash
source .venv/bin/activate
```

### 5️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The main dependencies are:
>
> * `colorama`
> * `prompt_toolkit`

---

## 📝 How to Use

### Start the Assistant Bot

```bash
python main.py
```

You'll see a welcome message and can start typing commands.

---

### 📋 Commands Overview

| Command                                         | Description                                 |
| ----------------------------------------------- | ------------------------------------------- |
| `add-contact <name> <phone>`                    | Add a new contact with phone number         |
| `change-contact <name> <old_phone> <new_phone>` | Edit contact phone                          |
| `delete-contact <name>`                         | Delete a contact                            |
| `phone <name>`                                  | Show contact details                        |
| `add-email <name> <email>`                      | Add or update email                         |
| `show-email <name>`                             | Show contact email                          |
| `edit-email <name> <email>`                     | Edit email                                  |
| `remove-email <name>`                           | Remove email                                |
| `add-address <name> <address>`                  | Add or update address                       |
| `show-address <name>`                           | Show address                                |
| `edit-address <name> <new_address>`             | Edit address                                |
| `remove-address <name>`                         | Remove address                              |
| `add-birthday <name> <DD.MM.YYYY>`              | Add birthday                                |
| `show-birthday <name>`                          | Show birthday                               |
| `birthdays`                                     | Show upcoming birthdays (default 7 days)    |
| `add-note <name> <text> #tag1 #tag2`            | Add note with optional tags                 |
| `show-notes <name>`                             | Show all notes for a contact                |
| `search-notes <tag>`                            | Search notes by tag                         |
| `edit-note <name> <note_id> <new_text> #newtag` | Edit note                                   |
| `remove-note <name> <note_id>`                  | Remove a note                               |
| `search <keyword>`                              | Search contacts by name, phone, email, etc. |
| `all`                                           | Show all contacts and notes                 |
| `all-notes`                                     | Show all notes                              |
| `save`                                          | Save data to file                           |
| `load`                                          | Load data from file                         |
| `help`                                          | Show help menu                              |
| `about`                                         | Show project info                           |
| `exit`, `close`, `quit`                         | Save and exit the program                   |

---

## 💾 Data Persistence

All data is saved automatically to:

* **`addressbook.pkl`** — for contacts  
* **`notesbook.pkl`** — for notes

These files are created in the project directory.

---

## 🧑‍💻 Example Usage

```bash
add-contact John 1234567890
add-email John john@example.com
add-address John 123 Main St
add-birthday John 25.12.1990
add-note John Buy gift #birthday
search John
show-notes John
birthdays
all
all-notes
save
exit
```

---

## 🧰 Project Structure

```bash
├── src
    ├── main.py               # Main bot script
    ├── notes.py              # Notes module
    ├── bot_help.py           # Help functions
    ├── prompts.py            # Autocomplete functions
    ├── pretty_table2.py     # Table format output functions
├── addressbook.pkl       # Saved contacts (auto-generated)
├── notesbook.pkl         # Saved notes (auto-generated)
├── requirements.txt      # Python dependencies
```

---

## 🐍 About the Project

**Pretty Notes Bot**  
Version: 1.0.0  
Produced by: **Serpent Rise Team©**  

