import streamlit as st
from googleapiclient.discovery import build
import pymysql
import pandas as pd
from datetime import datetime
import re
import matplotlib.pyplot as plt

def parse_iso_date(date_str):
    """Parses ISO 8601 date strings with or without fractional seconds."""
    try:
        # Try processing with fractional seconds first
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            # Fallback to standard format
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
             # Return original string or handle failure as needed if both fail (though unlikely for this API)
             return date_str

# Function to establish MySQL connection
def mysql_connection(user, password):

    try:
        connection = pymysql.connect(
            host='localhost',
            user=user,
            password=password,
            db='bharath',
            charset='utf8mb4',

        )
        return connection
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to MySQL:{e}")
        return None
# Function to create SQL tables
def create_tables(conn):

    try:
        with conn.cursor() as cursor:
            # Create a table for channel info
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ChannelInfo (
                channel_Id VARCHAR(255) PRIMARY KEY,
                channel_Name VARCHAR(255),
                subscription_count INT,
                channel_views INT,
                Total_videos INT,
                channel_description TEXT,
                playlist_id VARCHAR(255)
            )
            """)
            # Create a table for playlist details
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PlaylistDetails (
                Playlist_Id VARCHAR(255) PRIMARY KEY,
                Title VARCHAR(255),
                Channel_Id VARCHAR(255),
                Channel_Name VARCHAR(255),
                PublishedAt DATETIME,
                Video_count INT
            )
            """)
            # Create a table for video info
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS VideoInfo (
                video_id VARCHAR(255) PRIMARY KEY,
                channel_Name VARCHAR(255),
                channel_Id VARCHAR(255),
                video_description TEXT,
                tags TEXT,
                published_At DATETIME,
                view_count INT,
                like_count INT,
                dislike_count INT,
                favorite_count INT,
                comment_count INT,
                duration VARCHAR(255),
                thumbnail VARCHAR(255),
                caption_status VARCHAR(255)
            )
            """)
            # Create a table for comment info
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS CommentInfo (
                comment_id VARCHAR(255) PRIMARY KEY,
                video_id VARCHAR(255),
                author VARCHAR(255),
                comment_published_at DATETIME,
                comment_text TEXT,
                like_count INT,
                viewer_rating VARCHAR(255),
                comment_updated_at DATETIME
            )
            """)
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error creating tables: {e}")
def clear_existing_data(conn, channel_id):

    try:
        with conn.cursor() as cursor:
            # Deleting from CommentInfo first due to foreign key dependency on VideoInfo
            cursor.execute("DELETE FROM CommentInfo WHERE video_id IN (SELECT video_id FROM VideoInfo WHERE channel_Id = %s)", (channel_id,))
            # Deleting from VideoInfo next
            cursor.execute("DELETE FROM VideoInfo WHERE channel_Id = %s", (channel_id,))
            # Deleting from PlaylistDetails next
            cursor.execute("DELETE FROM PlaylistDetails WHERE channel_Id = %s", (channel_id,))
            # Deleting from ChannelInfo last
            cursor.execute("DELETE FROM ChannelInfo WHERE channel_Id = %s", (channel_id,))
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error clearing existing data from MySQL: {e}")
# Function to migrate data from YouTube to MySQL tables
def migrate_data_to_sql(youtube, conn, channel_id):
    try:
        # Collect and insert channel details
        channel_info = get_channel_info(youtube, channel_id)
        insert_channel_info(conn, channel_info)
        # Collect and insert playlist details
        playlist_details = get_playlist_details(youtube, channel_id)
        insert_playlist_details(conn, playlist_details)
        # Collect and insert video details
        video_ids = get_videos_ids(youtube, channel_id)
        video_details = get_video_info(youtube, video_ids)
        insert_video_info(conn, video_details)
        # Collect and insert comment details
        comment_details = get_comment_info(youtube, video_ids)
        insert_comment_info(conn, comment_details)
        st.success("Data migration to SQL completed successfully!")
    except Exception as e:
        st.error(f"Error migrating data to SQL: {e}")
# Function to get channel information
def get_channel_info(youtube, channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        )
        response = request.execute()
        channel_info = {
            'channel_Id': response['items'][0]['id'],
            'channel_Name': response['items'][0]['snippet']['title'],
            'subscription_count': int(response['items'][0]['statistics']['subscriberCount']),
            'channel_views': int(response['items'][0]['statistics']['viewCount']),
            'Total_videos': int(response['items'][0]['statistics']['videoCount']),
            'channel_description': response['items'][0]['snippet']['description'],
            'playlist_id': response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        }
        return channel_info
    except Exception as e:
        st.error(f"Error fetching channel info: {e}")
        return None
# Function to insert channel information into MySQL
def insert_channel_info(conn, channel_data):
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO ChannelInfo (channel_Id, channel_Name, subscription_count, channel_views, 
            Total_videos, channel_description, playlist_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            channel_Name=VALUES(channel_Name),
            subscription_count=VALUES(subscription_count),
            channel_views=VALUES(channel_views),
            Total_videos=VALUES(Total_videos),
            channel_description=VALUES(channel_description),
            playlist_id=VALUES(playlist_id)
            """
            cursor.execute(sql, (
                channel_data['channel_Id'],
                channel_data['channel_Name'],
                channel_data['subscription_count'],
                channel_data['channel_views'],
                channel_data['Total_videos'],
                channel_data['channel_description'],
                channel_data['playlist_id']
            ))
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error inserting channel info into MySQL: {e}")
# Function to get playlist details
def get_playlist_details(youtube, channel_id):
    try:
        next_page_token = None
        all_data = []
        while True:
            request = youtube.playlists().list(
                part='snippet,contentDetails',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                data = {
                    'Playlist_Id': item['id'],
                    'Title': item['snippet']['title'],
                    'Channel_Id': item['snippet']['channelId'],
                    'Channel_Name': item['snippet']['channelTitle'],
                    'PublishedAt': item['snippet']['publishedAt'],
                    'Video_count': item['contentDetails']['itemCount']
                }
                all_data.append(data)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        return all_data
    except Exception as e:
        st.error(f"Error fetching playlist details: {e}")
        return []
# Function to insert playlist details into MySQL
def insert_playlist_details(conn, playlist_data):
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO PlaylistDetails (Playlist_Id, Title, Channel_Id, Channel_Name, PublishedAt, Video_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Title=VALUES(Title),
            Channel_Id=VALUES(Channel_Id),
            Channel_Name=VALUES(Channel_Name),
            PublishedAt=VALUES(PublishedAt),
            Video_count=VALUES(Video_count)
            """
            for data in playlist_data:
                published_at = parse_iso_date(data['PublishedAt'])
                cursor.execute(sql, (
                    data['Playlist_Id'],
                    data['Title'],
                    data['Channel_Id'],
                    data['Channel_Name'],
                    published_at,
                    data['Video_count']
                ))
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error inserting playlist info into MySQL: {e}")
# Function to get video IDs
def get_videos_ids(youtube, channel_id):
    try:
        video_ids = []
        response = youtube.channels().list(
            id=channel_id,
            part='contentDetails'
        ).execute()
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        next_page_token = None
        while True:
            response1 = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            for item in response1['items']:
                video_ids.append(item['snippet']['resourceId']['videoId'])
            next_page_token = response1.get('nextPageToken')
            if not next_page_token:
                break
        return video_ids
    except Exception as e:
        st.error(f"Error fetching video IDs: {e}")
        return []
def parse_duration(iso_duration):
    try:
      match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
      if not match:
        raise ValueError(f"Invalid ISO 8601 duration format: {iso_duration}")

      hours = int(match.group(1) or 0)
      minutes = int(match.group(2) or 0)
      seconds = int(match.group(3) or 0)

      return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        pass
# Function to get video information
def get_video_info(youtube, video_ids):
    try:
        video_data = []
        for video_id in video_ids:
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            for item in response["items"]:
                data = {
                    'video_id': item['id'],
                    'channel_Name': item['snippet']['channelTitle'],
                    'channel_Id': item['snippet']['channelId'],
                    'video_description': item["snippet"]["description"],
                    'tags': item["snippet"].get("tags", []),
                    'published_At': item["snippet"]["publishedAt"],
                    'view_count': item["statistics"]["viewCount"],
                    'like_count': item["statistics"].get("likeCount"),
                    'dislike_count': item["statistics"].get("dislikeCount", 0),
                    'favorite_count': item["statistics"]["favoriteCount"],
                    'comment_count': item["statistics"].get("commentCount", 0),
                    'duration': item["contentDetails"]["duration"],
                    'thumbnail': item["snippet"]["thumbnails"]["high"]["url"],
                    'caption_status': item["contentDetails"]["caption"]
                }
                video_data.append(data)
        return video_data
    except Exception as e:
        st.error(f"Error fetching video info: {e}")
        return []
# Function to insert video information into MySQL
def insert_video_info(conn, video_data):
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO VideoInfo (video_id, channel_Name, channel_Id, video_description, tags, published_At, view_count, like_count, dislike_count, favorite_count, comment_count, duration, thumbnail, caption_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            channel_Name=VALUES(channel_Name),
            channel_Id=VALUES(channel_Id),
            video_description=VALUES(video_description),
            tags=VALUES(tags),
            published_At=VALUES(published_At),
            view_count=VALUES(view_count),
            like_count=VALUES(like_count),
            dislike_count=VALUES(dislike_count),
            favorite_count=VALUES(favorite_count),
            comment_count=VALUES(comment_count),
            duration=VALUES(duration),
            thumbnail=VALUES(thumbnail),
            caption_status=VALUES(caption_status)
            """
            for data in video_data:
                published_at = parse_iso_date(data['published_At'])
                duration=parse_duration(data['duration'])
                cursor.execute(sql, (
                    data['video_id'],
                    data['channel_Name'],
                    data['channel_Id'],
                    data['video_description'],
                    ",".join(data['tags']),
                    published_at,
                    data['view_count'],
                    data['like_count'],
                    data['dislike_count'],
                    data['favorite_count'],
                    data['comment_count'],
                    duration,
                    data['thumbnail'],
                    data['caption_status']
                ))
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error inserting video info into MySQL: {e}")
# Function to get comment information
def get_comment_info(youtube, video_ids):
    try:
        comment_data = []
        for video_id in video_ids:
            try:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=25
                )
                response = request.execute()
                for item in response["items"]:
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    data = {
                        'comment_id': item["id"],
                        'video_id': video_id,
                        'author': comment["authorDisplayName"],
                        'comment_published_at': comment["publishedAt"],
                        'comment_text': comment["textDisplay"],
                        'like_count': comment["likeCount"],
                        'viewer_rating': comment.get("viewerRating", "none"),
                        'comment_updated_at': comment["updatedAt"]
                    }
                    comment_data.append(data)
            except Exception as e:
                if 'commentsDisabled' in str(e):
                    st.warning(f"Comments are disabled for video ID {video_id}. Skipping this video.")
                else:
                    st.error(f"Error fetching comments for video ID {video_id}: {e}")
        return comment_data
    except Exception as e:
        st.error(f"Error fetching comment info: {e}")
        return []
# Function to insert comment information into MySQL
def insert_comment_info(conn, comment_data):
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO CommentInfo (comment_id, video_id, author, comment_published_at, comment_text, like_count, viewer_rating, comment_updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            video_id=VALUES(video_id),
            author=VALUES(author),
            comment_published_at=VALUES(comment_published_at),
            comment_text=VALUES(comment_text),
            like_count=VALUES(like_count),
            viewer_rating=VALUES(viewer_rating),
            comment_updated_at=VALUES(comment_updated_at)
            """
            for data in comment_data:
                published_at = parse_iso_date(data['comment_published_at'])
                updated_at = parse_iso_date(data['comment_updated_at'])
                cursor.execute(sql, (
                    data['comment_id'],
                    data['video_id'],
                    data['author'],
                    published_at,
                    data['comment_text'],
                    data['like_count'],
                    data['viewer_rating'],
                    updated_at
                ))
        conn.commit()
    except pymysql.MySQLError as e:
        st.error(f"Error inserting comment info into MySQL: {e}")
# Function to execute SQL queries and return results as a DataFrame
def execute_query(query, user, password):
    conn = mysql_connection(user, password)
    if conn:
        try:
            df = pd.read_sql(query, conn)
            return df
        except pymysql.MySQLError as e:
            st.error(f"Error executing query: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def check_channel_id(channel_id, user, password):
    conn = mysql_connection(user, password)
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ChannelInfo WHERE channel_Id = %s", (channel_id,))
            count = cursor.fetchone()[0]
            return count > 0
    return False
def visualize_bar_chart(df):
    st.caption("YouTube Channel Data Visualization - Bar Chart")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract video data columns
    columns_channel = ['Total_videos', 'channel_views', 'subscription_count']

    # Create separate indices for each bar category
    index = range(len(df))  # Use numerical indices for clarity
    bar_width = 0.35  # Adjust bar width as needed

    # Create bars with proper positioning
    bar1 = ax.bar(index, df['channel_views'], bar_width, label='Views')
    bar2 = ax.bar([p + bar_width for p in index], df['subscription_count'], bar_width, label='Subscription')
    bar3 = ax.bar([p + 2 * bar_width for p in index], df['Total_videos'], bar_width, label='videos')

    # Calculate total values (assuming you have a 'Total_videos' column)
    total_videos = df['Total_videos'].sum()
    total_subscriptions = df['subscription_count'].sum()
    total_channel_views = df['channel_views'].sum()

    # Option 2: Text elements in Streamlit (assuming you're using Streamlit)
    st.write(f"Total Videos: {total_videos}")
    st.write(f"Total Subscriptions: {total_subscriptions}")
    st.write(f"Total Channel Views:{total_channel_views}")

    # Set labels and title
    ax.set_xlabel('channel_Name ')
    ax.set_ylabel('Counts')
    ax.set_title('Channel Information Bar Chart')

    # Set x-axis tick labels (assuming video titles are in a column named 'title')
    ax.set_xticks([p + bar_width for p in index])  # Adjust based on index positions
    ax.set_xticklabels(df['channel_Name'], rotation=0, ha='right')  # Rotate for better readability

    # Add legend and adjust layout
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)
def visualize_bar_chart2(df):

    st.caption("YouTube Video Data Visualization")

    fig, ax = plt.subplots(figsize=(10, 6))  # Set figure size for clarity

    # Extract video data columns
    video_data_columns = ['view_count', 'like_count', 'comment_count']

    # Create separate indices for each bar category
    index = range(len(df))  # Use numerical indices for clarity
    bar_width = 0.35  # Adjust bar width as needed

    # Create bars with proper positioning
    bar1 = ax.bar(index, df['view_count'], bar_width, label='Views')
    bar2 = ax.bar([p + bar_width for p in index], df['like_count'], bar_width, label='Likes')
    bar3 = ax.bar([p + 2 * bar_width for p in index], df['comment_count'], bar_width, label='Comments')

    # Set labels and title
    ax.set_xlabel('Video Title')
    ax.set_ylabel('Counts')
    ax.set_title('Video Information Bar Chart')

    # Set x-axis tick labels (assuming video titles are in a column named 'title')
    ax.set_xticks([p + bar_width for p in index])  # Adjust based on index positions
    ax.set_xticklabels(df['video_id'], rotation=45, ha='right')  # Rotate for better readability

    # Add legend and adjust layout
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

# Streamlit app
with st.sidebar:
    st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("skill take Away")
    st.caption("python scripting")
    st.caption("data collection")
    st.caption("API integration")
    st.caption("Data management using MYSQL")
    
    # DB Credentials
    db_username = st.text_input("Enter DB Username", "root")
    db_password = st.text_input("Enter DB Password", type="password")

# YouTube API key input
api_key = st.text_input("Enter your YouTube API key", type="password")
# Channel ID input
channel_id = st.text_input("Enter YouTube channel ID")
# Create MySQL tables button
if st.button("Create MySQL Tables"):
    conn = mysql_connection(db_username, db_password)
    if conn:
        create_tables(conn)
        if check_channel_id(channel_id, db_username, db_password):
            st.error("Channel ID already registered")
            update_button = st.button("Update")
            new_id_button = st.button("Not Update")
            if update_button:
                st.success("Update initiated")
            if new_id_button:
                st.session_state.channel_id = ""
        else:
            st.success("MySQL tables created successfully")
        conn.close()
# Migrate data to MySQL button
if st.button("Migrate Data to MYSQL"):
    if api_key and channel_id:
        youtube = build('youtube', 'v3', developerKey=api_key)
        conn = mysql_connection(db_username, db_password)
        if conn:
            clear_existing_data(conn, channel_id)  # Clear existing data for the new channel ID
            migrate_data_to_sql(youtube, conn, channel_id)
            conn.close()
    else:
        st.error("Please enter both YouTube API key and channel ID")
# Show data for the entered channel ID
if st.button("Show Channel Data"):
    if channel_id:
        conn = mysql_connection(db_username, db_password)
        if conn:
            query_channel = f"SELECT * FROM ChannelInfo WHERE channel_Id = '{channel_id}'"
            query_playlists = f"SELECT * FROM PlaylistDetails WHERE channel_Id = '{channel_id}'"
            query_videos = f"SELECT * FROM VideoInfo WHERE channel_Id = '{channel_id}'"
            query_comments = f"SELECT * FROM CommentInfo WHERE video_id IN (SELECT video_id FROM VideoInfo WHERE channel_Id = '{channel_id}')"
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query_channel)
                    columns_channel = [desc[0] for desc in cursor.description]
                    df_channel = pd.DataFrame(cursor.fetchall(), columns=columns_channel)
                    visualize_bar_chart(df_channel)

                    cursor.execute(query_playlists)
                    columns_playlists = [desc[0] for desc in cursor.description]
                    df_playlists = pd.DataFrame(cursor.fetchall(), columns=columns_playlists)

                    cursor.execute(query_videos)
                    columns_videos = [desc[0] for desc in cursor.description]
                    df_videos = pd.DataFrame(cursor.fetchall(), columns=columns_videos)
                    visualize_bar_chart2(df_videos)

                    cursor.execute(query_comments)
                    columns_comments = [desc[0] for desc in cursor.description]
                    df_comments = pd.DataFrame(cursor.fetchall(), columns=columns_comments)

                st.header("Channel Information")
                st.dataframe(df_channel)
                st.header("Playlists")
                st.dataframe(df_playlists)
                st.header("Videos")
                st.dataframe(df_videos)
                st.header("Comments")
                st.dataframe(df_comments)

            except pymysql.MySQLError as e:
                st.error(f"MySQL Error: {e}")
            finally:
                conn.close()
        else:
            st.error("Error connecting to MySQL. Please check your connection settings.")
    else:
        st.error("Please enter a channel ID")

# Define SQL queries to fetch complete row details
query1 = """SELECT *FROM VideoInfo"""
query2 = """SELECT ChannelInfo.*, COUNT(VideoInfo.video_id) AS video_count FROM ChannelInfo
        JOIN VideoInfo ON ChannelInfo.channel_Id = VideoInfo.channel_Id GROUP BY ChannelInfo.channel_Id
        ORDER BY video_count DESC"""
query3 = """SELECT *FROM VideoInfo ORDER BY view_count DESC LIMIT 10"""
query4 = """SELECT *FROM VideoInfo ORDER BY comment_count DESC"""
query5 = """SELECT * FROM VideoInfo ORDER BY like_count DESC"""
query6 = """SELECT *, like_count + dislike_count AS total_likes_dislikes FROM VideoInfo"""
query7 = """SELECT ChannelInfo.*, SUM(VideoInfo.view_count) AS total_views FROM ChannelInfo
        JOIN VideoInfo ON ChannelInfo.channel_Id = VideoInfo.channel_Id
        GROUP BY ChannelInfo.channel_Id"""
query8 = """SELECT DISTINCT channel_name, published_At FROM VideoInfo WHERE YEAR(published_At) = 2022"""
query9 = """SELECT channel_name,SEC_TO_TIME(AVG(TIME_TO_SEC(duration))) AS average_duration 
        FROM VideoInfo GROUP BY channel_name"""
query10 = """
        SELECT VideoInfo.video_id, VideoInfo.channel_Name, VideoInfo.comment_count
        FROM VideoInfo ORDER BY VideoInfo.comment_count DESC"""
# Streamlit sidebar and buttons for executing queries
st.sidebar.header("SQL Queries")
if st.sidebar.button("All details of all videos"):
    df = execute_query(query1, db_username, db_password)
    if not df.empty:
        st.header("All details of all videos")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Channels with most videos"):
    df = execute_query(query2, db_username, db_password)
    if not df.empty:
        st.header("Channels with most videos")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Top 10 most viewed videos"):
    df = execute_query(query3, db_username, db_password)
    if not df.empty:
        st.header("Top 10 most viewed videos")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Videos with most comments"):
    df = execute_query(query4, db_username, db_password)
    if not df.empty:
        st.header("Videos with most comments")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Videos with highest likes"):
    df = execute_query(query5, db_username, db_password)
    if not df.empty:
        st.header("Videos with highest likes")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Total likes and dislikes for each video"):
    df = execute_query(query6, db_username, db_password)
    if not df.empty:
        st.header("Total likes and dislikes for each video")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Total views for each channel"):
    df = execute_query(query7, db_username, db_password)
    if not df.empty:
        st.header("Total views for each channel")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Channels with videos published in 2022"):
    df = execute_query(query8, db_username, db_password)
    if not df.empty:
        st.header("Channels with videos published in 2022")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Average duration of videos in each channel"):
    df = execute_query(query9, db_username, db_password)
    if not df.empty:
        st.header("Average duration of videos in each channel")
        st.write(df)
    else:
        st.warning("No data found for this query.")
if st.sidebar.button("Videos with highest comments"):
    df = execute_query(query10, db_username, db_password)
    if not df.empty:
        st.header("Videos with highest comments")
        st.write(df)
    else:
        st.warning("No data found for this query.")
