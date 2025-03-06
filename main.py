from multiprocessing import Process
import os
import time

# Define functions to run each bot
def run_ban_bot():
    os.system("python bantest.py")  # Update with the correct script name

def run_clean_bot():
    os.system("python clean.py")  # Update with the correct script name

def run_leave_bot():
    os.system("python leave.py")  # Update with the correct script name

def run_find_bot():
    os.system("python find.py")  # Update with the correct script name

def run_set_bot():
    os.system("python set.py")  # Update with the correct script name

if __name__ == "__main__":
    # Create processes for all four scripts
    p1 = Process(target=run_ban_bot)
    p2 = Process(target=run_clean_bot)
    p3 = Process(target=run_leave_bot)
    p4 = Process(target=run_find_bot)
    p5 = Process(target=run_set_bot)
    # Start all processes
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()

    print("✅ All bots are running!")

    try:
        while True:
            time.sleep(10)  # Keep the script alive
    except KeyboardInterrupt:
        print("⛔ Stopping all bots...")

        # Gracefully terminate all bots
        p1.terminate()
        p2.terminate()
        p3.terminate()
        p4.terminate()
        p5.terminate()

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()

        print("🚀 All bots stopped successfully!")
