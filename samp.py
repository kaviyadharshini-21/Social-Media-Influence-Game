import mysql.connector
from mysql.connector import Error
from flask import session
from groq import Groq
import os


def Areas_to_improve(Vote_cnt, influencer_details):
        try:
            client = Groq(
                api_key="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"
            )
            
            # Prepare the analysis prompt with vote data and influencer details
            analysis_prompt = f"""
            Analyze the following social media influencer data using Game Theory and Evolutionary Analysis principles:

            Vote Data (Monthly Performance):
            {Vote_cnt}

            Influencer Profile:
            {influencer_details}

            Please provide a strategic analysis focusing on:
            1. Competitive positioning and strategy effectiveness
            2. Audience behavior patterns and engagement evolution
            3. Content strategy adaptation recommendations
            4. Growth opportunities based on voting trends

            Format the response with clear sections:
            Issue: [specific issue identified]
            Impact: [detailed impact analysis]
            Recommendation: [actionable recommendation]
            """

            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000
            )
            response = chat_completion.choices[0].message.content
            
        
            
            return response
            
        except Exception as e:
            print(f"Error in Areas_to_improve: {str(e)}")
            # Fallback to basic analysis if API fails
            return [
                {
                    "title": "Performance Analysis",
                    "icon": "fas fa-chart-bar",
                    "issue": "Monthly voting patterns show varying engagement levels",
                    "impact": "Understanding performance trends across different strategies",
                    "recommendation": "Focus on strategies with consistent positive votes"
                },
                {
                    "title": "Strategy Effectiveness",
                    "icon": "fas fa-bullseye",
                    "issue": "Different strategies show varying success rates",
                    "impact": "Identifying most effective approaches",
                    "recommendation": "Optimize top-performing strategies based on vote data"
                },
                {
                    "title": "Growth Opportunities",
                    "icon": "fas fa-rocket",
                    "issue": "Analysis of voting trends reveals growth potential",
                    "impact": "Opportunities for audience expansion",
                    "recommendation": "Implement strategies based on positive voting patterns"
                }
            ]



print(Areas_to_improve(Vote_cnt="total 46 votes", influencer_details="Insta influencer with 50 followers"))
