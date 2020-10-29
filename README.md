## Introduction 

ChinesePokerAI is a project which combines machine learning and the card game of Chinese poker. There are many sites with information about Chinese poker itself. [Wikipedia](https://en.wikipedia.org/wiki/Chinese_poker) is a good place to start.

This repository is formed of three main components: 
1. Python game engine which can simulate rounds of Chinese poker.
1. Python modelling framework for fitting machine learning models.
1. Flask webservice for the web application.

The web application is currently deployed on AWS and can be accessed [here](http://app.chinesepokertips.com/)



---

## Requirements

Python version 3.69 or higher

---

## Usage

It is strongly recommended that you create a virtual environment first. For example:

```
python3 -m venv path/to/venv
```

then activate the virtual environment and install the required packages in requirements.txt:

```
# On Unix/Linux/OS X001
source path/to/venv/bin/activate
pip install -r requirements.txt 
```


ChinesePokerAI is a library under development so to install clone the repository and simply run:

```
pip install -e . 
```

To import the library in Python run

```
import ChinesePokerLib
```


---

Example code snippets will be added soon.
I am currently working on a REST API that will allow interested developers to more easily simulate 
rounds of chinese poker.

---

