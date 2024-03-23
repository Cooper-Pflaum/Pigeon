from textual import on
from textual.app import App, ComposeResult
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, RichLog, Log, Footer
from textual.containers import Container
import scrape
import json

from rich.syntax import Syntax
from rich.table import Table








class InputApp(App):
    
    CSS_PATH = "tui.tcss"
    BINDINGS = [("c-c", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Container(Input(placeholder="Search for user (Full name or @)", classes='User-Search'))
        yield Container(RichLog(highlight=True, markup=True, wrap=False, auto_scroll=False), classes="main")
        yield Footer()

    @on(Input.Submitted, '.User-Search')
    def search(self, event: Input.Submitted) -> None:
        self.query_one(RichLog).clear()
        # Updating the UI to show the reasons why validation failed
        if '@' in self.query_one(Input).value:
            data = scrape.scrape_user_data(self.query_one(Input).value, driver)

            # Convert JSON data to a single string without quotation marks and brackets

            result = ''
            for key, value in data.items():
                result += f" {key}: {value}  \n"
            result = result.rstrip('\n')  # Remove the newline character at the end
            
            self.query_one(RichLog).write(result)

        else:

            usernames = scrape.find_user(self.query_one(Input).value, driver)
            
            if len(usernames) == 1:
                data = scrape.scrape_user_data(usernames[0], driver)

                # Convert JSON data to a single string without quotation marks and brackets

                result = ''
                for key, value in data.items():
                    result += f" {key}: {value}  \n"
                result = result.rstrip('\n')  # Remove the newline character at the end
                self.query_one(RichLog).write(result)
            elif usernames == None:
                self.query_one(RichLog).write('No users found')
            else:
                self.query_one(RichLog).write(usernames)



        self.query_one(Input).clear()

    def action_quit(self) -> None:
        driver.quit()
        self.exit()





app = InputApp()
driver = scrape.init()

if __name__ == "__main__":
    app.run()
