from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes  = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_song(token, track_name, verbose):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    if verbose:
        json_result = json.loads(result.content)
    else:
        return_list = []
        json_result = json.loads(result.content)['tracks']['items']
        for x in json_result:
            tempList = [x["name"],x["artists"][0]["name"],x["id"]]
            return_list.append(tempList)
            #return_list.append(x["name"] + " - " + x["artists"][0]["name"] + " (" + x["id"] + ")")
        #return json_result["name"] + " - " +json_result["artists"][0]["name"]
        return return_list
    if len(json_result) == 0:
        return "song not found"
    return json_result

def get_audio_features(token, track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    unfiltered_json_result = json.loads(result.content)

    json_result = [unfiltered_json_result["acousticness"], unfiltered_json_result["danceability"], unfiltered_json_result["energy"], unfiltered_json_result["instrumentalness"], unfiltered_json_result["liveness"], unfiltered_json_result["speechiness"], unfiltered_json_result["valence"]]
    return json_result

def get_reccommendations(token, track_id, audio_features, importance_weights, track_limit):
    stat = ["acousticness","danceability","energy","instrumentalness","liveness","speechiness","valence"]
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    url+= f"?limit={track_limit}&seed_tracks={track_id}"
    for i in range(len(stat)):
        url += f"&min_{stat[i]}={audio_features[i] - (audio_features[i]*importance_weights[i])}&max_{stat[i]}={audio_features[i] + ((1 - audio_features[i])*importance_weights[0])}&target_{stat[i]}={audio_features[i]}"
    #query += f"&min_danceability={audio_features[1] - (audio_features[1]*importance_weights[1])}&max_danceability={audio_features[0] + ((1 - audio_features[0])*importance_weights[0])}&target_acousticness={audio_features[1]}"
    
    print(url)
    result = get(url, headers=headers)
    unfiltered_json_result = json.loads(result.content)
    json_result = unfiltered_json_result['tracks']
    return_list = []
    for x in json_result:
            tempList = [x["name"],x["artists"][0]["name"],x["id"]]
            return_list.append(tempList)
    return return_list
    

token = get_token()
#print(token)
song = search_for_song(token, "dance dance", False)
print(song)
print(get_audio_features(token, song[0][2]))
weights = [.5,1,.11,1,.25,1,0]
print(get_reccommendations(token, song[0][2], get_audio_features(token, song[0][2]), weights,6))