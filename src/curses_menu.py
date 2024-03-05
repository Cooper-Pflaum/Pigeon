import curses

class Menu(object):
    def __init__(self, stdscr, width, height, options):
        self.options = options
        self.height, self.width = stdscr.getmaxyx() 
        self.start_y = (self.height - height) // 2  # Calculate the starting y-coordinate for the subwindow
        self.start_x = (self.width - width) // 2    # Calculate the starting x-coordinate for the subwindow
        self.screen = stdscr.subwin(height, width, self.start_y, self.start_x)  # Create a subwindow centered on the screen
        self.width = width
        self.height = height + 1
        self.selected_index = 0


    def display(self):
        self.screen.clear()
        total_menu_height = len(self.options) + 2  # Total height of menu items plus top and bottom borders
        start_y = (self.height - total_menu_height) // 2  # Calculate the starting y-coordinate for the menu
        for idx, option in enumerate(self.options):
            # Center the option string within the width of the menu
            padded_option = "{:^{width}}".format(option, width=self.width-2)
            if idx == self.selected_index:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            # Calculate the x-coordinate to place the padded option string in the center
            x = (self.width - len(padded_option)) // 2
            # Add the centered padded option string to the screen at the calculated y-coordinate
            self.screen.addstr(start_y + idx, x, padded_option, mode)
        self.screen.border()
        self.screen.refresh()

    def select(self):
        # Handle the selected option here
        return self.options[self.selected_index]

    def navigate(self, n=0):
        self.selected_index += n
        if n == 0:
            self.selected_index = 0
        if self.selected_index < 0:
            self.selected_index = 0
        elif self.selected_index >= len(self.options):
            self.selected_index = len(self.options) - 1

    def resized(self, stdscr, width, height):
        self.height, self.width = stdscr.getmaxyx()

        self.start_y = (self.height - height) // 2  # Calculate the starting y-coordinate for the subwindow
        self.start_x = (self.width - width) // 2    # Calculate the starting x-coordinate for the subwindow
        self.screen = stdscr.subwin(height, width, self.start_y, self.start_x)  # Create a subwindow centered on the screen
        self.width = width
        self.height = height



