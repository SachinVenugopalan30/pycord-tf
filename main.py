#!/usr/bin/env python

import subprocess
import os
import signal
import time

bot_process = None
websocket_service_process = None

def start_process(script_name):
    return subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def stop_processes():
    if bot_process:
        print("Terminating bot.py...")
        os.kill(bot_process.pid, signal.SIGTERM)
    if websocket_service_process:
        print("Terminating websocket_service.py...")
        os.kill(websocket_service_process.pid, signal.SIGTERM)
    print("Subprocesses terminated.")

def signal_handler(sig, frame):
    print("Received termination signal")
    stop_processes()
    exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful termination
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start bot.py and websocket_service.py in the background
    bot_process = start_process('bot.py')
    websocket_service_process = start_process('websocket_service.py')
    
    print("Started bot.py with PID:", bot_process.pid)
    print("Started websocket_service.py with PID:", websocket_service_process.pid)

    try:
        # Keep the main script running to allow subprocesses to continue executing
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)