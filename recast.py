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


def list_for(playlists):

    return {
      'type': 'list',
      'content': {
        'elements': [list_element(i, pl) for i, pl in enumerate(playlists)]
      }
    }


def buttons_for(playlists):
    replies = [{
        'type': 'text',
        'content': pl.name,
    } for pl in playlists]
    replies.append({
      'type': 'quickReplies',
      'content': {
        'title': 'What would you like to listen to?',
        'buttons': [
          {
            'title': f'Select {i + 1}.',
            'value': f'Select {i + 1}.'
          } for i, _ in enumerate(playlists)
        ]
      }
    })
    return replies


def spotify_login(url):
    return [{
        'type': 'text',
        'content': url,
    }]
    # return {
    #     'type': 'buttons',
    #     'content': {
    #         'buttons': [{
    #             'title': 'Login to Spotify',
    #             'type': 'web_url',
    #             'value': url
    #         }]
    #     }
    # }
