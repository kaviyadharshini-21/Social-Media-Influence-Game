from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
from main import DataProcessor
import os
from dotenv import load_dotenv
import markdown2  # Add this import

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Get from environment or use default

# MySQL Configuration
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

# Add Markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    return markdown2.markdown(text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').lower()  # Convert to lowercase
    user_type = request.form.get('user_type')
    password = request.form.get('password')

    print(f"Login attempt - Username: {username}, User Type: {user_type}")  # Debugging

    if user_type == 'user':
        if username.strip():  # Check if username is not empty
            session['username'] = username
            session['user_type'] = user_type
            return redirect(url_for('voting'))
        else:
            flash('Please enter your name', 'error')
    elif user_type == 'influencer':
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                # Query to check credentials against users table
                query = "SELECT * FROM users WHERE LOWER(username) = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                
                if user:
                    session['username'] = user['username']  # Use the exact username from DB
                    session['user_type'] = user_type
                    print(f"Successful influencer login for {user['username']}")  # Debug successful login
                    return redirect(url_for('dashboard'))
                else:
                    print(f"Failed influencer login - Invalid credentials")  # Debug failed login
                    flash('Invalid credentials. Please try again.', 'error')
            except Error as e:
                print(f"Database error during login: {e}")
                flash('Database error occurred', 'error')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Database connection error', 'error')
    else:
        flash('Invalid user type', 'error')

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    if connection:
        try:
            data_processor = DataProcessor(connection)
            
            # Get user profile
            user_data = data_processor.get_user_profile(session['username'])
            if not user_data:
                return redirect(url_for('logout'))
            
            # Get vote counts and strategy
            vote_data, strategy = data_processor.get_vote_counts(session['username'])
            
            # Calculate additional statistics
            vote_stats = data_processor.calculate_vote_statistics(vote_data)
            
            # Get improvement analysis
            try:
                improvement_data = data_processor.Areas_to_improve(vote_data, user_data)
            except Exception as e:
                print(f"Error getting improvement data: {str(e)}")
                improvement_data = "# Error\nUnable to generate analysis at this time."
            
            return render_template('dashboard.html', 
                                user_data=user_data,
                                vote_data=vote_data,
                                vote_stats=vote_stats,
                                strategy=strategy,
                                improvement_data=improvement_data)
            
        except Error as e:
            print(f"Database error: {e}")
            return redirect(url_for('logout'))
        finally:
            connection.close()
    
    return redirect(url_for('index'))

@app.route('/voting')
def voting():
    if 'username' not in session or session['user_type'] != 'user':
        return redirect(url_for('index'))
    
    # Fetch historical data from MySQL
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fetch data from previous months
            historical_data = {}
            for month in range(1, 4):
                cursor.execute(f"SELECT * FROM votes_month{month}")
                historical_data[f'month{month}'] = cursor.fetchall()
            
            return render_template('voting.html', 
                                username=session['username'],
                                historical_data=historical_data)
        except Error as e:
            print(f"Error fetching data: {e}")
            flash('Error loading historical data', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('voting.html', username=session['username'])

@app.route('/submit_votes', methods=['POST'])
def submit_votes():
    if 'username' not in session or session['user_type'] != 'user':
        return jsonify({'success': False, 'message': 'Please log in first'})

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Initialize vote data with logged-in username
            vote_data = {
                'Person_Name': session['username'],
                'Viral_Trend_Riding': None,
                'Niche_Expertise': None,
                'Clickbait': None,
                'Quality_Content': None,
                'Engagement_Optimization': None,
                'Paid_Promotion': None,
                'Memes_Humor': None
            }

            # Map strategy names to database columns
            strategy_mapping = {
                'viral_strategy': 'Viral_Trend_Riding',
                'niche_strategy': 'Niche_Expertise',
                'clickbait_strategy': 'Clickbait',
                'quality_strategy': 'Quality_Content',
                'engagement_strategy': 'Engagement_Optimization',
                'promotion_strategy': 'Paid_Promotion',
                'memes_strategy': 'Memes_Humor'
            }

            # Process each strategy vote
            for form_field, db_column in strategy_mapping.items():
                strategy_value = request.form.get(form_field)
                if strategy_value:
                    vote_data[db_column] = strategy_value

            # Insert votes into votes_month4
            columns = ', '.join(vote_data.keys())
            values = ', '.join(['%s'] * len(vote_data))
            query = f"INSERT INTO votes_month4 ({columns}) VALUES ({values})"
            
            # Insert the vote data
            cursor.execute(query, list(vote_data.values()))
            
            connection.commit()
            return jsonify({'success': True, 'message': 'Votes submitted successfully!'})
            
        except Error as e:
            print(f"Error submitting votes: {e}")
            return jsonify({'success': False, 'message': 'Error submitting votes'})
        finally:
            cursor.close()
            connection.close()
    
    return jsonify({'success': False, 'message': 'Database connection error'})

# Add a template filter to format large numbers
@app.template_filter('format_number')
def format_number(value):
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    return str(value)

if __name__ == '__main__':
    app.run(debug=True) 