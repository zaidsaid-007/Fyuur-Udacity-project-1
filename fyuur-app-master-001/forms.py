from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

def validate_phone(form, field):
    if not re.search(r'^(?:\+?44)?[07]\d{9,13}$', field.data):
        raise ValidationError("Invalid phone number")

state_choice =[
    ('AL', 'AL'),('AK', 'AK'),('AZ', 'AZ'),('AR', 'AR'),
    ('CA', 'CA'),('CO', 'CO'),('CT', 'CT'),
    ('DE', 'DE'),('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),('IL', 'IL'),('IN', 'IN'),('IA', 'IA'),
    ('KS', 'KS'),('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),('MT', 'MT'),('MD', 'MD'),('MA', 'MA'),('MI', 'MI'),('MN', 'MN'),('MS', 'MS'),('MO', 'MO'),
    ('NE', 'NE'),('NV', 'NV'),('NH', 'NH'),('NJ', 'NJ'),('NM', 'NM'),('NY', 'NY'),('NC', 'NC'),('ND', 'ND'),
    ('OH', 'OH'),('OK', 'OK'),('OR', 'OR'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),('SD', 'SD'),
    ('TN', 'TN'),('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),('VA', 'VA'),
    ('WA', 'WA'),('WV', 'WV'),('WI', 'WI'),('WY', 'WY'),
]
genre_choice = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),('Punk', 'Punk'),
    ('R&B', 'R&B'),('Reggae', 'Reggae'),('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

class VenueForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()],choices=state_choice)
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired(),validate_phone])
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()],choices=genre_choice)
    website = StringField('website', validators=[URL()])
    facebook_link = StringField('facebook_link', validators=[URL()])
    seeking_talent = BooleanField('seeking_talent')
    seeking_description = StringField('seeking_description')
class ArtistForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()],choices=state_choice)
    phone = StringField('phone',validators=[DataRequired(),validate_phone])
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()],choices=genre_choice,default=('Hip-Hop'))
    website = StringField('website', validators=[URL()])
    facebook_link = StringField('facebook_link', validators=[URL()])
    seeking_venue = BooleanField('seeking_venue')
    seeking_description = StringField('seeking_description')
class ShowForm(Form):
    artist_id = StringField('artist_id',validators=[DataRequired()])
    venue_id = StringField('venue_id', validators=[DataRequired()])
    start_time = DateTimeField('start_time',validators=[DataRequired()],default= datetime.today())
