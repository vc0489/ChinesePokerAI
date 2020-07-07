import os.path as op
from pathlib import Path

DATADIR = Path(__file__).parent.absolute() / '..' / '..'/ '..' / 'Data'
DATADIR = DATADIR.resolve()

DEALT_HANDS_DUMP_DIR = Path(DATADIR) / 'DealtHandsDump'
SPLITS_FROM_DEALT_HANDS_DIR = Path(DATADIR) / 'SplitsFromDealtHands'

DEFAULT_SPLITS_JSON_FILE = SPLITS_FROM_DEALT_HANDS_DIR / 'splits_json_data_0_to_999.txt'
# VC TODO: create dirs if don't exist