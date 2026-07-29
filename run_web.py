import subprocess
import sys
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "src", "app.py")
    print(f"Launching ApexSupport AI Web UI via: {sys.executable} src/app.py\n")
    try:
        subprocess.run([sys.executable, app_path])
    except KeyboardInterrupt:
        print("\nWeb server stopped.")
