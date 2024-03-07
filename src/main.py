import curses
from curses_menu import Menu
from curses_textinput import SearchBar


import scrape
from selenium import webdriver




class App(object):
    def __init__(self, stdscr):
        self.driver = scrape.init()
        curses.curs_set(0)
        curses.use_default_colors()  # Use the default terminal background color
        curses.set_escdelay(25)
        curses.init_pair(1, curses.COLOR_RED, -1)  # Define a color pair
        curses.noecho()  # Turn off automatic echoing of keys

        self.screen = stdscr    # Initialize the window
        self.screen.keypad(True)  # Enable keypad mode
        self.height, self.width = self.screen.getmaxyx()


        self.menu_options  = ['Search', 'Download', 'Load', 'Update', 'Remove', 'About', 'Debug', 'Exit']
        self.search_fields = ["Name", "Username", "Email"]

        self.menu = Menu(self.screen, self.width // 4, max(self.height // 4, len(self.menu_options)) + 2, self.menu_options)
        self.menu_active = False


        while self.width < 128 or self.height < 48:
            self.tooSmall()

        self.current_screen = 'About'
        self.display()  # Initial display call to set up the screen





    def tooSmall(self):
        self.screen.addstr((self.height // 2) - 1, (self.width - len("Window Too Small")) // 2, "Window Too Small")  # Message for when the window is too small
        self.screen.addstr((self.height // 2), (self.width - len("Resize to 128x48")) // 2, "Resize to 128x48")
        self.screen.refresh()

        key = self.screen.getch()
        if key == curses.KEY_RESIZE:
            self.resized() 

    def display(self):

        if self.width < 128 or self.height < 48:
            self.tooSmall()
            return  # Return early if window is too small

        self.screen.clear()  # Clear the screen before redrawing
        self.screen.border()

        # Calculate the position to center the title
        self.screen.addstr(0, (self.width-len(' Pigeon '))//2, ' Pigeon ')  # Add a centered title at the top
        self.screen.addstr(0, 2,                               f' {self.current_screen} ') # Set the top left to the current screen
        self.screen.addstr(self.height-1, 2,                   ' ESC > Menu ') # Little navigation help at the bottom left
        self.screen.addstr(self.height-1, 16,                   ' UP/DOWN > Navigate ') # Little navigation help at the bottom left
        self.screen.addstr(self.height-1, 38,                   ' Q > Quit ') # Little navigation help at the bottom left



        if self.current_screen == 'About':
            self.about_screen()
        elif self.current_screen == 'Debug':
            self.debug_screen()
        elif self.current_screen == 'Search':
            self.search_screen()

        elif self.current_screen == 'Exit':
            curses.endwin()
            exit()

        else:
            self.screen.refresh()

        if self.menu_active:
            self.menu.display()  # Display the menu if it is active


    def resized(self):
        self.screen.clear()  # Clear the screen after resize
        self.height, self.width = self.screen.getmaxyx()
        if self.width < 128 or self.height < 48:
            self.tooSmall()  # Display the too small message if needed
            return  # Return early

        # Proceed with resizing logic if the window is big enough
        self.menu.resized(self.screen, self.width//4, max(self.height//4, len(self.menu_options))+2)
        self.screen.refresh()  # Refresh the screen



    def about_screen(self):
        # Clear previous content in the about section or ensure it doesn't overlap
        # self.screen.clear() might be too aggressive if you have other content you wish to preserve
        # Calculate the center for each line of text
        about_texts = [
        '                        ▒▒▒▒▒▒         ',
        '                        ▒▒▒▒▓▓         ',
        '                      ▓▓▒▒▓▓▒▒         ',
        '                      ▓▓▒▒▓▓▓▓         ',
        '                    ░░▒▒▒▒▓▓▓▓         ',
        '                  ░░▓▓▒▒▒▒▓▓▓▓▒▒       ',
        '                ▒▒▓▓▒▒▒▒▒▒▓▓▓▓▓▓       ',
        '              ▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓       ',
        '          ░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓       ',
        '          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████▓▓       ',
        '        ▓▓▓▓██▓▓▓▓▓▓▓▓▓▓▓▓████▓▓       ',
        '      ▓▓▓▓████████▒▒▓▓▓▓▓▓▓▓▓▓▒▒       ',
        '  ▒▒▓▓▒▒▓▓██▓▓████▒▒▓▓▓▓▓▓▓▓▒▒         ',
        '░░▓▓▓▓▒▒▒▒▓▓██████▓▓▓▓▓▓▓▓▓▓           ',
        '                ▓▓▓▓▒▒▓▓               ',
        '                ▒▒      ▒▒░░           ',
        '                  ░░                   ',
        'Pigeon V1.0',
        'Created 2024 by Cooper Pflaum',
        'Something Something MIT License',
        '',
        'Go follow me on Instagram:',
        '@cooper_pflaum @project__pigeon',
        'Also on Github! @Cooper-Pflaum',
        '',
        'Press ESC to get started',
        ]
        for i, text in enumerate(about_texts):

            start_y = (self.height//3)-5
            start_x = (self.width//2)-(len(text)//2)
            if text == '@cooper_pflaum @project__pigeon':
                self.screen.addstr(i + start_y, start_x, text, curses.color_pair(1))
            else:
                self.screen.addstr(i + start_y, start_x, text)

    
    def debug_screen(self):
        self.screen.addstr(1, 1, f' Window Size: {self.width}x{self.height} ')





    def search_screen(self):
        self.target_search = SearchBar(self.screen, 3,self.width//2,2, self.width//4,'Search Target')
        output_data = ""
        self.target_search.display(self.screen)  # Display before getting input
        if self.target_search.focused and not self.menu_active:
            self.target_output = self.target_search.get_input(self.screen)
            
            if self.target_output != None:
                output_data = scrape.find_user(self.target_output, self.driver)

                for i, data in enumerate(output_data):
                    if output_data[data] is not None:
                        self.screen.addstr(5+i*2, 4, f'{data}: {output_data[data]}')
                    else:
                        self.screen.addstr(5+i*2, 4, f'{data}: N/A')

                self.screen.addstr(20, 4, 'Press any key to continue...')

        curses.curs_set(0)
        self.screen.refresh()



    def run(self):
        while True:
            self.display()  # Call display to refresh the screen
            key = self.screen.getch()
            if key == curses.KEY_RESIZE:
                self.resized() 



            if self.menu_active:
                if key == 27:  # ESC key
                    self.menu_active = False
                    self.menu.navigate()

                elif key == curses.KEY_ENTER or key in [10, 13]: # If key is ENTER (10 - 13 needed to make it dissapear on selection)
                    self.current_screen = self.menu.select()
                    self.menu_active = False

                # This is because I like vim keybindings and I am a nerd
                elif key == curses.KEY_DOWN or key == ord('j'): 
                    self.menu.navigate(1)
                elif key == curses.KEY_UP or key == ord('k'):
                    self.menu.navigate(-1)

            else:
                if key == 27:  # ESC key
                    self.menu_active = True
                elif key == 113:  # 'q' key
                    break


def main(stdscr):
    app = App(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
