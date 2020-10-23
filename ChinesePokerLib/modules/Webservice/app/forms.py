from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, IntegerField, FormField, BooleanField
#PasswordField, BooleanField, 
from wtforms.validators import DataRequired, ValidationError
from wtforms import widgets


from app.utils import submitted_cards_validator




class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CheckboxTableField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


"""
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
"""

"""
class CardNumberForm(Form):
  def __init__(self, label):
    self.label = label

  card_number_choices = [
    ('A','A'),
    ('K','K'),
    ('Q','Q'),
    ('10','10'),
    ('9','9'),
    ('8','8'),
    ('7','7'),
    ('6','6'),
    ('5','5'),
    ('4','4'),
    ('3','3'),
    ('2','2'),
  ]

  cards = SelectMultipleField(
    self.label,
    choices = card_number_choices
  )
""" 

class SuggestForm(FlaskForm):
  #cards = StringField('Cards', validators=[DataRequired()])
  card_number_choices = [
    ('A','A'),
    ('K','K'),
    ('Q','Q'),
    ('J','J'),
    ('10','10'),
    ('9','9'),
    ('8','8'),
    ('7','7'),
    ('6','6'),
    ('5','5'),
    ('4','4'),
    ('3','3'),
    ('2','2'),
  ]
  #cards = StringField('Cards', validators=[DataRequired(), submitted_cards_validator])
  card_errors = []

  choose_random = BooleanField('Random cards')
  spades = SelectMultipleField(
    'Spades', 
    choices = card_number_choices,
  )
  hearts = SelectMultipleField(
    'Hearts', 
    choices = card_number_choices,
  )
  diamonds = SelectMultipleField(
    'Diamonds', 
    choices = card_number_choices,
  )
  clubs = SelectMultipleField(
    'Clubs', 
    choices = card_number_choices,
  )
  
  #cards = FormField
  select_random = BooleanField('Random cards')
  n_suggestions = IntegerField('No. of Suggestions', validators=[DataRequired()])
  unique_code_levels = SelectField(
    'Variability', 
    choices=[('0', 'None'), ('3', 'Low'), ('2', 'Medium'), ('1', 'High')],
    #choices=['4','3','2','1'],
  )
  #choices=[(0, 'None'), (3, 'Low'), (2, 'Medium'), (1, 'High')],
  #unique_top_level_codes = SelectField(u'Variability', choices=[(None, 'None'), (3, 'Low'), (2, 'Medium'), (1, 'High')])
  #cards = StringField('Cards', validators=[DataRequired(), submitted_cards_validator])
  submit = SubmitField('Submit')


  def validate(self):
    
    if not self.select_random.data:
      cards_selected = len(self.spades.data) + len(self.hearts.data) + len(self.diamonds.data) + len(self.clubs.data)
      if cards_selected < 13:
        #raise ValidationError(f'Too few ({cards_selected}) cards selected. Please select 13 cards.')
        self.card_errors.append(f'Too few ({cards_selected}) cards selected. Please select 13 cards.')
              
        return False
      elif cards_selected > 13:
        #raise ValidationError(f'Too many ({cards_selected}) cards selected. Please select 13 cards.')
        self.card_errors.append(f'Too many ({cards_selected}) cards selected. Please select 13 cards.')
        return False
    return True
