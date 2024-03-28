from textual import on
from textual.app import App, ComposeResult
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, RichLog, Log, Footer, Placeholder, Static
from textual.containers import Container, VerticalScroll
from textual_imageview.viewer import ImageViewer
from PIL import Image
import scrape



class UserInfoBox(Static):
    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.image = Image.open(f'../captured_users/{self.user_data["Username"].replace("@", "")}/{self.user_data["Username"].replace("@", "")}.png')
        self.image_viewer = ImageViewer(self.image)


    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Username:  ", classes="user-info-label"), Label(f"{self.user_data['Username']}",   classes="user-info-username"),
            Label(f"Full name: ", classes="user-info-label"), Label(f"{self.user_data['Fullname']}",   classes="user-info-fullname"),
            Label(f"Bio:       ", classes="user-info-label"), Label(f"{self.user_data['Bio']}",        classes="user-info-bio"),
            Label(f"Followers: ", classes="user-info-label"), Label(f"{self.user_data['Followers']}",  classes="user-info-followers"),
            Label(f"Following: ", classes="user-info-label"), Label(f"{self.user_data['Following']}",  classes="user-info-following"),
            Label(f"Posts:     ", classes="user-info-label"), Label(f"{self.user_data['Posts']}",      classes="user-info-posts"),
            Label(f"Private:   ", classes="user-info-label"), Label(f"{self.user_data['Private']}",    classes="user-info-private" if self.user_data['Private'] else "user-info-private false"),
            Label(f"Verified:  ", classes="user-info-label"), Label(f"{self.user_data['Verified']}",   classes="user-info-verified" if self.user_data['Verified'] else "user-info-verified false"),

            self.image_viewer,
        classes='User-data'
        )

class InputApp(App):
    CSS_PATH = "tui.tcss"
    BINDINGS = [("c-c", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Container(Input(placeholder="Search for user (Full name or @)", classes='User-Search'))
        yield VerticalScroll(id="users")
        yield Footer()

    @on(Input.Submitted, '.User-Search')
    def search(self, event: Input.Submitted) -> None:

        users = self.query('UserInfoBox')

        if users != None:
            users.remove()




        if '@' in self.query_one(Input).value:
            user_data = scrape.scrape_user_data(self.query_one(Input).value, driver)
            user_info_box = UserInfoBox(user_data)
            self.query_one("#users").mount(user_info_box)
            self.notify("Completed user query", severity="information", timeout=3)


        else:
            usernames = scrape.find_user(self.query_one(Input).value, driver)
            if usernames == None:
                self.notify("No user found", severity='error', timeout=3)
                pass
            elif len(usernames) == 1:
                user_data = scrape.scrape_user_data(usernames[0], driver)
                user_info_box = UserInfoBox(user_data)
                self.query_one("#users").mount(user_info_box)
                self.notify("Completed user query", severity="information", timeout=3)
            else:
                for username in usernames:
                    user_data = scrape.scrape_user_data(username, driver)
                    user_info_box = UserInfoBox(user_data)
                    self.query_one("#users").mount(user_info_box)
                self.notify("Completed user query", severity="information", timeout=3)

        self.query_one(Input).clear()

    def action_quit(self) -> None:
        driver.quit()
        self.exit()

app = InputApp()
driver = scrape.init()

if __name__ == "__main__":
    app.run()
