import curses

class SearchBar:
    def __init__(self, height, width, y, x, title):
        self.stdscr = curses.initscr()
        curses.noecho()  # Turn off automatic echoing of keys
        self.stdscr.keypad(True)  # Enable keypad mode

        self.search_win = curses.newwin(height, width, y, x)
        self.height = height
        self.width = width
        self.title = title
        self.user_input = ""

    def get_input(self):
        curses.curs_set(0)
        while True:
            self.search_win.border()
            self.search_win.addstr(0, 2, f" {self.title}: ")
            self.search_win.move(1,len(self.user_input)+(len(self.user_input) < self.width-2)) # Move the cursor to the end of the text and stops before overflowing the box

            key = self.search_win.getch()
            if key == ord('\n'):  # Enter key pressed
                break
            elif key == 127:  # Backspace key pressed
                self.user_input = self.user_input[:-1]
            elif len(self.user_input) < self.width-2: # Input to the edge of the box
                self.user_input += chr(key)

            self.search_win.addstr(1, 1, self.user_input + " " * (self.width - len(self.user_input) - 1))
            self.search_win.refresh()
        return self.user_input

    def close(self):
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

# Example of how to use the SearchBar class
search_bar = SearchBar(3, 50, 3, 0, 'Search')
output = search_bar.get_input()
search_bar.close()
print(output)
