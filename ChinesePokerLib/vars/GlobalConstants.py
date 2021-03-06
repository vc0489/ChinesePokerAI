import os
import os.path as op
from pathlib import Path

_BASEDIR = Path(__file__).parent.absolute() / '..' / '..' 
_BASEDIR = _BASEDIR.resolve()

DATADIR = _BASEDIR / 'Data'
MODELDIR = _BASEDIR / 'Models'

DEALT_HANDS_DUMP_DIR = Path(DATADIR) / 'DealtHandsDump'
SPLITS_FROM_DEALT_HANDS_DIR = Path(DATADIR) / 'SplitsFromDealtHands'

DEFAULT_SPLITS_JSON_FILE = SPLITS_FROM_DEALT_HANDS_DIR / 'splits_json_data_0_to_999.txt'
# VC TODO: create dirs if don't exist

DEFAULT_SLACK_VARS = {
  'channel':'#chinese-poker',
  'token':os.environ.get('SLACK_TOKEN'),
  'username':'Chokerot',
  'icon':'https://img.icons8.com/color/96/000000/cards.png'
}

SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'