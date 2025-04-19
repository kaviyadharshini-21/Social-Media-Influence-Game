# Social Media Influencer Game Theory Analysis

A web application that analyzes social media influencer strategies using game theory concepts, particularly Nash Equilibrium and evolutionary game theory.

## Features

- User authentication and role-based access control
- Interactive dashboard for strategy analysis
- Nash Equilibrium visualization
- Evolutionary game theory analysis
- Voting system for strategy evaluation
- Data visualization and reporting

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
- Create a MySQL database named 'Social_Media_Influencer_Game'
- Update the database configuration in `app.py` with your credentials

5. Create a `.env` file with the following variables:
```
FLASK_SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=Social_Media_Influencer_Game
```

## Project Structure

```
├── app.py                 # Main Flask application
├── main.py               # Data processing module
├── generate_nash_visualization.py  # Nash equilibrium visualization
├── evolgametheory.py     # Evolutionary game theory analysis
├── requirements.txt      # Project dependencies
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, images)
└── .env                 # Environment variables
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

3. Login with appropriate credentials:
   - Admin users can access all features
   - Regular users can participate in voting and view analysis

## Features in Detail

### Strategy Analysis
- View and analyze different influencer strategies
- Calculate Nash Equilibrium for strategy pairs
- Visualize strategy outcomes

### Voting System
- Participate in strategy evaluation
- View voting results and statistics
- Export voting data

### Data Visualization
- Interactive charts and graphs
- Strategy comparison tools
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries or support, please contact the project maintainers. 