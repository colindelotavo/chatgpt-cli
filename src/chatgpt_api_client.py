#!/usr/bin/env python3

import os
import json
from dotenv import load_dotenv
import click
import openai

load_dotenv()

INSPECT_REQUEST_HELP_MESSAGE = 'Shows the user what messages are being sent to the API. By default, it only \
                                sends the last response sent by the API (for context) plus the current prompt.'
HELP_MESSAGE_TEMPLATE = 'Example usage: {filename} "Who won the world series in 2020?"'
MESSAGES_SAVE_FILENAME = "messages.save.txt"


class ChatGPTAPI:
    def __init__(self, api_key=os.getenv("OPENAI_API_KEY")):
        openai.api_key = api_key
        self.messages = []
        self.messages_save_filename = MESSAGES_SAVE_FILENAME

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def create_chat_completion(self, prompt, max_tokens=50, inspect_request=False):
        self.load_messages()
        self.add_message("user", prompt)
        last_two_messages = self.get_last_messages(2)
        if inspect_request:
            self.print_messages_as_json(last_two_messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=last_two_messages
        )
        assistant_response = response["choices"][0]["message"]["content"]
        print(response)
        self.add_message("assistant", assistant_response)
        self.keep_most_recent_messages()
        self.save_messages()
        print(f"Q: {prompt}")
        print(f"A: {assistant_response}\n")
        return response

    def get_last_messages(self, n):
        return self.messages[-n:]

    def get_last_message_content(self, n):
        return [message['content'] for message in self.get_last_messages(n)]

    def keep_most_recent_messages(self, n=10):
        self.messages = self.messages[-n:]

    def load_messages(self):
        if not os.path.exists(self.messages_save_filename):
            self.add_message("system", "You are a helpful assistant.")
            return
        with open(self.messages_save_filename, 'r') as f:
            try:
                self.messages = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                self.add_message("system", "You are a helpful assistant.")

    def print_messages_as_json(self, data=None):
        print(json.dumps(self.messages if data is None else data, indent=4, sort_keys=False))

    def print_most_recent_content(self, n=2):
        print('\n'.join(self.get_last_message_content(n)))

    def print_most_recent_messages(self, n=2):
        if not self.messages:
            print("Brand new chat. No previous messages.")
            return
        self.print_messages_as_json(self.get_last_messages(n))

    def save_messages(self):
        with open(self.messages_save_filename, 'w') as f:
            f.write(json.dumps(self.messages, indent=4))

    def test_authenticate_gpt(self):
        try:
            openai.Completion.create(model="text-davinci-003", prompt="Hello", max_tokens=5)
            print("Authentication successful!")
        except Exception as e:
            print("Authentication failed:", str(e))


@click.command(help=HELP_MESSAGE_TEMPLATE.format(filename=__file__))
@click.argument('prompt')
@click.option("-f","--filename", default=MESSAGES_SAVE_FILENAME, show_default=True)
@click.option("--inspect-request/--no-inspect-request", default=False, show_default=True, help=INSPECT_REQUEST_HELP_MESSAGE)
@click.option("--max-tokens", type=int, default=50, show_default=True)
def main(prompt, filename, inspect_request, max_tokens):
    chat_api = ChatGPTAPI()

    chat_api.messages_save_filename = filename

    chat_api.create_chat_completion(prompt, inspect_request=inspect_request)


if __name__ == "__main__":
    main()
