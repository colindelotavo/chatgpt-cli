import pytest
import os
import json
from src.chatgpt_api_client import ChatGPTAPI
from src.chatgpt_api_client import MESSAGES_SAVE_FILENAME
from dotenv import load_dotenv

load_dotenv()

API_KEY = api_key=os.getenv("OPENAI_API_KEY")
MESSAGES_TEMPLATE = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    ]

@pytest.fixture
def chat_api():
    return ChatGPTAPI(api_key=API_KEY)

def test_add_message(chat_api):
    chat_api.messages = []
    chat_api.add_message("system", "You are a helpful assistant.")
    chat_api.add_message("user", "Who won the world series in 2020?")
    chat_api.add_message("assistant", "The Los Angeles Dodgers won the World Series in 2020.")
    assert chat_api.messages == MESSAGES_TEMPLATE

def test_create_chat_completion(chat_api, tmpdir):
    chat_api.messages_save_filename = tmpdir.join('test_messages.save.txt')
    chat_api.messages = []
    expected_response = chat_api.create_chat_completion("Who won the world series in 2020?")
    assert expected_response["choices"][0]["message"]["role"] == "assistant"
    assert "content" in expected_response["choices"][0]["message"]
    assert chat_api.messages == MESSAGES_TEMPLATE

def test_get_last_messages(chat_api):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    assert chat_api.get_last_messages(2) == [
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    ]

def test_get_last_message_content(chat_api):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    assert chat_api.get_last_message_content(2) == [
        "Who won the world series in 2020?",
        "The Los Angeles Dodgers won the World Series in 2020."
    ]

def test_keep_most_recent_messages(chat_api):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    chat_api.keep_most_recent_messages(1)
    assert chat_api.messages == [
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."}
    ]

def test_load_messages(chat_api, tmpdir):
    chat_api.messages_save_filename = tmpdir.join('test_messages.save.txt')
    chat_api.messages = []
    chat_api.load_messages()
    assert chat_api.messages == [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    chat_api.messages = []
    chat_api.load_messages()
    chat_api.messages_save_filename.write(json.dumps([{"role": "system", "content": "You are a helpful assistant."}]))
    with open(chat_api.messages_save_filename, 'r') as f:
        f_contents = json.load(f)
    assert f_contents == chat_api.messages

def test_print_messages_as_json(chat_api, capfd):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    chat_api.print_messages_as_json(chat_api.messages)
    out, _ = capfd.readouterr()
    assert json.loads(out) == MESSAGES_TEMPLATE

def test_print_most_recent_content(chat_api, capfd):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    chat_api.print_most_recent_content()
    out, _ = capfd.readouterr()
    assert out == "Who won the world series in 2020?\nThe Los Angeles Dodgers won the World Series in 2020.\n"

def test_print_most_recent_messages(chat_api, capfd):
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    chat_api.print_most_recent_messages()
    out, _ = capfd.readouterr()
    assert json.loads(out) == [
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    ]
    
def test_save_messages(chat_api, tmpdir):
    chat_api.messages_save_filename = tmpdir.join('test_messages.save.txt')
    chat_api.messages = []
    chat_api.messages = MESSAGES_TEMPLATE
    chat_api.save_messages()
    with open(chat_api.messages_save_filename, 'r') as f:
        f_contents = json.load(f)
    assert f_contents == chat_api.messages