import mysql.connector
import pandas as pd
import numpy as np

def analyze_influencer_strategy_changes(
    host: str,
    user: str,
    password: str,
    database: str,
    current_influencer: str,  
    strategies: list = [
        "Viral_Trend_Riding", "Niche_Expertise", "Clickbait", "Quality_Content", 
        "Engagement_Optimization", "Paid_Promotion", "Memes_Humor"
    ],
    months: int = 4
):

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    # Get monthly counts for each strategy
    monthly_counts = {}
    monthly_totals = {}  

    for month in range(1, months + 1):
        query = f"""
            SELECT 
                {', '.join([f"SUM(CASE WHEN {strategy} = '{current_influencer}' THEN 1 ELSE 0 END) AS {strategy}" for strategy in strategies])},
                COUNT(*) as total_voters
            FROM Votes WHERE MONTH(V_Date) = {month};
        """
        print(f"Executing query for month {month}:")
        print(query)
        cursor.execute(query)
        result = cursor.fetchone()
        
        strategy_counts = result[:-1]
        total_voters = result[-1]
        
        print(f"Month {month} results: {strategy_counts}, Total voters: {total_voters}")
        
        monthly_counts[f"Month_{month}"] = dict(zip(strategies, strategy_counts))
        monthly_totals[f"Month_{month}"] = total_voters
    
    evolution_results = {}
    
    for i in range(1, months):
        month_key1 = f"Month_{i}"
        month_key2 = f"Month_{i+1}"
        comparison_key = f"{month_key1}vs{month_key2}"
        evolution_results[comparison_key] = {}

        total_prev_month = sum([count or 0 for count in monthly_counts[month_key1].values()])
        total_curr_month = sum([count or 0 for count in monthly_counts[month_key2].values()])
        if total_prev_month == 0:
            total_prev_month = 1
        if total_curr_month == 0:
            total_curr_month = 1

        for strategy in strategies:
            prev_count = monthly_counts[month_key1][strategy] or 0  
            curr_count = monthly_counts[month_key2][strategy] or 0 

            prev_fitness = prev_count / total_prev_month if total_prev_month > 0 else 0
            curr_fitness = curr_count / total_curr_month if total_curr_month > 0 else 0
            
            selection_coefficient = (curr_fitness - prev_fitness) / prev_fitness if prev_fitness > 0 else 0
            
            if prev_count > 0:
                percentage_change = ((curr_count - prev_count) / prev_count) * 100
            else:
                percentage_change = 0 if curr_count == 0 else 100
            
            if selection_coefficient > 0.1: 
                status = "Adaptation"
            elif selection_coefficient < -0.1:  
                status = "Mutation"
            else:  
                status = "Stability"
            
            evolution_results[comparison_key][strategy] = {
                "Previous_Count": prev_count,
                "Current_Count": curr_count,
                "Percentage_Change": percentage_change,
                "Relative_Fitness": curr_fitness * 100,  
                "Selection_Coefficient": selection_coefficient,
                "Status": status
            }

    cursor.close()
    conn.close()
    return evolution_results
