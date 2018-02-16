from genres import Playlist


def list_element(i, playlist):
    return {
        'title': getattr(playlist, 'genre'),
        'imageUrl': playlist.image_url,
        'subtitle': playlist.name,
        'buttons': [
          {
            'title': str(i + 1),
            'type': 'BUTTON_TYPE',
            'value': f'Select choice {i + 1}'
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
            'elements': [list_element(i, pl) for i, pl in enumerate(playlists)]
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
    return {
        'type': 'buttons',
        'content': {
            'title': 'BUTTON_TITLE',
            'buttons': [{
                'title': 'BUTTON_TITLE',
                'type': 'BUTTON_TYPE',
                'value': 'BUTTON_VALUE'
            }]
        }
    }
    return [{
        'type': 'text',
        'content': url,
    }]
