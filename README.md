# Blockchain-Based Voting System

A secure, transparent, and immutable voting system built with Flask and blockchain technology.

## Features

- 🔐 **Secure Authentication**: Separate login systems for voters and administrators
- 🗳️ **Vote Casting**: Easy-to-use interface for casting votes
- 🔗 **Blockchain Integration**: All votes are recorded in an immutable blockchain
- 📊 **Real-time Dashboard**: Live voting results with charts and blockchain ledger
- 🛡️ **Vote Integrity**: Each voter can only vote once
- 🎨 **Modern UI**: Responsive design with Bootstrap 5

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd "Voting system"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## Usage

### For Voters
1. **Register**: Click "Register Voter" and fill in your details
2. **Login**: Use your Voter ID and password to login
3. **Vote**: Select your preferred political party and submit

### For Administrators
1. **Login**: Use admin credentials (default: username: `admin`, password: `admin123`)
2. **Dashboard**: View real-time results, blockchain ledger, and winner

## Security Features

- **Environment Variables**: Set `SECRET_KEY` and `ADMIN_PASSWORD` environment variables for production
- **Blockchain Validation**: Automatic integrity checks on the blockchain
- **One Vote Per Voter**: Prevents duplicate voting
- **Session Management**: Secure session handling

## Production Deployment

For production deployment, set these environment variables:
```bash
export SECRET_KEY="your-secure-secret-key"
export ADMIN_PASSWORD="your-secure-admin-password"
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight database)
- **Blockchain**: Custom implementation with SHA-256 hashing
- **Frontend**: Bootstrap 5, Chart.js
- **Security**: Session-based authentication

## File Structure

```
Voting system/
├── app.py                 # Main Flask application
├── blockchain.py          # Blockchain implementation
├── database.db           # SQLite database (created automatically)
├── requirements.txt      # Python dependencies
├── templates/           # HTML templates
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── vote.html        # Voting page
│   └── admin_dashboard.html # Admin dashboard
└── README.md            # This file
```

## Contributing

Feel free to submit issues and enhancement requests!


