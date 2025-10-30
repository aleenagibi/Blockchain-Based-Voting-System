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
<img width="1916" height="910" alt="image" src="https://github.com/user-attachments/assets/ce4c2568-bc8a-41e7-bff4-d70783d324a1" />

1. **Register**: Click "Register Voter" and fill in your details
<img width="1145" height="864" alt="image" src="https://github.com/user-attachments/assets/9ba7e130-8359-4bc2-8e43-617a7d4e4ccf" />

2. **Login**: Use your Voter ID and password to login
<img width="559" height="739" alt="image" src="https://github.com/user-attachments/assets/9c74c089-ef7e-48ba-adf3-6a061cc99b60" />

3. **Vote**: Select your preferred political party and submit
<img width="582" height="913" alt="image" src="https://github.com/user-attachments/assets/0588dd33-a5b7-45db-9baa-e32ef0f98f49" />
<img width="750" height="916" alt="image" src="https://github.com/user-attachments/assets/80fb9af8-978f-41eb-8bc4-09cd19fbe64a" />

### For Administrators
1. **Login**: Use admin credentials (default: username: `admin`, password: `admin123`)
<img width="816" height="787" alt="image" src="https://github.com/user-attachments/assets/2bf0be10-448a-40fc-8dc4-f103c85bf7b1" />

2. **Dashboard**: View real-time results, blockchain ledger, and winner

Real-time Results:
<img width="1331" height="821" alt="image" src="https://github.com/user-attachments/assets/403f0ee5-7a45-4ef4-9ec3-c928e930d226" />
Blockchain Ledger:
<img width="1149" height="909" alt="image" src="https://github.com/user-attachments/assets/a1f2d31f-a0bb-471d-a499-1d1d79d5316c" />
Validator Login:
<img width="582" height="540" alt="image" src="https://github.com/user-attachments/assets/e2968033-9ca4-441f-9f90-dd82a0353492" />
<img width="1152" height="913" alt="image" src="https://github.com/user-attachments/assets/29cde4da-f1b4-4a87-9100-8e1dd345f0b8" />



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





