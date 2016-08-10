"""
Script to repost youtube videos on vk.com. DRAFT. Do not take it seriously.

NOTES:
Does not look further than 50 most recently uploaded videos (1 request limit).
No DB. Stores last reposted video id in file `last_id`.
No proper error handling/logging. 
Does not guarantee repost to be atomic operation. 
Youtube API costs: 6 units / run (2 requests).
"""
from config import YT_API_KEY, YT_CHANNEL_ID, VK_API_KEY, VK_OWNER_ID, FILE_LAST_ID

import logging
import requests
from itertools import takewhile
from pprint import pprint as pp


yt_api_baseurl = 'https://www.googleapis.com/youtube/v3/'
vk_api_baseurl = 'https://api.vk.com/method/'
logger = logging.getLogger('yt2vk')


class RequestError(Exception):
    pass


def _yt_api_request(resource, params=None):
    if params is None:
        params = {}
    params['key'] = YT_API_KEY
    url = yt_api_baseurl + resource
    response = requests.get(url, params).json()
    if 'error' in response:
        raise RequestError(url, response)
    return response

def yt_new_videos(last_id=None):
    """
    Returns list of videos which should be reposted.
    `last_id` is video id of last reposted video.
    """
    response = _yt_api_request('channels', params={
            'part': 'contentDetails',
            'id': YT_CHANNEL_ID,
        })
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    response = _yt_api_request('playlistItems', params={
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 50,
        })
    videos = list(takewhile(
        lambda item: item['snippet']['resourceId']['videoId'] != last_id,
        response['items']))
    videos.reverse()
    return videos

def _vk_api_request(method_name, params=None):
    if params is None:
        params = {}
    params['access_token'] = VK_API_KEY
    params['v'] = '5.53'
    url = vk_api_baseurl + method_name
    response = requests.post(url, data=params)
    json_data = response.json()
    if 'error' in json_data:
        raise RequestError(url, json_data)
    return json_data['response']

def _vk_follow_upload_url(upload_url, yt_video_id):
    # Do not upload again if video is already uploaded. 
    response = _vk_api_request('video.get', params={
            'owner_id': VK_OWNER_ID,
            'count': 200,
        })
    for item in response['items']:
        if yt_video_id in item['player']:
            logging.warn('Video "%s" was already uploaded. New video upload is cancelled.', yt_video_id)
            return item['id']

    response = requests.get(upload_url).json()
    if 'error_code' in response:
        raise RequestError(upload_url, response)

def vk_post(yt_video):
    snippet = yt_video['snippet']
    title = snippet['title']
    yt_video_id = snippet['resourceId']['videoId']
    yt_video_url = 'https://youtube.com/watch?v=' + yt_video_id
    description = snippet['description']
    #message = title + '\n' + description + '\n' + yt_video_url
    message = title.upper() + '\n\n' + description
    message += '\n\n(дополнительный комментарий - в видео)'

    response = _vk_api_request('video.save', params={
            'link': yt_video_url,
            #'wallpost': 1,
            'group_id': VK_OWNER_ID.lstrip('-'),
        })
    old_vid = _vk_follow_upload_url(response['upload_url'], yt_video_id)
    if old_vid is not None:
        # Video has been uploaded already. Use it.
        vk_video_id = old_vid  
    else:
        vk_video_id = response['video_id']
    
    attachments = 'video{}_{}'.format(response['owner_id'], vk_video_id)
    response = _vk_api_request('wall.post', params={
            'owner_id': VK_OWNER_ID,
            'from_group': 1,
            'guid': yt_video_id,
            'message': message,
            'attachments': attachments,
        })

def _set_last_id(last_id):
    with open(FILE_LAST_ID, 'w') as f:
        f.write(last_id)

def _get_last_id():
    with open(FILE_LAST_ID, 'a+') as f:
        f.seek(0)
        last_id = f.read().rstrip()
    return last_id or None
        
def main():
    last_id = _get_last_id()
    for yt_video in yt_new_videos(last_id):
        yt_video_id = yt_video['snippet']['resourceId']['videoId']
        logger.info("Processing: last_id = %s, vid = %s, title = %s",
                last_id, yt_video_id, yt_video['snippet']['title'])

        vk_post(yt_video)
        
        _set_last_id(yt_video_id)

if __name__ == '__main__':
    try:
        main()
    except RequestError as e:
        logger.error(repr(e))
        raise
    
