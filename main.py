#!/usr/bin/env python3
"""
Google Cloud App Engine Entry Point
This file serves as the entry point for Google Cloud App Engine deployment
"""

import os
import subprocess
import sys

def main():
    """Main entry point for Google Cloud App Engine"""
    
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = os.environ.get('PORT', '8080')
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Run Streamlit dashboard
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'dashboard.py',
            '--server.port', os.environ['STREAMLIT_SERVER_PORT'],
            '--server.address', os.environ['STREAMLIT_SERVER_ADDRESS'],
            '--server.headless', 'true'
        ])
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
