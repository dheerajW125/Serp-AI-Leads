#!/bin/bash

# Path to your virtual environment and the main script
VENV_PATH="/mnt/RAPIDAPI-EXTERNAL/Serp-AI-Leads/.venv/bin/activate"
SCRIPT_PATH="/mnt/RAPIDAPI-EXTERNAL/Serp-AI-Leads/main_app.py"
LOG_DIR="//mnt/RAPIDAPI-EXTERNAL/Serp-AI-Leads/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Define lock file path
LOCK_FILE="/mnt/RAPIDAPI-EXTERNAL/Serp-AI-Leads/serp-ai-leads.lock"

# Check if the lock file exists (if the script is already running)
if [ -f "$LOCK_FILE" ]; then
  echo "Previous instance is still running. Exiting." >> "$LOG_DIR/$(date +\%Y-\%m-\%d).log"
  exit 1
fi

# Create the lock file
touch "$LOCK_FILE"

# Activate the virtual environment and run the script, logging output
{
  echo "Running main_app.py at $(date)"
  source "$VENV_PATH"
  python "$SCRIPT_PATH"
} >> "$LOG_DIR/$(date +\%Y-\%m-\%d).log" 2>&1

# Remove the lock file after the script finishes
rm "$LOCK_FILE"

#*/5 * * * * /mnt/RAPIDAPI-EXTERNAL/Serp-AI-Leads/run_main.sh
