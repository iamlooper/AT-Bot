#!/bin/bash

# Function to check for updates and restart if necessary
check_and_update() {
    # Fetch the latest changes
    git fetch origin

    # Compare local and remote HEADs
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})

    if [ $LOCAL != $REMOTE ]; then
        echo "Updates available. Updating now..."
        
        # Kill the main process
        kill -9 $MAIN_PID

        # Force pull the latest changes
        git pull --force

        # Upgrade python packages
        echo "Upgrading python packages..."
        pip install -qUr requirements.txt

        # Get and print commit details
        echo "Update successful. Commit details:"
        git log -1

        # Restart the main script
        python main.py --auto &
        MAIN_PID=$!
    fi
}

# Start the main script
python main.py --auto &
MAIN_PID=$!

# Continuous loop to check for updates
while true; do
    check_and_update
    sleep 10
done