#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import ( Flask, render_template, request, Response,  flash,  redirect, url_for
 
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, String, func, distinct, ARRAY, Table
from sqlalchemy.dialects import postgresql
import logging
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from flask_debugtoolbar import DebugToolbarExtension

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from Models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #shows the venues page with the venues grouped by city and state

  data = Venue.query.with_entities(Venue.city, Venue.state,
  postgresql.array_agg(
    func.json_build_object('id',Venue.id,'name',Venue.name)).label('venues'))\
  .group_by(Venue.city,Venue.state).all()

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #searches the venues

  search_term = request.form.get('search_term', '')
  response = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))\
  .with_entities(func.count(Venue.id).label('count'), postgresql.array_agg(
    func.json_build_object('id',Venue.id,'name',Venue.name,)).label('data')).all()

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  data = Venue.query.filter(venue_id==Venue.id and Venue.name is not None)\
    .outerjoin(Show, Venue.id == Show.venue_id)\
    .outerjoin(Artist, Artist.id == Show.artist_id)\
    .add_columns(Venue.id,Venue.name,Venue.city,
      Venue.state,Venue.address,Venue.phone,
      Venue.image_link,Venue.facebook_link,Venue.genres,
      Venue.seeking_description,Venue.seeking_talent,Venue.website,
      postgresql.array_agg(
        func.json_build_object(
          'artist_id',Artist.id,
          'artist_name',Artist.name,
          'artist_image_link',Artist.image_link,
          'start_time',Show.start_time
        )).filter(Show.start_time < datetime.today()).label('past_shows'), 
      postgresql.array_agg(
        func.json_build_object(
          'artist_id',Artist.id,
          'artist_name',Artist.name,
          'artist_image_link',Artist.image_link,
          'start_time',Show.start_time
        )).filter(Show.start_time > datetime.today()).label('upcoming_shows'),
      func.count(Artist.id).filter(Show.start_time < datetime.today()).label('past_shows_count'),
      func.count(Artist.id).filter(Show.start_time > datetime.today()).label('upcoming_shows_count'))\
    .group_by(Venue.id).all()

  if not data:
    return render_template('errors/404.html')

  return render_template('pages/show_venue.html', venues=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #called upon submitting the new venue listing form
  error = False

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, website=website, 
    facebook_link=facebook_link, image_link=image_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except():
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return redirect(url_for('/venues'))
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = Artist.query.filter(Artist.name is not None)\
    .with_entities(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  #searches the artists

  search_term = request.form.get('search_term', '')
  response = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))\
  .with_entities(func.count(Artist.id).label('count'), postgresql.array_agg(
    func.json_build_object('id',Artist.id,'name',Artist.name,)).label('data')).all()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id

  data = Artist.query.filter(artist_id==Artist.id)\
    .outerjoin(Show, Artist.id == Show.artist_id)\
    .outerjoin(Venue, Venue.id == Show.venue_id)\
    .add_columns(Artist.id,Artist.name,Artist.city,
      Artist.state,Artist.phone,Artist.image_link,
      Artist.facebook_link,Artist.genres,Artist.seeking_description,
      Artist.seeking_venue,Artist.website,
      postgresql.array_agg(
        func.json_build_object(
          'venue_id', Venue.id,
          'venue_name',Venue.name,
          'venue_image_link',Venue.image_link,
          'start_time',Show.start_time
        )).filter(Show.start_time < datetime.today()).label('past_shows'), 
      postgresql.array_agg(
        func.json_build_object(
          'venue_id', Venue.id,
          'venue_name',Venue.name,
          'venue_image_link',Venue.image_link,
          'start_time',Show.start_time
        )).filter(Show.start_time > datetime.today()).label('upcoming_shows'),
      func.count(Venue.id).filter(Show.start_time < datetime.today()).label('past_shows_count'),
      func.count(Venue.id).filter(Show.start_time > datetime.today()).label('upcoming_shows_count'))\
    .group_by(Artist.id).all()

  return render_template('pages/show_artist.html', artists=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, website=website, 
    facebook_link=facebook_link, image_link=image_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Artist ' + request.form['name'] + ' was unsuccessfully added!')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully added!')

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = Show.query\
    .join(Venue, Venue.id == Show.venue_id)\
    .join(Artist, Artist.id == Show.artist_id)\
    .with_entities(Show.venue_id, Venue.name.label('venue_name'), 
      Show.artist_id, (Artist.name).label('artist_name'), Artist.image_link.label('artist_image_link'), 
      func.to_char(Show.start_time, 'Day DD-MON-YYYY HH12:MIPM').label('start_time')).order_by(Show.start_time).all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False

  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Show was unsuccessfully listed!')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist=Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  error = False
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Artist ' + request.form['name'] + ' was unsuccessfully updated!')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue=Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.genres = request.form.getlist('genres')
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Venue ' + request.form['name'] + ' was unsuccessfully updated!')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

