# YouTube Data Harvesting & Warehousing Pipeline

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange?logo=mysql)
![API](https://img.shields.io/badge/API-YouTube%20Data%20v3-red?logo=youtube)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 📊 Business Use Case

In the creator economy, **data-driven content strategy is key to growth**. Content creators and marketers need to analyze engagement metrics across channels to understand what works. This application solves the problem of manual data collection by **automating the extraction, transformation, and loading (ETL)** of YouTube data into a structured SQL database. It enables users to:

- **Benchmark Competitors**: Compare metrics like views, likes, and comment counts across multiple channels.
- **Analyze Engagement**: Identify high-performing videos and understand audience sentiment through comment analysis.
- **Archive Data**: Create a persistent local warehouse of channel data for historical analysis, independent of platform availability.
- **Query Insights**: Answer complex questions (e.g., "Which videos published in 2022 have the most comments?") using SQL.

---

## 🏗️ Architecture

The system implements a classic **ETL Pipeline** with a user-friendly Streamlit interface:

```
┌─────────────────────────────────────────────────────────────┐
│                       YOUTUBE DATA API                       │
│                   (External Source System)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ JSON Response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ EXTRACTION ENGINE (Python)                               │
│  • Channel Info: Subscribers, Views, Description            │
│  • Playlist Details: Content structure                      │
│  • Video Metrics: Likes, Comments, Duration, Tags           │
│  • Comment Threads: Top-level comments and replies          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Structured Data Objects
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  🗄️ DATA WAREHOUSE (MySQL)                                  │
│  • Relational Schema: Channels ➔ Playlists ➔ Videos ➔ Comments│
│  • Idempotency: Prevents duplicate data ingestion           │
│  • Persistence: Long-term storage for querying              │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQL Queries
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  📈 ANALYTICS DASHBOARD (Streamlit)                         │
│  • Data Migration Control: Trigger ETL jobs                 │
│  • SQL Interface: Execute pre-defined analytical queries    │
│  • Visualization: Tabular display of insights               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🚀 **Automated ETL Pipeline**
- **One-Click Harvesting**: Fetch comprehensive data for any YouTube channel using just its Channel ID.
- **Deep Extraction**: Recursively retrieves all videos from uploads playlists and associated comments.
- **Smart Migration**: Seamlessly transfers harvested data into a normalized MySQL schema.

### 🗄️ **Robust Warehousing**
- **Relational Design**: Structured tables for `Channels`, `Playlists`, `Videos`, and `Comments` with proper foreign key constraints.
- **Data Integrity**: Checks for existing channel data to avoid redundancy.

### 🔍 **Advanced Analytics**
- **SQL-Powered Insights**: Built-in library of complex queries to answer business questions:
  - *Top 10 most viewed videos*
  - *Average video duration per channel*
  - *Videos with highest engagement (likes/comments)*
- **Interactive Dashboard**: User-friendly interface to input API keys, manage database connections, and view results.

---

## 💻 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.x |
| **Frontend** | Streamlit |
| **Database** | MySQL, pymysql |
| **API Integration** | google-api-python-client |
| **Data Processing** | Pandas |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server installed and running
- Google Cloud Console Project with **YouTube Data API v3** enabled

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone git@github.com:rajaganaa/YouTube-Data-ETL-Pipeline.git
   cd YouTube-Data-ETL-Pipeline
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Installs streamlit, google-api-python-client, pymysql, and pandas.*

3. **Configure Database**:
   - Ensure your MySQL server is running.
   - Update the `mysql_connection` function in `src/youtube_data_harvesting.py` with your credentials (host, user, password) if not using the UI inputs.
   - *Tip: The app allows dynamic input of API keys, but DB credentials might need initial setup.*

---

## 🚀 Usage

1. **Launch the App**:
   ```bash
   streamlit run src/youtube_data_harvesting.py
   ```

2. **Input Credentials**:
   - Enter your **YouTube API Key** in the sidebar.
   - Enter the **Channel ID** you want to analyze.

3. **Execute Workflow**:
   - **Step 1**: Click `Create MySQL Tables` to initialize the database schema.
   - **Step 2**: Click `Migrate Data to MySQL` to harvest and store data.
   - **Step 3**: Use the **SQL Query** dropdown to generate insights from the stored data.

---

## 📝 License

This project is open-source and available for educational and portfolio purposes.

---

## 👤 Author

**Rajaganapathy M**  
GitHub: [@rajaganaa](https://github.com/rajaganaa)  
Email: rajaganaa@gmail.com

---

**Built with ❤️ for Data Engineering and Analytics**
