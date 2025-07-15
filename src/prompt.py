from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

# Commands for autocompletion
commands = ['add-contact', 
            'change-phone', 
            'change-contact', 
            'delete-contact',
            'phone', 
            'add-birthday', 
            'show-birthday', 
            'birthdays', 
            'all', 
            'save',
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
