from openai import OpenAI
import logging
import sys
import os
import asyncio
import datetime

class AI:
    async def query(self, prompt):
        retries = 4
        wait_time = 3
        failure_details = []
        if os.path.exists("environ/shuttleai"):
            with open("environ/shuttleai", 'r') as f:
                APIKEY = f.read().strip()
        else:
            logging.critical("environ/shuttleai not found. Make sure the file exists.")
            sys.exit(1)
        NEWLINE = "\n"
        try:
         cli = OpenAI(api_key=APIKEY,base_url='https://api.shuttleai.app/v1')
         response = cli.chat.completions.create(
                    model='gpt-3.5-turbo-1106',
                    messages=[
                        {"role": "system",
                         "content": "You are a helpful GPT-3 based chatbot, you currently live in a discord bot called 'Atheno'. Atheno is a custom discord bot written in Python, by rare1k.space. Keep in mind that your memory only lasts for one message due to Discord limitations. You have basic access to the current user and guild that you were invoked in, and the info is at the bottom of every message. To mention a user, find the Proper Mention area and use that to mention the user, as that properly pings them on Discord. The current time and date is provided to you in the Unix Epoch. The server that you were invoked in is in the Current Server Info section at the bottom of the message. This section gives the server name and ID."},
                        {"role": "user", "content": prompt}
                    ]
                )
         logging.debug(response.choices[0].message.content)
         return response.choices[0].message.content
        except Exception as e:
            return f"```[ATHENO EXCEPTION]: A Python exception has occurred while trying to run AI.query(...)\nException Details: {e=}"
        
