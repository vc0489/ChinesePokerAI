from ChinesePokerLib.classes.StrategyClass import ChinesePokerModelSetToGameScoreStrategyClass
import ChinesePokerLib.vars.GlobalConstants as GConst


from flask import Flask

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
print('loading COM start')
app.com_strat = ChinesePokerModelSetToGameScoreStrategyClass.load_strategy_from_file(
  GConst.MODELDIR / 'FullGameScoreModelGradBoostHyperoptR1.pickle')

print('loaded COM start')
from app import routes
