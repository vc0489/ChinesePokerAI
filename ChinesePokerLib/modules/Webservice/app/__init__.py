from ChinesePokerLib.classes.Strategy import ChinesePokerModelSetToGameScoreStrategy
import ChinesePokerLib.vars.GlobalConstants as GConst


from flask import Flask

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
print('loading COM start')
#app.com_strat = ChinesePokerModelSetToGameScoreStrategy.load_strategy_from_file(
#  GConst.MODELDIR / 'FullGameScoreModelGradBoostHyperoptR1.pickle')

app.com_strat = ChinesePokerModelSetToGameScoreStrategy.load_strategy_from_file(
  GConst.MODELDIR / 'FullGameScoreModelRandomForestV1.pickle')

print('loaded COM start')
from app import routes
