#!/bin/bash

# Function to stop the main process gracefully, then forcefully if necessary
stop_main_process() {
    if kill -TERM $MAIN_PID 2>/dev/null; then
        echo "Sent SIGTERM to main process $MAIN_PID. Waiting for it to exit..."
        for i in {1..30}; do
            if ! kill -0 $MAIN_PID 2>/dev/null; then
                echo "Main process stopped gracefully."
                return
            fi
            sleep 1
        done
    fi

    if kill -0 $MAIN_PID 2>/dev/null; then
        echo "Main process did not stop gracefully. Forcing termination..."
        kill -9 $MAIN_PID
        echo "Main process terminated forcefully."
    fi
}

# Function to check for updates and restart if necessary
check_and_update() {
    # Fetch the latest changes
    git fetch origin --quiet

    # Compare local and remote HEADs
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})

    if [ $LOCAL != $REMOTE ]; then
        echo "Updates available. Updating now..."
        
        # Stop the main process
        stop_main_process

        # Force pull the latest changes
        git pull --force --quiet

        # Upgrade python packages
        echo "Upgrading python packages..."
        pip install -qUr requirements.txt

        # Get and print commit details
        echo "Update successful. Commit details:"
        git log -1 --oneline

        # Restart the main script
        python main.py --auto &
        MAIN_PID=$!
    fi
}

# Install SQLite
apt update
apt install -y libsqlite3-dev

# Install python packages
echo "Installing python packages..."
pip install -qUr requirements.txt

# Start the main script
python main.py --auto &
MAIN_PID=$!

# Continuous loop to check for updates
while true; do
    check_and_update
    sleep 60
done