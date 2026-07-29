import subprocess
import sys
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cli_path = os.path.join(script_dir, "src", "ASSIST.py")
    print(f"Launching ApexSupport AI CLI Client via: {sys.executable} src/ASSIST.py\n")
    try:
        subprocess.run([sys.executable, cli_path])
    except KeyboardInterrupt:
        print("\nCLI stopped.")
