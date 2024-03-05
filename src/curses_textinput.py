import curses

class SearchBar:
    def __init__(self, stdscr, height, width, y, x, title):
        self.stdscr = stdscr
        self.search_win = self.stdscr.subwin(height, width, y, x)
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.title = title
        self.user_input = ""
        self.focused = True
        curses.curs_set(1)

    def display(self, screen=None):

        curses.curs_set(self.focused)


        self.search_win.border()
        self.search_win.addstr(0, 2, f" {self.title}: ")

        self.search_win.addstr(1, 1, self.user_input + " " * (self.width - len(self.user_input) - 2))
        self.search_win.refresh()

        if screen != None:
            screen.move(self.y+1,len(self.user_input) + (len(self.user_input)<self.width-2) + self.x) # Move the cursor to the end of the text and stops before overflowing the box
            screen.refresh()



    def get_input(self, screen=None):
        while True and self.focused:
            key = self.search_win.getch()
            if key == ord('\n'):  # Enter key pressed
                print('')
                return self.user_input
                self.user_input = ""
                break
            elif key == 27:
                self.focused = False
            elif key == 127:  # Backspace key pressed
                self.user_input = self.user_input[:-1]
            elif len(self.user_input) < self.width - 2:  # Input within the box width
                self.user_input += chr(key)
            self.display(screen)
