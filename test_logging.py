#!/usr/bin/env python3
"""
Test script to verify the logging system works correctly
"""

import time
import threading
import queue
from modules.garak_scanner import log_queue, get_latest_logs, scan_complete

def simulate_garak_output():
    """Simulate garak output for testing"""
    messages = [
        "Starting Garak scan...",
        "Loading model: phi3",
        "Running probe: dan.DAN_Jailbreak",
        "Generating test prompts...",
        "Analyzing responses...",
        "Scan completed successfully!"
    ]
    
    for i, message in enumerate(messages):
        time.sleep(1)  # Simulate processing time
        log_output = f"[{time.strftime('%H:%M:%S')}] {message}\n"
        try:
            log_queue.put_nowait(log_output)
            print(f"Added to queue: {message}")
        except queue.Full:
            print(f"Queue full, skipped: {message}")
    
    # Send completion signal
    try:
        log_queue.put_nowait("__SCAN_COMPLETE__")
        print("Sent completion signal")
    except queue.Full:
        print("Queue full, couldn't send completion signal")

def test_log_processing():
    """Test the log processing functionality"""
    print("Starting log processing test...")
    
    # Start the simulation in a background thread
    thread = threading.Thread(target=simulate_garak_output, daemon=True)
    thread.start()
    
    # Monitor the queue for updates
    start_time = time.time()
    while time.time() - start_time < 10:  # Run for 10 seconds
        latest_logs = get_latest_logs()
        if latest_logs:
            if latest_logs == "__SCAN_COMPLETE__":
                print("✅ Completion signal received!")
                break
            else:
                print(f"📝 Log update: {len(latest_logs)} characters")
        time.sleep(0.5)
    
    print(f"Test completed. Scan complete: {scan_complete}")

if __name__ == "__main__":
    test_log_processing() 