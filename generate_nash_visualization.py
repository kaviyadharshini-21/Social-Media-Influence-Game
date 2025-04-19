import mysql.connector
import pandas as pd
import numpy as np
import nashpy as nash
import matplotlib.pyplot as plt
import os


os.makedirs('static/images', exist_ok=True)


conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'Social_Media_Influencer_Game'),
    port=int(os.getenv('DB_PORT', '3306'))
)
cursor = conn.cursor()


strategies = [
    "Viral_Trend_Riding", "Niche_Expertise", "Clickbait", "Quality_Content", 
    "Engagement_Optimization", "Paid_Promotion", "Memes_Humor"
]

payoff_I1 = np.zeros((7, 7))
payoff_I2 = np.zeros((7, 7))

total_revenue = 100000
cost_I1 = [7000, 6000, 8000, 5000, 7500, 9000, 6500]
cost_I2 = [6500, 5500, 8500, 4500, 7000, 9500, 6000]

for i, strategy1 in enumerate(strategies):
    for j, strategy2 in enumerate(strategies):
        query = f"""
            SELECT 
                SUM(CASE WHEN {strategy1} = 'I1' THEN 1 ELSE 0 END) AS I1_Votes,
                SUM(CASE WHEN {strategy2} = 'I2' THEN 1 ELSE 0 END) AS I2_Votes
            FROM (
                FROM Votes WHERE MONTH(V_Date) IN (1, 2, 3, 4)
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

print("Nash Equilibria:", equilibria)

plt.figure(figsize=(12, 10))
ax = plt.subplot(111)


im = ax.imshow(payoff_I1, cmap='Blues', alpha=0.7)
plt.colorbar(im, label='Influencer 1 Payoff')

ax.set_xticks(range(7))
ax.set_yticks(range(7))
ax.set_xticklabels([s.replace('_', ' ') for s in strategies], rotation=45, ha="right")
ax.set_yticklabels([s.replace('_', ' ') for s in strategies])
ax.set_xlabel("Influencer 1 Strategies", fontsize=12)
ax.set_ylabel("Influencer 2 Strategies", fontsize=12)
ax.set_title("Nash Equilibrium for Social Media Strategy Game", fontsize=16)


if equilibria:
    for eq in equilibria:
        best_I1 = np.argmax(eq[0])
        best_I2 = np.argmax(eq[1])
        ax.plot(best_I1, best_I2, 'ro', markersize=12, label="Nash Equilibrium")
        
  
        ax.axvline(best_I1, color='#1c346c', linestyle='--', alpha=0.6)
        ax.axhline(best_I2, color='#1c346c', linestyle='--', alpha=0.6)
        

        payoff_text = f"I1: ${int(payoff_I1[best_I1, best_I2])}\nI2: ${int(payoff_I2[best_I1, best_I2])}"
        ax.annotate(payoff_text, 
                   xy=(best_I1, best_I2),
                   xytext=(best_I1+0.5, best_I2+0.5),
                   fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper right')

plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()

plt.savefig('static/images/nash_equilibrium.png', dpi=300, bbox_inches='tight')
print("Visualization saved to static/images/nash_equilibrium.png")

cursor.close()
conn.close() 