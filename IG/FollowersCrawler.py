import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


# 用於存 Follower 的資料
class User:
    def __init__(self, account: str, name: str) -> None:
        self.account = account  # Follower Account
        self.name = name  # Followers Name
        self.url = f"https://www.instagram.com/{account}"  # Followers Page Url


# 用於抓取 Instagram 指定用戶(target_account)的 Followers
def scrapingInstegramFollowers(
    login_account: str, login_password: str, target_account: str, max_scroll: int = 100
) -> list[User]:

    base_url = "https://www.instagram.com/"

    driver = webdriver.Chrome()  # 初始化 Chrome 瀏覽器
    driver.get(base_url)  # 打開 Instagram 首頁

    username = WebDriverWait(driver, timeout=60).until(
        lambda d: d.find_element(
            By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input'
        )
    )
    username.send_keys(login_account)  # 輸入用戶名

    password = driver.find_element(
        By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input'
    )
    password.send_keys(login_password)  # 輸入密碼

    # Click on Login Button
    enter = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
    enter.click()
    time.sleep(random.randint(4, 6))

    # Click on Not save in pop up
    not_save = driver.find_element(By.XPATH, "//div[@role = 'button']")
    not_save.click()
    time.sleep(random.randint(3, 6))

    # Click on Not Now in pop up
    not_now = driver.find_element(By.CSS_SELECTOR, "._a9_1")
    not_now.click()
    time.sleep(random.randint(3, 6))

    # Re-direact
    driver.get(url=f"{base_url}{target_account}")
    time.sleep(random.randint(3, 6))

    # Find follower's button
    followers_btn = driver.find_element(
        By.CSS_SELECTOR, f"a[href='/{target_account}/followers/']"
    )
    followers_btn.click()
    # time.sleep(2)
    # driver.refresh()

    time.sleep(random.randint(4, 6))
    # Get follower list
    followers_list = driver.find_element(By.CSS_SELECTOR, "div[class='_aano']")
    time.sleep(random.randint(4, 6))

    # Scroll the followers list to load all items
    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", followers_list
    )
    scroll_time = 0
    while True and scroll_time < max_scroll:
        # Scroll down to the bottom of the list
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", followers_list
        )
        scroll_time += 1

        # Wait for new items to load
        time.sleep(4)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", followers_list
        )
        if new_height == last_height:
            break
        last_height = new_height

    # Extract account from the followers list
    followers = followers_list.find_elements(By.CSS_SELECTOR, "a[role='link']")
    # Collect the follower account
    follower_account = [follower.text for follower in followers if follower.text != ""]

    # Extract name from the followers list
    followers = followers_list.find_elements(
        By.XPATH, ".//div[position()=2]//span/span"
    )
    # Collect the follower information
    follower_name = [follower.text for follower in followers]

    result = []
    for account, name in zip(follower_account, follower_name):
        result.append(User(account, name))

    return result


# Example:
result_list = scrapingInstegramFollowers(
    login_account="LOGINACCOUNT",
    login_password="LOGINPASSWORD",
    target_account="arielsvlog_816",
    max_scroll=50,
)
result_list[0].account  # First Follower Account
result_list[0].name  # First Follower Name
result_list[0].url  # First Follower Page Url

result_dict = []
for result in result_list:
    result_dict.append(
        {"account": result.account, "name": result.name, "url": result.url}
    )
