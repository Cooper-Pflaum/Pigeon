from textual import on
from textual.app import App, ComposeResult
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, RichLog, Log, Footer, Placeholder, Static, TextArea, Button
from textual.containers import Container, VerticalScroll
from textual_imageview.viewer import ImageViewer
import asyncio
from PIL import Image
import scrape


class UserInfoBox(Static):
    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                TextArea(f"Username:  ", classes="user-info-label"), TextArea(f"{self.user_data['Username']}",   soft_wrap=False, read_only=True, classes="user-info-username"),
                TextArea(f"Full name: ", classes="user-info-label"), TextArea(f"{self.user_data['Fullname']}",   soft_wrap=False, read_only=True, classes="user-info-fullname"),
                TextArea(f"Bio:       ", classes="user-info-label"), TextArea(f"{self.user_data['Bio']}",        soft_wrap=False, read_only=True, classes="user-info-bio"),
                TextArea(f"Followers: ", classes="user-info-label"), TextArea(f"{self.user_data['Followers']}",  soft_wrap=False, read_only=True, classes="user-info-followers"),
                TextArea(f"Following: ", classes="user-info-label"), TextArea(f"{self.user_data['Following']}",  soft_wrap=False, read_only=True, classes="user-info-following"),
                TextArea(f"Posts:     ", classes="user-info-label"), TextArea(f"{self.user_data['Posts']}",      soft_wrap=False, read_only=True, classes="user-info-posts"),
                TextArea(f"Private:   ", classes="user-info-label"), TextArea(f"{self.user_data['Private']}",    soft_wrap=False, read_only=True, classes="user-info-private"  if self.user_data['Private'] else "user-info-private false"),
                TextArea(f"Verified:  ", classes="user-info-label"), TextArea(f"{self.user_data['Verified']}",   soft_wrap=False, read_only=True, classes="user-info-verified" if self.user_data['Verified'] else "user-info-verified false"),
                # Button("Download") if self.user_data['Private'] == False else None,
            classes='user-data-text'
            ),
            ImageViewer(Image.open(f'../captured_users/{self.user_data["Username"].replace("@", "")}/{self.user_data["Username"].replace("@", "")}.png')),
            Button("Download", variant="success") if self.user_data['Private'] == False else Button("Download", disabled=True),

        classes='User-data'
        )

    async def download_user_posts(self):
        try:
            await scrape.scrape_instagram_posts(self.user_data['Username'], driver)
            self.notify("Successfully downloaded user's posts", severity="information", timeout=3)
        except Exception as e:
            self.notify(f"Error downloading posts: {str(e)}", severity="error", timeout=5)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        asyncio.create_task(self.download_user_posts())


class InputApp(App):
    CSS_PATH = "tui.tcss"
    BINDINGS = [("c-c", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Container(Input(placeholder="Search for user (Full name or @)", classes='User-Search'))
        yield VerticalScroll(id="users")
        yield Footer()

    @on(Input.Submitted, '.User-Search')
    def search(self, event: Input.Submitted) -> None:

        self.query_one(Input).loading = True

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

        self.query_one(Input).loading = False
        self.query_one(Input).clear()

    def action_quit(self) -> None:
        driver.quit()
        self.exit()

app = InputApp()
driver = scrape.init()

if __name__ == "__main__":
    app.run()
