import mysql.connector
from mysql.connector import Error
from flask import session
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables at the start of the file
load_dotenv()

# Get API key
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaviya2004',
    'database': 'Social_Media_Influencer_Game'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def voting_details(username, password):
    connection = get_db_connection()
    if connection is None:
        return None  # Return None if connection fails
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to check credentials against users table
        query = "SELECT * FROM votes_month1 where viral_trend_riding =='l1' "
        query="select * from votes_month1 where "
        cursor.execute(query, (username.lower(), password))
        
        user = cursor.fetchone()
        
        return user  # Return user details if found
    except Error as e:
        print(f"Error in query execution: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class DataProcessor:
    def __init__(self, db_connection):
        self.connection = db_connection

    def get_user_profile(self, username):
        """Fetch user profile details from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            cursor.close()
            return user_data
        except Error as e:
            print(f"Error fetching user profile: {e}")
            return None

    def get_vote_counts(self, username):
        """Get aggregated vote counts for the influencer's strategy"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Determine strategy based on username
            strategy = 'I1' if username.lower() == 'kaviya' else 'I2'
            
            # Query to get vote counts for all months
            vote_query = """
                SELECT 
                    'Month 1' as month,
                    COUNT(CASE WHEN Viral_Trend_Riding = %s THEN 1 END) as viral_trends,
                    COUNT(CASE WHEN Niche_Expertise = %s THEN 1 END) as expertise,
                    COUNT(CASE WHEN Clickbait = %s THEN 1 END) as clickbait,
                    COUNT(CASE WHEN Quality_Content = %s THEN 1 END) as quality,
                    COUNT(CASE WHEN Engagement_Optimization = %s THEN 1 END) as engagement,
                    COUNT(CASE WHEN Paid_Promotion = %s THEN 1 END) as promotion,
                    COUNT(CASE WHEN Memes_Humor = %s THEN 1 END) as memes,
                    COUNT(*) as total_votes
                FROM votes_month1
                UNION ALL
                SELECT 
                    'Month 2' as month,
                    COUNT(CASE WHEN Viral_Trend_Riding = %s THEN 1 END) as viral_trends,
                    COUNT(CASE WHEN Niche_Expertise = %s THEN 1 END) as expertise,
                    COUNT(CASE WHEN Clickbait = %s THEN 1 END) as clickbait,
                    COUNT(CASE WHEN Quality_Content = %s THEN 1 END) as quality,
                    COUNT(CASE WHEN Engagement_Optimization = %s THEN 1 END) as engagement,
                    COUNT(CASE WHEN Paid_Promotion = %s THEN 1 END) as promotion,
                    COUNT(CASE WHEN Memes_Humor = %s THEN 1 END) as memes,
                    COUNT(*) as total_votes
                FROM votes_month2
                UNION ALL
                SELECT 
                    'Month 3' as month,
                    COUNT(CASE WHEN Viral_Trend_Riding = %s THEN 1 END) as viral_trends,
                    COUNT(CASE WHEN Niche_Expertise = %s THEN 1 END) as expertise,
                    COUNT(CASE WHEN Clickbait = %s THEN 1 END) as clickbait,
                    COUNT(CASE WHEN Quality_Content = %s THEN 1 END) as quality,
                    COUNT(CASE WHEN Engagement_Optimization = %s THEN 1 END) as engagement,
                    COUNT(CASE WHEN Paid_Promotion = %s THEN 1 END) as promotion,
                    COUNT(CASE WHEN Memes_Humor = %s THEN 1 END) as memes,
                    COUNT(*) as total_votes
                FROM votes_month3
                UNION ALL
                SELECT 
                    'Month 4' as month,
                    COUNT(CASE WHEN Viral_Trend_Riding = %s THEN 1 END) as viral_trends,
                    COUNT(CASE WHEN Niche_Expertise = %s THEN 1 END) as expertise,
                    COUNT(CASE WHEN Clickbait = %s THEN 1 END) as clickbait,
                    COUNT(CASE WHEN Quality_Content = %s THEN 1 END) as quality,
                    COUNT(CASE WHEN Engagement_Optimization = %s THEN 1 END) as engagement,
                    COUNT(CASE WHEN Paid_Promotion = %s THEN 1 END) as promotion,
                    COUNT(CASE WHEN Memes_Humor = %s THEN 1 END) as memes,
                    COUNT(*) as total_votes
                FROM votes_month4
            """
            
            params = [strategy] * 28  # 7 strategies * 4 months
            cursor.execute(vote_query, params)
            vote_data = cursor.fetchall()
            cursor.close()
            
            return vote_data, strategy
        except Error as e:
            print(f"Error fetching vote counts: {e}")
            return None, None

    def calculate_vote_statistics(self, vote_data):
        """Calculate additional statistics from vote data"""
        if not vote_data:
            return None

        total_stats = {
            'total_votes': sum(month['total_votes'] for month in vote_data),
            'highest_category': {
                'name': '',
                'votes': 0
            },
            'monthly_growth': []
        }

        # Calculate highest performing category
        categories = ['viral_trends', 'expertise', 'clickbait', 'quality', 
                     'engagement', 'promotion', 'memes']
        
        for category in categories:
            category_total = sum(month[category] for month in vote_data)
            if category_total > total_stats['highest_category']['votes']:
                total_stats['highest_category'] = {
                    'name': category.replace('_', ' ').title(),
                    'votes': category_total
                }

        # Calculate monthly growth
        for i in range(1, len(vote_data)):
            growth = ((vote_data[i]['total_votes'] - vote_data[i-1]['total_votes']) 
                     / vote_data[i-1]['total_votes'] * 100 if vote_data[i-1]['total_votes'] > 0 else 0)
            total_stats['monthly_growth'].append({
                'month': vote_data[i]['month'],
                'growth': growth
            })

        return total_stats

    def Areas_to_improve(self, Vote_cnt, influencer_details):
        try:
            client = Groq(
                api_key="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"
            )
            
            analysis_prompt = f"""
            Act like a professional data analyst specializing in Game Theory and Evolutionary Analysis. You have extensive experience in analyzing competitive environments, strategic decision-making, and adaptive behaviors in social media dynamics.

    Your task is to analyze the following social media influencer data using Game Theory principles (such as Nash Equilibrium, Payoff Matrices, and Strategic Dominance) along with Evolutionary Analysis (including adaptation, fitness landscapes, and replicator dynamics).

    Data:
    Vote Data (Monthly Performance):
    {Vote_cnt}
    (Exclude Month 4 votes from your analysis)

    Influencer Profile:
    {influencer_details}
           Provide a concise summary of key insights from the analysis.

    Use bullet points for clarity and structured results.

    Present findings in an actionable format, highlighting trends and implications.

    Keep explanations clear and free of unnecessary complexity.

    Offer data-driven reasoning behind insights.

    Take a deep breath and work on this problem step-by-step.
            """

            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }],
                model="llama-3.3-70b-versatile",
                temperature=1,
                max_tokens=700
            )
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error in Areas_to_improve: {str(e)}")
            return "Error generating analysis. Please try again later."