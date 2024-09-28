import os
import re
import sys
import time
import signal
import shutil
import tempfile
import subprocess
import threading
import shlex

from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
SMB_USERNAME = os.getenv("SMB_USERNAME")
SMB_PASSWORD = os.getenv("SMB_PASSWORD")
SMB_INPUT_SERIES = os.getenv("SMB_INPUT_SERIES")
SMB_OUTPUT_SERIES = os.getenv("SMB_OUTPUT_SERIES")
SMB_INPUT_MOVIES = os.getenv("SMB_INPUT_MOVIES")
SMB_OUTPUT_MOVIES = os.getenv("SMB_OUTPUT_MOVIES")
CRF = os.getenv("CRF")
PRESET = os.getenv("PRESET")


# Handle interruption with Ctrl+C
def signal_handler(sig, frame):
    print(
        "\n\nInterruption detected. "
        "Exiting the program safely..."
    )
    sys.exit(0)


# Mount SMB folder as read-only
def mount_smb_readonly(smb_path, username, password, read_only=True):
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    # Create a temporary credentials file
    credentials_file = tempfile.mktemp(suffix='.credentials')
    with open(credentials_file, 'w') as f:
        f.write(f"username={username}\n")
        f.write(f"password={password}\n")

    # Ensure the file is readable only by the user
    os.chmod(credentials_file, 0o600)

    if read_only:
        mount_cmd = (
            f"mount -t cifs {shlex.quote(smb_path)} {shlex.quote(temp_dir)} "
            f"-o credentials={shlex.quote(credentials_file)},ro"
        )
    else:
        mount_cmd = (
            f"mount -t cifs {shlex.quote(smb_path)} {shlex.quote(temp_dir)} "
            f"-o credentials={shlex.quote(credentials_file)}"
        )

    try:
        subprocess.run(mount_cmd, shell=True, check=True)
        print(f"Folder {smb_path} mounted at {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"Error mounting {smb_path}: {e}")
        return None
    finally:
        # Cleanup: remove the credentials file
        if os.path.exists(credentials_file):
            os.remove(credentials_file)


# Unmount and delete temporary folder
def unmount_and_cleanup(temp_dir):
    try:
        subprocess.run(
            f"umount {shlex.quote(temp_dir)}", shell=True, check=True
        )
        shutil.rmtree(temp_dir)  # Remove the temporary directory
        print(f"Folder {temp_dir} unmounted and deleted")
    except subprocess.CalledProcessError as e:
        print(f"Error unmounting {temp_dir}: {e}")


# Run a command and capture the output
def run_command(command):
    try:
        result = subprocess.run(command, shell=True,
                                capture_output=True,
                                text=True,
                                check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\nOutput: {e.stderr}")
        return None


# Get the duration of a video using ffprobe
def get_video_duration(file_path):
    command = (
        "ffprobe -v error -show_entries format=duration "
        f"-of default=noprint_wrappers=1:nokey=1 {shlex.quote(file_path)}"
    )
    duration_str = run_command(command)
    if duration_str:
        return float(duration_str)
    return None


# Compress a file using ffmpeg
def compress_video(input_file, output_file, duration):
    # Create a temporary file to receive ffmpeg progress
    progress_file = tempfile.mktemp(suffix=".progress")

    # ffmpeg command with progress option
    ffmpeg_command = (
        f"ffmpeg -i {shlex.quote(input_file)} -map 0 -c:v libx264 -crf {CRF} "
        f"-preset {PRESET} -c:a copy -c:s copy "
        f"-progress {shlex.quote(progress_file)} -stats {shlex.quote(output_file)}"
    )

    # Start ffmpeg in a separate thread
    def run_ffmpeg():
        run_command(ffmpeg_command)

    ffmpeg_thread = threading.Thread(target=run_ffmpeg)
    ffmpeg_thread.start()

    # Progress bar
    with tqdm(total=duration, unit="s", desc="Progress", ncols=80) as pbar:
        while ffmpeg_thread.is_alive():
            try:
                with open(progress_file, "r") as f:
                    lines = f.readlines()

                # Search for the line that indicates elapsed time
                for line in lines:
                    if "out_time_ms" in line:
                        # Extract elapsed time in milliseconds
                        elapsed_time = int(
                            line.split("=")[1].strip()
                        ) / 1000000
                        pbar.n = elapsed_time  # Update progress bar
                        pbar.refresh()  # Refresh the bar

                time.sleep(1)
            except FileNotFoundError:
                continue

    ffmpeg_thread.join()

    # Remove the temporary progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)


# Extract season and chapter from the filename
def extract_season_and_chapter(file_name):
    match = re.search(r"(\d+x)(\d+)", file_name)
    if match:
        season = match.group(1)
        chapter = match.group(2)
        return season, chapter
    return None, None


# Process a chapter of a series
def process_chapter(file_path,
                    series_name,
                    series_season,
                    total_chapters,
                    output_dir):
    file_name = os.path.basename(file_path)
    season, chapter = extract_season_and_chapter(file_name)

    if season and chapter:
        output_file = os.path.join(
            output_dir, series_name, series_season, file_name
        )
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(output_file):
            print(
                f"\nThe file '{output_file}' has already "
                "been compressed; skipping."
            )
            return

        print(
            f"\nCompressing chapter {chapter} of the {total_chapters} "
            f"in season {series_season} of the series '{series_name}'."
        )

        # Compress the video with a progress bar
        compress_video(file_path, output_file, get_video_duration(file_path))

        print(
            f"Compression of chapter '{season}{chapter}' "
            f"from the series '{series_name}' completed."
        )


# Process series
def process_series(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                path_parts = Path(file_path).parts
                if len(path_parts) >= 3:
                    series_name = path_parts[-3]  # Series name
                    series_season = path_parts[-2]  # Season
                    total_chapters = len(
                        [f for f in os.listdir(
                            os.path.join(input_dir, series_name, series_season)
                        ) if f.endswith(".mkv")]
                    )

                    process_chapter(file_path,
                                    series_name,
                                    series_season,
                                    total_chapters,
                                    output_dir)

    print("\nAll series have been fully compressed.")


# Process movies
def process_movies(input_dir, output_dir_base):
    for dirpath, dirnames, _ in os.walk(input_dir):
        for movie_dir in dirnames:
            movie_path = os.path.join(dirpath, movie_dir)
            movie_name = os.path.basename(movie_path)

            movie_file = next(
                (f for f in os.listdir(movie_path) if f.endswith('.mkv')),
                None)
            if not movie_file:
                print(f"No .mkv file found in '{movie_path}'. Skipping.")
                continue

            input_file = os.path.join(movie_path, movie_file)
            output_dir = os.path.join(output_dir_base, movie_name)
            output_file = os.path.join(output_dir, f"{movie_name}.mkv")

            os.makedirs(output_dir, exist_ok=True)

            if os.path.exists(output_file):
                print(
                    f"The movie '{movie_name}' has already been compressed. "
                    "Skipping."
                )
                continue

            print(f"Compressing the movie '{movie_name}'...")

            # Compress the movie with a progress bar
            compress_video(
                input_file, output_file, get_video_duration(input_file)
            )

            print(f"\nCompression of the movie '{movie_name}' completed.")


# Main function to decide what to compress based on the argument
def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python media_compressor.py [series|movies]")
            sys.exit(1)

        task = sys.argv[1].lower()

        # Register the SIGINT (Ctrl+C) signal handler
        signal.signal(signal.SIGINT, signal_handler)

        if task == "series":
            print("Processing series...")
            input_dir = mount_smb_readonly(
                SMB_INPUT_SERIES, SMB_USERNAME, SMB_PASSWORD, True
            )
            output_dir = mount_smb_readonly(
                SMB_OUTPUT_SERIES, SMB_USERNAME, SMB_PASSWORD, False
            )
            if input_dir and output_dir:
                process_series(input_dir, output_dir)
                unmount_and_cleanup(input_dir)
                unmount_and_cleanup(output_dir)
        elif task == "movies":
            print("Processing movies...")
            input_dir = mount_smb_readonly(
                SMB_INPUT_MOVIES, SMB_USERNAME, SMB_PASSWORD, True
            )
            output_dir = mount_smb_readonly(
                SMB_OUTPUT_MOVIES, SMB_USERNAME, SMB_PASSWORD, False
            )
            if input_dir and output_dir:
                process_movies(input_dir, output_dir)
                unmount_and_cleanup(input_dir)
                unmount_and_cleanup(output_dir)
        else:
            print("Invalid argument. Use 'series' or 'movies'.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nThe process was interrupted by the user. Exiting...")


# Execute the program
if __name__ == "__main__":
    main()
