import aiohttp
import asyncio
import json
import os
import random
import requests
import shutil
import threading
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from rich import print
from rich.progress import Progress
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller






def find_user(name, driver):
    name = name.replace(' ', '%20')
    url = f'https://www.picuki.com/search/{name}'
    driver.delete_all_cookies();


    driver.get(url)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-result-box")))
    driver.execute_script("window.stop();")
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    usernames = [username.text.strip() for username in soup.find_all('div', class_='result-username')]
    for uname in usernames:
        scrape_user_data(uname, driver)



def scrape_user_data(username, driver, update=True):
# Make sure that the usersnames that get returned don't have an @ symbol
# If they don't have one when getting passed in then it just skips over 
# And I don't have to worry about it
    username = username.replace('@','')


# Set up the directories for parsing the data
    user_dir = f'../captured_users/{username}/'     # Folder for storing the whole user
    user_json = os.path.join(user_dir, 'user.json') # JSON file for the user data

    user_data = {}                                  # Array for storing the captured data


# Check to see if there is already data on the user. 
# If there is, then skip the update and just read the user data back
# However if the user data doesn't exist, then update the data and write it to a json file
    if os.path.exists(user_json):
        with open(user_json, 'r') as json_file:
            try:
                user_data = json.load(json_file)
                update = False
            except json.JSONDecodeError:
                os.makedirs(user_dir, exist_ok=True)
                update = True
    else:
        os.makedirs(user_dir, exist_ok=True)
        update = True


    print ('\nUpdated: ' + str(update))
    # Compare the existing data with the new data
    if update == True:
        url = f'https://www.pixwox.com/profile/{username}/'
# Delete all cookies to get rid of any tracked data that the site uses
        driver.delete_all_cookies();

# Fetch the actual site
        driver.get(url)

# Wait until the page data loads in, and then stop the loading
        wait = WebDriverWait(driver, 5)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.fullname")))
        driver.execute_script("window.stop();")


# Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')



# Extract user data from the HTML
        user_data = {
            'Username':  soup.find('div', class_='username').text.strip()                                 if soup.find('div', class_='username') else None,
            'Fullname':  soup.find('h1',  class_='fullname').text.strip()                                 if soup.find('h1',  class_='fullname') else None,
            'Bio':       soup.find('div', class_='sum').text.strip().replace('\n', ' ')                   if soup.find('div', class_='sum') else None,
            'Posts':     soup.find('div', class_='item_posts').find('div', class_='num').text.strip()     if soup.find('div', class_='item_posts') else None,
            'Followers': soup.find('div', class_='item_followers').find('div', class_='num').text.strip() if soup.find('div', class_='item_followers') else None,
            'Following': soup.find('div', class_='item_following').find('div', class_='num').text.strip() if soup.find('div', class_='item_following') else None,
            'Private':                                                                                    True if soup.find('div', class_='notice') else False,
            'Verified':                                                                                   True if soup.find('span', class_='ident verified icon icon_verified') else False,
        }


        # If the data has changed, update the user.info file
        with open(user_json, 'w') as file:
            json.dump(user_data, file, indent=2)
    
    print(user_data)
    return user_data




async def download_image(url, index, session, path):
    async with session.get(url) as response:
        if response.status == 200:
            filename = os.path.join(path, f"image_{index}.jpg")
            with open(filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            # print(f"Downloaded: {url} as image_{index}.jpg")

async def download_images(urls, path):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(url, index, session, path) for index, url in enumerate(urls)]
        await asyncio.gather(*tasks)


async def process_post_data(post, post_count, save_dir):
    post_dir = os.path.join(save_dir, f'post_{post_count}')
    os.makedirs(post_dir, exist_ok=True)

    download_urls = [a.get('href') for a in post.find_all('a') if not a.get('href').startswith('/')]
    description = post.find('div', class_='sum').get_text(strip=True) if post.find('div', class_='sum') else "no description"
    likes = post.find('span', class_='count_item_like').get_text().replace('\n', '') if post.find('span', class_='count_item_like') else post.find('div', class_='count_item_like').get_text().replace('\n', '')
    comments = post.find('span', class_='count_item_comment').get_text().replace('\n', '') if post.find('span', class_='count_item_comment') else post.find('div', class_='count_item_comment').get_text().replace('\n', '')
    date = post.find('div', class_='time').get_text().replace('\n', '').replace('\n', '')
    hashtags = [tag.get_text() for tag in post.find('div', class_='sum').find_all('a') if tag.get_text().startswith('#')]
    mentions = [tag.get_text() for tag in post.find('div', class_='sum').find_all('a') if tag.get_text().startswith('@')]

    post_data = {
        'urls': download_urls,
        'description': description,
        'likes': likes,
        'comments': comments,
        'time_posted': date,
        'hashtags': hashtags,
        'mentions': mentions,
    }
    print(f'Post {post_count + 1}\n{post_data}\n')

    await download_images(download_urls, post_dir)


async def scrape_all_posts(parsed_posts, save_dir):
    tasks = []
    for post_count, post in enumerate(parsed_posts):
        task = asyncio.create_task(process_post_data(post, post_count, save_dir))
        tasks.append(task)

    await asyncio.gather(*tasks)

def scrape_instagram_posts(username, driver):

    # Load Instagram page
    url = f'https://www.pixwox.com/profile/{username}/'

    if driver.current_url != url:
        driver.delete_all_cookies();
        driver.get(url)


    with Progress(transient=True) as progress:
        scrolling_task = progress.add_task("[green]Scrolling...", total=None)  # Example total value

        while not progress.finished:
            old_height = driver.execute_script("return document.body.scrollHeight;")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.random()+0.5)  # Random delay

            new_height = driver.execute_script("return document.body.scrollHeight;")
            progress.update(scrolling_task, advance=5)

            if new_height == old_height:
                progress.update(scrolling_task, completed=100)  # Mark the task as completed
                break


# Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all the div elements with class 'post_box be-1'
    posts = soup.find_all('div', class_='post_box be-1')
# Loop through each post
    save_dir = f'../captured_users/{username}/posts'
    os.makedirs(save_dir, exist_ok=True)


    photo_count = 0
    post_count = 0
    print(f'Fetched Posts: {len(posts)}')
    # post_dir = save_dir+f'/post_{len(posts)-post_count}'

    with Progress(transient=True) as progress:
        downloading = progress.add_task("Downloading", total=None)  # Example total value

        while not progress.finished:
            progress.update(downloading, advance=1)
            asyncio.run(scrape_all_posts(posts, save_dir))
            progress.update(downloading, completed=100)  # Mark the task as completed
            break



def init():
    print('Initializing...')
    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                          # and if it doesn't exist, download it automatically,
                                          # then add chromedriver to path
    options = webdriver.ChromeOptions()

# add a random user agent to our chrome options (Helps to bypass page limits)
    user_agent = UserAgent()

# This gives me the ablity to cancel loading web pages and move on to the next page once a certain element appears 
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    options.page_load_strategy = 'none'

# Generic options
    options.add_argument(f'--test-type=gpu') # Helps to render stuff with the GPU
    options.add_argument(f'user-agent={user_agent.random}') # Changes the User Agent everytime so that it helps to avoid detection
    # options.add_argument( '--headless') # Makes it run in the background

# Disable botting and automation flags in chrome
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])

# start chrome with our custom options
    driver = webdriver.Chrome(options=options)
    return driver


if __name__ == "__main__":
    driver = init()
    
    while True:
        name = input('User to look for: ')
        usernames = find_user(name, driver)
    # scrape_instagram_posts(username_to_scrape, driver)

