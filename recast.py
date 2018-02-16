from genres import Playlist


def list_element(i, playlist):
    return {
        'title': playlist.name,
        'imageUrl': playlist.image_url,
        'subtitle': playlist.id,
        'buttons': [
          {
            'title': str(i),
            'type': 'BUTTON_TYPE',
            'value': f'Select choice {i}'
          }
        ]
    }


def list_for(sp, genres):
    playlists = [Playlist.from_genre(sp, genre) for genre in genres.values()]
    if not all((pl.found for pl in playlists)):
        return {}
    else:
        return {
          'type': 'list',
          'content': {
            'elements': [list_element(i, pl) for i, pl in enumerate(playlists)],
          }
        }


def buttons_for(genres, title=''):
    title = title or 'Select a genre!'
    return {
      'type': 'quickReplies',
      'content': {
        'title': title,
        'buttons': [
          {
            'title': f'({k}): {v.title()}',
            'value': f'Select genre {k}.'
          } for k, v in genres.items()
        ]
      }
    }


def spotify_login(url):
    return [{
        'type': 'text',
        'content': url,
    }]
