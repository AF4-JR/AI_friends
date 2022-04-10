from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pynput.keyboard import Key, Controller
from selenium import webdriver

import re
import time
import logger
import vars as v
import datetime as d


def clean_message(text):
    """
    # Cleans text of characters that cannot be typed

     - Bad Characters:\n
    u"\U0001F600-\U0001F64F"  # emoticons\n
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs\n
    u"\U0001F680-\U0001F6FF"  # transport & map symbols\n
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)\n


    :param text: Text containing bad characters
    :return: The clean text
    """
    cleaner = re.compile("["   u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    return cleaner.sub(r'', text).strip()


def pass_cookies(ai):
    """
    # Deal with cookies pop-up. Accepts the cookies to clear the ui

    :param ai: The ai browser window to accept cookies for
    :return: None
    """
    ai_1_cookies = ai.find_element(By.CSS_SELECTOR, v.cookies_accept_id)
    ai_1_cookies.click()


def min_max_windows(window, window2):
    """
    # Swap windows - minimizing first, maximizing second

    :param window: The first browser window - will be minimized
    :param window2: The second browser window - will be maximized
    :return: None
    """
    time.sleep(1)
    window.minimize_window()
    time.sleep(0.5)
    window2.maximize_window()
    time.sleep(0.5)


def login(ai, username, password):
    """
    # Login username and password

    :param ai: The ai to login as
    :param username: Username field
    :param password: Password field
    :return:
    """
    # email
    ai_email_elem = ai.find_element(By.ID, v.login_email_id)
    ai_email_elem.send_keys(username)
    ai_email_next_btn = ai.find_element(By.CSS_SELECTOR, v.login_email_next_btn)
    ai_email_next_btn.click()
    time.sleep(1)
    # password
    ai_password_elem = ai.find_element(By.ID, v.login_password_id)
    ai_password_elem.send_keys(password)
    ai_password_next_btn = ai.find_element(By.CSS_SELECTOR, v.login_email_next_btn)
    ai_password_next_btn.click()
    time.sleep(2)
    pass_cookies(ai)


def collect_messages(ai):
    """
    # Collect messages from ai browser window, cleaning the text in the process\n

    :param ai: Collect messages from this ai
    :return: All messages available in the ai window. These messages are cleaned of bad/invalid characters that cannot be typed, and stripped of leading/trailing spaces
    """
    messages = []
    # collect ai message IDs
    ai_message_elements = ai.find_elements(By.XPATH, v.messages_XPATH)
    # fill ai messages array
    for i in ai_message_elements:
        for j in i.find_elements(By.XPATH, ".//*"):
            messages.append(clean_message(j.text.strip()))
    return messages


def get_last_messages(destination_ai, source_ai_messages):
    """
    # Returns a maximum of 3 messages that have not been sent from the 3 most recent source messages. The ai can only send a maximum of 3 messages at a time -
    Using the most recent 3 messages from the source ai, we check to see if they exist in the last 6 messages from the destination ai.
    If any of the 3 most recent source messages do not exist in any of the 6 most recent destination messages, these source messages have not been sent and are returned.

    :param destination_ai: The destination window where the messages are being sent
    :param source_ai_messages: Array containing source ai messages
    :return: Array of 3 or less messages that have not been sent yet
    """
    last_messages = []

    # pull all messages in destination window
    destination_messages_temp = collect_messages(destination_ai)

    # get last 3 potential messages from source
    potential_messages = source_ai_messages[-3:]  # chat bot can only send up to 3 new messages at a time
    destination_messages = destination_messages_temp[-6:]  # only need to check maximum of last 6 messages from destination - due to both bots potentially sending 3 messages each

    # output debug info
    if isDebug == 1:
        print("\nDestination messages: \n")
        print(destination_messages)
        print("\nPotential source messages: \n")
        print(potential_messages)

    # for each message in potential messages
    for msg in potential_messages:
        if msg not in destination_messages:  # if message is not in target windows last 6 messages
            last_messages.append(msg)  # message needs to be sent

    if isDebug == 1:
        print("\nActual messages sent: \n")
        print(last_messages)

    return last_messages


def type_messages(destination_ai, messages):
    """
    # Types and sends [messages] to the [destination_ia]. Types all messages in messages array as individual messages\n
    # Will not send the messages if debug mode is on, will only provide logs and console output. Debug must be off for messages to send.

    :param destination_ai: The ai that is receiving the messages
    :param messages: The list of messages from [from_ai]
    :return: The messages sent
    """
    # get text input element for message destination
    ai_message_input = destination_ai.find_element(By.ID, v.send_message_id)

    ai_message_input.click()  # set cursor on text input

    # need to handle characters that cannot be typed
    for msg in messages:  # for each message
        for j in msg:  # for each character in each message
            try:  # try to type character
                keyboard.press(j)
                keyboard.release(j)
            except Exception as error:
                logger.write(v.full_log_file, "Failed to print: " + str(j) + ". \n Reason: " + str(error))
        if isDebug == 0:  # only enter text if not in debug mode
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        else:  # type a space between messages if in debug mode
            keyboard.press(Key.space)
            keyboard.release(Key.space)
    return messages


def wait_for_response():
    """
    # Wait for response time
    # Configurable in vars.py

    :return: None
    """
    time.sleep(v.response_time)


def log_message(ai_number, message):
    """
    # Log a message to a text file, 'chat_log.txt'. Configure the name of this file in vars.py.

    :param ai_number: The ai # used to identify who is sending the message
    :param message: The message to log
    :return: None
    """
    print(str(d.datetime.now()) + "\nAI #" + str(ai_number) + ": \n " + str(message) + "\n")
    logger.write(v.full_log_file, "\nAI #" + str(ai_number) + ": \n " + str(message) + "\n")


def converse(first, second):
    """
    The conversation loop.\n
    # Collects messages from first ai, logs and sends those messages to second ai.\n
    # Waits for a response from second ai\n
    # Send response from second ai to first ai\n
    # Waits for a response from first ai\n
    # Loop\n

    :param first: The first ai
    :param second: The second ai
    :return: None
    """
    try:
        while True:
            # get first AI messages # login process should leave us waiting on ai 1 window for entry point consideration
            ai_1_messages = collect_messages(first)

            min_max_windows(first, second)  # swap to second window

            # send message from first ai to second ai
            ai_1_messages_sent = type_messages(second, get_last_messages(second, ai_1_messages))
            for msg in ai_1_messages_sent:  # log all message sent
                log_message("1", msg)

            wait_for_response()  # on second ai window

            # get second ai response messages
            ai_2_messages = collect_messages(second)

            min_max_windows(second, first)  # swap to first window

            # send message response from second ai to first ai
            ai_2_messages_sent = type_messages(first, get_last_messages(first, ai_2_messages))
            for msg in ai_2_messages_sent:  # log all message sent
                log_message("2", msg)

            wait_for_response()  # wait for a response on first window to continue loop
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    # required for text input to properly activate send message button
    keyboard = Controller()

    # to test without sending messages, set debug on
    print("Debug? (Y/N) \nIf yes, program will not send messages and instead only generate logs")
    debug_str = str(input())
    isDebug = 0

    if debug_str == 'Y' or debug_str == 'y':
        isDebug = 1

    # Do the Things
    logger.write(v.full_log_file, "\n\n <<<----------New chat started---------->>>\n Debug mode:" + str(isDebug))

    # sets browsers service path to driver file
    s = Service(v.chrome_driver_path)

    # create and init login # 2 first - then minimize window
    ai_2 = webdriver.Chrome(service=s)
    ai_2.get(v.starting_url)  # navigate to login page
    login(ai_2, v.ai_2_email_value, v.ai_2_password_value)  # login #2
    ai_2.minimize_window()  # minimize #2

    # create and init login # 1 second - then maximize window
    ai_1 = webdriver.Chrome(service=s)
    ai_1.get(v.starting_url)  # navigate to login page
    ai_1.maximize_window()  # maximize #1
    login(ai_1, v.ai_1_email_value, v.ai_1_password_value)  # login #1

    # wait for additional buffer before chatting
    time.sleep(1)

    # start chatting
    try:
        converse(ai_1, ai_2)
    except Exception as e:
        print("Encountered fatal error: " + str(e))
