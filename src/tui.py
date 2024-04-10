import asyncio
import scrape
from PIL import Image
from textual import on
from textual.app import App, ComposeResult
from textual_imageview.viewer import ImageViewer
from textual.containers import Container, VerticalScroll
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, RichLog, Log, Footer, Placeholder, Static, TextArea, Button


# Class for the user profile container
class UserInfoBox(Static):
    # import the scraped user data into the class for displaying
    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data

    # Widgets that are used to display the profile information
    def compose(self) -> ComposeResult:
        # Container to hold the whole profile
        yield Container(
            # Container to hold all the text information about a profile
            Container(
                TextArea(f"Username:  ", classes="user-info-label"), TextArea(f"{self.user_data['Username']}",   soft_wrap=False, read_only=True, classes="user-info-username"),
                TextArea(f"Full name: ", classes="user-info-label"), TextArea(f"{self.user_data['Fullname']}",   soft_wrap=False, read_only=True, classes="user-info-fullname"),
                TextArea(f"Bio:       ", classes="user-info-label"), TextArea(f"{self.user_data['Bio']}",        soft_wrap=False, read_only=True, classes="user-info-bio"),
                TextArea(f"Followers: ", classes="user-info-label"), TextArea(f"{self.user_data['Followers']}",  soft_wrap=False, read_only=True, classes="user-info-followers"),
                TextArea(f"Following: ", classes="user-info-label"), TextArea(f"{self.user_data['Following']}",  soft_wrap=False, read_only=True, classes="user-info-following"),
                TextArea(f"Posts:     ", classes="user-info-label"), TextArea(f"{self.user_data['Posts']}",      soft_wrap=False, read_only=True, classes="user-info-posts"),
                TextArea(f"Private:   ", classes="user-info-label"), TextArea(f"{self.user_data['Private']}",    soft_wrap=False, read_only=True, classes="user-info-private"  if self.user_data['Private'] else "user-info-private false"),
                TextArea(f"Verified:  ", classes="user-info-label"), TextArea(f"{self.user_data['Verified']}",   soft_wrap=False, read_only=True, classes="user-info-verified" if self.user_data['Verified'] else "user-info-verified false"),
                classes='user-data-text'
            ),
            # Terminal profile photo renderer
            ImageViewer(Image.open(f'../captured_users/{self.user_data["Username"].replace("@", "")}/{self.user_data["Username"].replace("@", "")}.png')),

            # Download button to download the posts of a user
            Button("Download", variant="success") if self.user_data['Private'] == False else Button("Download", disabled=True),
            classes='User-data'
        )

    # Async funciton to download the user posts. This is needed because the async function in the scrape library will error out if this is not here
    async def download_user_posts(self):
        try:
            await scrape.scrape_instagram_posts(self.user_data['Username'], driver)
            self.notify("Successfully downloaded user's posts", severity="information", timeout=3)
        except Exception as e:
            self.notify(f"Error downloading posts: {str(e)}", severity="error", timeout=5)

    # When the download button is pressed, then run the async download posts function
    def on_button_pressed(self, event: Button.Pressed) -> None:
        asyncio.create_task(self.download_user_posts())


# Main application class
class InputApp(App):

    CSS_PATH = "tui.tcss"
    BINDINGS = [("c-c", "quit", "Quit")]

    # Main app for UI
    def compose(self) -> ComposeResult:
        
        # Search Bar
        yield Container(Input(placeholder="Search for user (Full name or @)", classes='User-Search'))
        
        #Container to hold all the profiles
        yield VerticalScroll(id="users")

        # Displays key bindings
        yield Footer()

    # Called when the user presses enter from the search bar
    # TODO:
        # Fix the freeze that happens whenever you query based on person Search
    @on(Input.Submitted, '.User-Search')
    def search(self, event: Input.Submitted) -> None:

        # Set the loading bar animation on the search bar
        self.query_one(Input).loading = True

        # Setup the conatiner to add users
        users = self.query('UserInfoBox')
        if users != None:
            users.remove()

        # Direct username search
        if '@' in self.query_one(Input).value:
            user_data = scrape.scrape_user_data(self.query_one(Input).value, driver)
            user_info_box = UserInfoBox(user_data)
            self.query_one("#users").mount(user_info_box)
            self.notify("Completed user query", severity="information", timeout=3)

        else:
            # Run the find user function which returns a list of usernames
            usernames = scrape.find_user(self.query_one(Input).value, driver)

            # No users found
            if usernames == None:
                self.notify("No user found", severity='error', timeout=3)

            # One user found
            elif len(usernames) == 1:
                user_data = scrape.scrape_user_data(usernames[0], driver)

                # Add a new user container onto the screen
                user_info_box = UserInfoBox(user_data)
                self.query_one("#users").mount(user_info_box)
                
                self.notify("Completed user query", severity="information", timeout=3)

            else:
                for username in usernames:
                    user_data = scrape.scrape_user_data(username, driver)

                    # Add a new user container onto the screen
                    user_info_box = UserInfoBox(user_data)
                    self.query_one("#users").mount(user_info_box)
                
                self.notify("Completed user query", severity="information", timeout=3)


        # Diaable the loading animation and clear the search bar
        self.query_one(Input).loading = False
        self.query_one(Input).clear()

    # Closes the terminal app and the background chrome instance when the user presses CTRL + C
    def action_quit(self) -> None:
        driver.quit()
        self.exit()


# Main Function
if __name__ == "__main__":
    app = InputApp()
    driver = scrape.init()
    app.run()
