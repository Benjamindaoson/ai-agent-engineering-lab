import subprocess


def main() -> None:
    try:
        version = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=30)
        if version.returncode != 0:
            print("Docker is not running. Start Docker Desktop first.")
            return
        images = subprocess.run(["docker", "images"], capture_output=True, text=True, timeout=30)
        print("Docker connection test succeeded")
        print(images.stdout)
    except FileNotFoundError:
        print("Docker CLI is not installed or not available on PATH.")
    except subprocess.TimeoutExpired:
        print("Docker check timed out. Start Docker Desktop and try again.")
    except OSError as exc:
        print("Docker check failed:")
        print(exc)


if __name__ == "__main__":
    main()
