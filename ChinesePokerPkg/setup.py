from distutils.core import setup

#with open("README.md", "r") as fh:
#  long_description = fh.read()

setup(
  name="ChinesePokerLib",
  version="0.0.1",
  author="Vincent Chen",
  author_email="vc0489@gmail.com",
  description="Library for simulating Chinese Poker",
  packages=[
    "ChinesePokerLib",
    "ChinesePokerLib.classes",
    "ChinesePokerLib.vars",
    "ChinesePokerLib.modules",
    "ChinesePokerLib.modules",
    "ChinesePokerLib.modules.Webservice",
    "ChinesePokerLib.modules.Webservice.app",
  ],
  package_data={"": ["VERSION"]},
  include_package_data=True,
)
