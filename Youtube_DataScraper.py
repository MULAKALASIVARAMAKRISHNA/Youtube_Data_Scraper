from googleapiclient.discovery import build
import csv

# Your API Key Here
API_KEY = ""

# Fixed Genre
genre = "Action_Movies"

# YouTube API Client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_top_videos_by_genre(genre, max_results=500):
    results = []
    next_page_token = None
    while len(results) < max_results:
        try:
            request = youtube.search().list(
                part="id,snippet",
                maxResults=50,
                q=genre,
                type="video",
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                results.append(item['id']['videoId'])
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
            else:
                break
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            break
    return results[:max_results]

def get_video_details(video_id):
    try:
        request = youtube.videos().list(
            part="id,snippet,statistics,contentDetails,topicDetails,recordingDetails",
            id=video_id
        )
        response = request.execute()
        if response['items']:
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            contentDetails = item['contentDetails']
            topicDetails = item.get('topicDetails', {})
            recordingDetails = item.get('recordingDetails', {})
            
            return {
                'Video URL': f"https://youtu.be/{video_id}",
                'Title': snippet['title'],
                'Description': snippet['description'],
                'Channel Title': snippet['channelTitle'],
                'Keyword Tags': ', '.join(snippet.get('tags', [])),  # Simplified
                'YouTube Video Category': snippet.get('categoryId', 'Not Available'),
                'Topic Details': ', '.join(topicDetails.get('topicIds', [])),  # Simplified
                'Video Published at': snippet['publishedAt'],
                'Video Duration': contentDetails['duration'],
                'View Count': statistics.get('viewCount', '0'),
                'Comment Count': statistics.get('commentCount', '0'),
            }
        else:
            return {}
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred while fetching video {video_id}: {e.content}")
        return {}

def main():
    video_ids = get_top_videos_by_genre(genre)
    
    with open('video_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Video URL', 'Title', 'Description', 'Channel Title', 
            'Keyword Tags', 'YouTube Video Category', 'Topic Details', 
            'Video Published at', 'Video Duration', 'View Count', 
            'Comment Count'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for video_id in video_ids:
            video_data = get_video_details(video_id)
            writer.writerow(video_data)
            print(f"Saved: {video_data.get('Title', 'Unknown')}")
    print("Video data saved to 'video_data.csv'.")

if __name__ == "__main__":
    main()

