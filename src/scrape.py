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
import chromedriver_autoinstaller







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


def scrape_user_data(username, driver, update=False):
    url = f'https://www.pixwox.com/profile/{username}/'

    info_dir = f'../captured_users/{username}/'
    info_file_path = os.path.join(info_dir, 'user.info')

    # Check if the user.info file exists and read its content
    if os.path.exists(info_file_path):
        with open(info_file_path, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                os.makedirs(info_dir, exist_ok=True)
                existing_data = {}
                update = True
    else:
        os.makedirs(info_dir, exist_ok=True)
        existing_data = {}
        update = True

    user_data = {}

    # Compare the existing data with the new data
    if update == True:
        # print('Fetching Profile')
        driver.get(url)
        # print('Fetched successfully')


        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')



            # Extract user data
        user_data = {
            'fullname':  soup.find('h1',  class_='fullname').text.strip()                                 if soup.find('h1',  class_='fullname') else None,
            'username':  soup.find('div', class_='username').text.strip()                                 if soup.find('div', class_='username') else None,
            'bio':       soup.find('div', class_='sum').text.strip().replace('\n', ' ')                   if soup.find('div', class_='sum') else None,
            'posts':     soup.find('div', class_='item_posts').find('div', class_='num').text.strip()     if soup.find('div', class_='item_posts') else None,
            'followers': soup.find('div', class_='item_followers').find('div', class_='num').text.strip() if soup.find('div', class_='item_followers') else None,
            'following': soup.find('div', class_='item_following').find('div', class_='num').text.strip() if soup.find('div', class_='item_following') else None,
        }

        # If the data has changed, update the user.info file
        with open(info_file_path, 'w') as file:
            json.dump(user_data, file, indent=2)
    else:
        # Read data from the existing file
        with open(info_file_path, 'r') as file:
            user_data = json.load(file)

# Return the user_data variable
    return user_data




def init():
    print('Initializing...')
    user_agent = UserAgent() # create a UserAgent instance

    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                          # and if it doesn't exist, download it automatically,
                                          # then add chromedriver to path

# Set up Selenium WebDriver (you need to have the appropriate webdriver for your browser)
# create a ChromeOptions instance
    options = webdriver.ChromeOptions()
# add a random user agent to our options
    options.add_argument(f'--test-type=gpu') # Helps to render stuff with the GPU
    options.add_argument(f'user-agent={user_agent.random}') # Changes the User Agent everytime so that it helps to avoid detection
    options.add_argument( '--headless') # Makes it run in the background

    options.add_experimental_option("useAutomationExtension", False) # Used to disable the automation and botting flags on chrome
    options.add_experimental_option("excludeSwitches",["enable-automation"])

    # start chrome with our custom options
    driver = webdriver.Chrome(options=options)
    return driver





if __name__ == "__main__":
    username_to_scrape = "therock"  # Replace with the desired Instagram username
    driver = init()
    
    scrape_user_data(username_to_scrape, driver)
    scrape_instagram_posts(username_to_scrape, driver)
