from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
from main import DataProcessor
import os
from dotenv import load_dotenv
import markdown2  # Add this import
import numpy as np
import nashpy as nash
import pandas as pd
import matplotlib.pyplot as plt
from evolgametheory import analyze_influencer_strategy_changes

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Get from environment or use default

# MySQL Configuration using environment variables
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'Social_Media_Influencer_Game'),
    'port': int(os.getenv('DB_PORT', '3306'))
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
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'header-ids', 'smarty-pants', 'cuddled-lists'])

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
                    session['username'] = user['username']  
                    session['user_type'] = user_type
                    print(f"Successful influencer login for {user['username']}")  
                    return redirect(url_for('dashboard'))
                else:
                    print(f"Failed influencer login - Invalid credentials")  
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
            
            # Get improvement analysis - fixed error handling
            try:
                improvement_data = data_processor.Areas_to_improve(vote_data, user_data)
            except Exception as e:
                print(f"Error in Areas_to_improve: {str(e)}")
                # Provide default content instead of failing completely
                improvement_data = """
# Areas for Improvement

## Analysis Currently Unavailable

We're currently experiencing issues with the analysis system. Here are some general recommendations:

1. **Diversify your content strategies** - Try experimenting with different content types
2. **Engage with your audience** - Respond to comments and messages
3. **Post consistently** - Maintain a regular posting schedule

Our team is working to restore the full analysis functionality.
"""
            
            # Nash Equilibrium analysis (from trialnashproj.py)
            try:
                strategies = [
                    "Viral_Trend_Riding", "Niche_Expertise", "Clickbait", "Quality_Content", 
                    "Engagement_Optimization", "Paid_Promotion", "Memes_Humor"
                ]

                payoff_I1 = np.zeros((7, 7))
                payoff_I2 = np.zeros((7, 7))

                total_revenue = 100000
                cost_I1 = [7000, 6000, 8000, 5000, 7500, 9000, 6500]
                cost_I2 = [6500, 5500, 8500, 4500, 7000, 9500, 6000]

                cursor = connection.cursor()
                for i, strategy1 in enumerate(strategies):
                    for j, strategy2 in enumerate(strategies):
                        query = f"""
                            SELECT 
                                SUM(CASE WHEN {strategy1} = 'I1' THEN 1 ELSE 0 END) AS I1_Votes,
                                SUM(CASE WHEN {strategy2} = 'I2' THEN 1 ELSE 0 END) AS I2_Votes
                            FROM (
                                SELECT * FROM Votes WHERE MONTH(V_Date) IN (1, 2, 3, 4)
                            ) AS combined_votes;
                        """
                        cursor.execute(query)
                        result = cursor.fetchone()
                        I1_votes, I2_votes = result if result else (0, 0)
                        
                        total_votes = I1_votes + I2_votes
                        I1_revenue = (I1_votes / total_votes) * total_revenue if total_votes > 0 else 0
                        I2_revenue = (I2_votes / total_votes) * total_revenue if total_votes > 0 else 0
                        
                        payoff_I1[i, j] = I1_revenue - cost_I1[i]
                        payoff_I2[i, j] = I2_revenue - cost_I2[j]

                influencer_game = nash.Game(payoff_I1, payoff_I2)
                equilibria = list(influencer_game.support_enumeration())
                
                # Generate Nash equilibrium visualization
                img_path = os.path.join(app.static_folder, 'images', 'nash_equilibrium.png')
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                
                plt.figure(figsize=(12, 10))
                ax = plt.subplot(111)
                
                # Create heatmap for payoff values
                im = ax.imshow(payoff_I1, cmap='Blues', alpha=0.7)
                plt.colorbar(im, label='Influencer 1 Payoff')
                
                # Set grid, labels, and title
                ax.set_xticks(range(7))
                ax.set_yticks(range(7))
                ax.set_xticklabels([s.replace('_', ' ') for s in strategies], rotation=45, ha="right")
                ax.set_yticklabels([s.replace('_', ' ') for s in strategies])
                ax.set_xlabel("Influencer 1 Strategies", fontsize=12)
                ax.set_ylabel("Influencer 2 Strategies", fontsize=12)
                ax.set_title("Nash Equilibrium for Social Media Strategy Game", fontsize=16)
                
                # Prepare data for the template
                nash_equilibria = []
                best_strategy = ""
                max_payoff = float('-inf')
                
                if equilibria:
                    for eq in equilibria:
                        best_I1 = np.argmax(eq[0])
                        best_I2 = np.argmax(eq[1])
                        
                        # Add to visualization
                        ax.plot(best_I1, best_I2, 'ro', markersize=12, label="Nash Equilibrium")
                        ax.axvline(best_I1, color='#1c346c', linestyle='--', alpha=0.6)
                        ax.axhline(best_I2, color='#1c346c', linestyle='--', alpha=0.6)
                        
                        # Add annotation for payoff values
                        payoff_text = f"I1: ${int(payoff_I1[best_I1, best_I2])}\nI2: ${int(payoff_I2[best_I1, best_I2])}"
                        ax.annotate(payoff_text, 
                                   xy=(best_I1, best_I2),
                                   xytext=(best_I1+0.5, best_I2+0.5),
                                   fontsize=10,
                                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
                        
                        payoff1 = payoff_I1[best_I1, best_I2]
                        payoff2 = payoff_I2[best_I1, best_I2]
                        
                        if payoff1 > max_payoff:
                            max_payoff = payoff1
                            best_strategy = strategies[best_I1].replace('_', ' ')
                        
                        nash_equilibria.append({
                            'strategy1': strategies[best_I1].replace('_', ' '),
                            'strategy2': strategies[best_I2].replace('_', ' '),
                            'payoff1': payoff1,
                            'payoff2': payoff2
                        })
                
                # Remove duplicate labels in plot
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys(), loc='upper right')
                
                plt.grid(True, linestyle='--', alpha=0.3)
                plt.tight_layout()
                
                # Save the visualization
                plt.savefig(img_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                cursor.close()
            except Exception as e:
                print(f"Error generating Nash equilibrium: {str(e)}")
                nash_equilibria = []
                best_strategy = "Analysis Error"
            
            # Evolutionary Game Theory analysis (from evolgametheory.py)
            try:
                # Map usernames to influencer IDs correctly based on the database
                influencer_username = session['username'].lower()
                
                # In database: "Kaviya" is I1, "Sutharshana" is I2
                if influencer_username == "kaviya":
                    current_influencer = 'I1'
                elif influencer_username == "sutharshana":
                    current_influencer = 'I2'
                else:
                    # Default fallback based on user_data id if available
                    current_influencer = 'I1' if user_data.get('id') == 1 else 'I2'
                
                print(f"Username: {influencer_username}, Determined influencer: {current_influencer}")
                
                evolution_data = analyze_influencer_strategy_changes(
                    host=db_config['host'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    current_influencer=current_influencer
                )
                
            except Exception as e:
                print(f"Error generating evolutionary analysis: {str(e)}")
                evolution_data = {}
            
            return render_template('dashboard.html', 
                                user_data=user_data,
                                vote_data=vote_data,
                                vote_stats=vote_stats,
                                strategy=strategy,
                                  improvement_data=improvement_data,
                                  nash_equilibria=nash_equilibria,
                                  best_strategy=best_strategy,
                                  evolution_data=evolution_data)
            
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

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fetch data from previous months
            historical_data = {}
            for month in range(1, 4):
                cursor.execute("SELECT * FROM Votes WHERE MONTH(V_Date) = %s", (month,))
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
            query = f"INSERT INTO Votes ({columns}, V_Date) VALUES ({values}, CURDATE())"
            
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