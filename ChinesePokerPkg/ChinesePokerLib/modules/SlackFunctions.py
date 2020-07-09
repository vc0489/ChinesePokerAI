#%%
import requests
from pathlib import Path
import json
import os
import sys

#%%

#slack_token = os.environ['SLACK_TOKEN']
#slack_channel = '#chinese-poker'
slack_icon = 'https://img.icons8.com/color/96/000000/cards.png'
slack_user_name = 'Chokerot'

def post_message_to_slack_channel(text, channel, token=None, icon=None, username=None, blocks=None):
  
  if slack_token is None:
    slack_token = os.environ['SLACK_TOKEN']
  return requests.post('https://slack.com/api/chat.postMessage', {
    'token': token,
    'channel': channel,
    'text': text,
    'icon_url': icon,
    'username': username,
    'blocks': json.dumps(blocks) if blocks else None
  }).json()




# %%
