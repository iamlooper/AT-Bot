#!/bin/bash

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

stop_main_process() {
    if [ -n "$MAIN_PID" ]; then
        kill -TERM $MAIN_PID 2>/dev/null
        for i in {1..30}; do
            if ! kill -0 $MAIN_PID 2>/dev/null; then
                log_message "Main process stopped gracefully"
                return
            fi
            sleep 1
        done
        log_message "Forcing termination of main process"
        kill -9 $MAIN_PID 2>/dev/null
    fi
}

install_packages() {
    log_message "Installing python packages..."
    pip install -qr requirements.txt
}

update_and_restart() {
    log_message "Updating..."
    stop_main_process
    git pull --force --quiet
    install_packages
    log_message "Update complete: $(git log -1 --oneline)"
    start_main_process
}

start_main_process() {
    python main.py --auto &
    MAIN_PID=$!
    log_message "Started main process (PID: $MAIN_PID)"
}

check_for_updates() {
    git fetch origin main --quiet
    if [ $(git rev-list HEAD...origin/main --count) -gt 0 ]; then
        update_and_restart
    fi
}

trap 'stop_main_process; exit' SIGINT SIGTERM

# Install SQLite (using Alpine)
apk update
apk add -q --no-cache sqlite-dev

install_packages

start_main_process

# Main loop to periodically check for updates
while true; do
    check_for_updates
    sleep 60  # Wait for 60 seconds before next check
done