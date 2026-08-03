# AI Dashboard - Flask System Core

A modern, responsive web application built with Python Flask, featuring a neon-green dark theme, automated backend records generation, and a secure admin panel.

## Features
- **Mobile Responsive & Bootstrap 5:** Fits seamlessly on Android devices.
- **REST APIs:** Read and query database records via JSON.
- **Auto-Refresh:** Frontend pings the backend every 5 seconds for live updates.
- **Background Scheduler:** APScheduler automatically simulates a new record every 60 seconds.
- **Data Export:** Admins can export the SQLite database history securely to CSV format.
- **Chart.js Statistics:** Visual data display on the admin panel.

## Installation & Setup

1. **Clone or Download the Repository.**
2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   