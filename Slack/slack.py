#%%
import requests
from pathlib import Path
import json
import os
import sys

#%%

slack_token = os.environ['SLACK_TOKEN']
slack_channel = '#chinese-poker'
slack_icon = 'https://img.icons8.com/color/96/000000/cards.png'
slack_user_name = 'Chokerot'

def post_message_to_slack(text, blocks = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'icon_url': slack_icon,
        'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()



if __name__ == "__main__":
  msg = 'Testing. 1,2,3.'
  post_message_to_slack(msg)
  sys.exit()


# %%
