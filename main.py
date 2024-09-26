import subprocess

def run_files():
    subprocess.run(["python", "clean.py"])
    subprocess.run(["python", "general_stats.py"])
    subprocess.run(["python", "position.py"])
    subprocess.run(["python", "individual.py"])

if __name__ == "__main__":
    run_files()