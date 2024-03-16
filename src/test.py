import shutil

from prompt_toolkit import prompt
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

# Function to get the terminal width and height
def get_terminal_size():
    return shutil.get_terminal_size()

def get_terminal_width():
    return get_terminal_size().columns

def get_terminal_height():
    return get_terminal_size().lines

# Calculate border length based on terminal width and height
border_width = get_terminal_width() - 40  # Adjusted for options on the side
border_height = get_terminal_height() - 2  # Subtract 2 for borders on both sides

# Define the layout and style for the fullscreen application with dynamic border width and height
layout = Layout(
    container=HSplit([
        Window(
            FormattedTextControl(text='\n'.join([
                '┌' + '─' * border_width + '┐',
                *['│' + ' ' * border_width + '│' for _ in range(border_height)],
                '└' + '─' * border_width + '┘'
            ]))
        ),
        VSplit([
            Window(FormattedTextControl(text='Select Functionality:'), width=20),
            Window(FormattedTextControl(text='[ ] Option 1\n[ ] Option 2\n[ ] Option 3'), width=20)
        ])
    ])
)

style = Style.from_dict({
    'window': 'bg:#ffffff #000000',
})

# Key bindings for the application
kb = KeyBindings()

@kb.add('c-c') # CTRL+C
def _(event):
    event.app.exit()

# Create the application with the defined layout, style, and key bindings
app = Application(layout=layout, key_bindings=kb, style=style, full_screen=True)

# Run the application in fullscreen mode with dynamic border width and height
def run_app():
    app.run()

if __name__ == '__main__':
    run_app()
