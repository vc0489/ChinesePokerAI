#%%
import requests
from pathlib import Path
import json

#%%

slack_token = 'xoxb-530987712531-1229869759123-sRfLUlGs2jb63x3rhCaHTgr2'
slack_channel = '#chinese-poker'

#slack_icon = Path(__file__).parent / 'playing_cards_icon.png'
slack_icon = 'https://img.icons8.com/color/96/000000/cards.png'
slack_user_name = 'Chokerot'

print(slack_icon)

def post_message_to_slack(text, blocks = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'icon_url': slack_icon,
        'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()



msg = 'Testing. 1,2,3.'

post_message_to_slack(msg)


# %%
