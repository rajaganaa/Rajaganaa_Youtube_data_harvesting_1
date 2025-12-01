# Rajaganaa_Youtube_data_harvesting_1

# YouTube Data Harvesting and Warehousing

This project involves building a Streamlit application to harvest data from YouTube using the YouTube Data API and store it in a MySQL database. The application allows users to view and query this data through various SQL queries.

## Features

- Fetch channel information, playlist details, video details, and comments from a YouTube channel.
- Store the fetched data in a MySQL database.
- Perform SQL queries on the stored data and display the results in the Streamlit app.

## Requirements

- Python 3.x
- Streamlit
- google-api-python-client
- pymysql
- pandas

## Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up your MySQL database:**

    - Create a database named `bharath` (or modify the code to use your preferred database name).
    - Ensure your MySQL server is running and you have the necessary privileges to create tables and insert data.

## Usage

1. **Run the Streamlit application:**

    ```bash
    streamlit run src/youtube_data_harvesting.py
    ```

2. **Enter your YouTube API key and channel ID:**

    - You can obtain a YouTube API key from the Google Developer Console.
    - Enter the channel ID of the YouTube channel you wish to fetch data from.

3. **Create MySQL Tables:**

    - Click the "Create MySQL Tables" button to create the necessary tables in your MySQL database.

4. **Migrate Data to MySQL:**

    - Click the "Migrate Data to MySQL" button to fetch and store data from the specified YouTube channel.

5. **Show Channel Data:**

    - Click the "Show Channel Data" button to view the fetched data in the app.

6. **Execute SQL Queries:**

    - Use the sidebar to execute predefined SQL queries and view the results.

## SQL Queries

The application supports the following SQL queries:

- **All details of all videos**
- **Channels with most videos**
- **Top 10 most viewed videos**
- **Videos with most comments**
- **Videos with highest likes**
- **Total likes and dislikes for each video**
- **Total views for each channel**
- **Channels with videos published in 2022**
- **Average duration of videos in each channel**
- **Videos with highest comments**

## Code Overview

### Functions

- **mysql_connection**: Establishes a connection to the MySQL database.
- **create_tables**: Creates the necessary tables in the MySQL database.
- **clear_existing_data**: Clears existing data for a specified channel ID.
- **migrate_data_to_sql**: Migrates data from YouTube to MySQL tables.
- **get_channel_info**: Fetches channel information from YouTube.
- **insert_channel_info**: Inserts channel information into MySQL.
- **get_playlist_details**: Fetches playlist details from YouTube.
- **insert_playlist_details**: Inserts playlist details into MySQL.
- **get_videos_ids**: Fetches video IDs from a YouTube channel.
- **get_video_info**: Fetches video information from YouTube.
- **insert_video_info**: Inserts video information into MySQL.
- **get_comment_info**: Fetches comment information from YouTube.
- **insert_comment_info**: Inserts comment information into MySQL.
- **execute_query**: Executes an SQL query and returns the result as a DataFrame.

### Streamlit App

- Sidebar for YouTube API key and channel ID input.
- Buttons for creating MySQL tables, migrating data, and showing channel data.
- Sidebar buttons for executing predefined SQL queries.

## Note

- Ensure to replace `host`, `user`, `password`, and `database` in the `mysql_connection` function with your MySQL server details.
- Handle sensitive information like database credentials and API keys securely in a production environment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
