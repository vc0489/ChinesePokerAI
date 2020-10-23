## Introduction 

ChinesePokerAI is a project which combines machine learning and the card game of Chinese poker. There are many sites with information about Chinese poker itself. [Wikipedia](https://en.wikipedia.org/wiki/Chinese_poker) is a good place to start.

This repository is formed of three main components: 
1. Python game engine which can simulate rounds of Chinese poker.
1. Python modelling framework for fitting machine learning models.
1. Flask webservice for the web application.

The web application is currently deployed on AWS and can be accessed [here](http://app.chinesepokertips.com/)

---

## Usage

It is strongly recommended that you create a virtual environment first.
ChinesePokerAI is a library under development so to install clone the repository and simply run

```
pip install -e . 
```

in the top level folder. Then, install the dependent libraries by running

```
pip install -r requirements.txt
```

To import the library in Python run

```
import ChinesePokerLib
```

---

I am currently working on a REST API that will allow interested developers to simulate 
chinese poker.

---

