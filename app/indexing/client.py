from algoliasearch.search_client import SearchClient
from app.config import settings
from app.db.models import Video, Playlist
from app.db.schemas_indexing import *


def get_index(name=settings.ALGOLIA_INDEX_NAME):

    client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_API_KEY)
    index = client.init_index(name)
    return index

async def get_dataset():

    video_dic = [x.as_dict() for x in await Video.get_list_videos()]
    video_dataset = [VideoIndex(**x).dict() for x in video_dic]

    playlist_dic = [x.as_dict() for x in await Playlist.get_list_playlists()]
    playlist_dataset = [PlaylistIndex(**x).dict() for x in playlist_dic]

    dataset = video_dataset + playlist_dataset
    return dataset

async def update_index():

    index = get_index()
    dataset = await get_dataset()
    result = index.search("")  # obtener el total de data, records
    count =  abs(result.get("nbHits") - len(dataset)) 

    if count != 0:
                #len(list(idx_response)[0]['objectIDs'])
        try:
            idx_response = index.replace_all_objects(dataset).wait()
        except:
            count = 0
    return count

def search_index(query):

    index = get_index()

    return index.search(query)





