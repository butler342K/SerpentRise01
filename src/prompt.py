from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

# Commands for autocompletion
commands = ['add-contact', 
            'change-contact', 'edit-contact','edit-phone',
            'delete-contact',
            'phone', 
            'add-email',
            'show-email',
            'edit-email',
            'remove-email',
            'add-birthday', 
            'show-birthday', 
            'add-address',
            'show-address',
            'edit-address',
            'remove-address',
            'birthdays', 
            'all', 
            'save',
            'search'
            'load',
            'close',
            'exit', 
            'quit',
            'help',
            'hello'
            ]

completer = WordCompleter(commands, ignore_case=True)

# History in memory
history = InMemoryHistory()

session = PromptSession(history=history)
