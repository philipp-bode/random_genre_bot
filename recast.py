
def list_element():

    {
        'title': 'ELEM_1_TITLE',
        'imageUrl': 'IMAGE_URL',
        'subtitle': 'ELEM_1_SUBTITLE',
        'buttons': [
          {
            'title': 'BUTTON_1_TITLE',
            'type': 'BUTTON_TYPE',
            'value': 'BUTTON_1_VALUE'
          }
        ]
    }


def list_for():
    return {
      'type': 'list',
      'content': {
        'elements': [],
        'buttons': [
          {
            'title': 'BUTTON_1_TITLE',
            'type': 'BUTTON_TYPE',
            'value': 'BUTTON_1_VALUE'
          }
        ]
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
            'title': v.title(),
            'value': k
          } for k, v in genres.items()
        ]
      }
    }
