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
import argparse

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
    global interrupted
    interrupted = True
    print("\n\nInterruption detected. Stopping compression safely...")
    # FFmpeg will be stopped gracefully with loglevel quiet
    return


# Mount SMB folder
def mount_smb(smb_path, username, password, read_only=True):
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
            f"-o credentials={shlex.quote(credentials_file)},iocharset=utf8,ro"
        )
    else:
        mount_cmd = (
            f"mount -t cifs {shlex.quote(smb_path)} {shlex.quote(temp_dir)} "
            f"-o credentials={shlex.quote(credentials_file)},iocharset=utf8"
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


# Adjust video dimensions to be divisible by 2
def adjust_video_dimensions(input_file):
    command = (
        f"ffprobe -v error -select_streams v:0 "
        f"-show_entries stream=width,height "
        f"-of csv=p=0:s=x {shlex.quote(input_file)}"
    )
    dimensions = run_command(command)

    # Handling empty or incorrect ffprobe output
    if not dimensions:
        print(
            "Warning: Could not retrieve dimensions "
            f"for file '{input_file}'."
        )
        return None, None

    # Remove any extra characters, such as a trailing "x"
    dimensions = dimensions.strip().rstrip('x')

    try:
        width, height = map(int, dimensions.split('x'))
        new_width = width if width % 2 == 0 else width - 1
        new_height = height if height % 2 == 0 else height - 1
        return new_width, new_height
    except ValueError as e:
        print(f"Error parsing dimensions for file '{input_file}': {e}")
        return None, None


# Compress a file using ffmpeg
def compress_video(input_file, output_file, duration):
    # Create a temporary file to receive ffmpeg progress
    progress_file = tempfile.mktemp(suffix=".progress")
    width, height = adjust_video_dimensions(input_file)
    scale_filter = f"-vf scale={width}:{height}" if width and height else ""

    # ffmpeg command with progress option
    ffmpeg_command = (
        f"ffmpeg -i {shlex.quote(input_file)} -map 0 -c:v libx264 -crf {CRF} "
        f"-preset {PRESET} -c:a copy -c:s copy -probesize 50M "
        f"-analyzeduration 100M {scale_filter} "
        f"-progress {shlex.quote(progress_file)} "
        f"-stats {shlex.quote(output_file)}"
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
def extract_season_and_chapters(file_name):
    match = re.search(r"(\d+x)([\d-]+)", file_name)
    if match:
        season = match.group(1)
        chapters_range = match.group(2)

        # Parse chapters if they are in a range like 01-02-03 or 04-05
        chapter_list = []
        for chapter_part in chapters_range.split('-'):
            chapter_list.append(chapter_part.zfill(2))  # Ensure two digits

        return season, chapter_list
    return None, []


# Process a chapter of a series
def process_chapter(file_path, series_name, series_season,
                    total_chapters, output_dir):
    file_name = os.path.basename(file_path)
    season, chapter_list = extract_season_and_chapters(file_name)

    if season and chapter_list:
        # Use first chapter for output file name
        output_file = os.path.join(
            output_dir, series_name, series_season, file_name
        )
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(output_file):
            print(
                f"\nThe file '{output_file}' has already "
                "been compressed; skipping.")
            return

        # Indicate whether to use "chapter" or "chapters"
        chapters = ', '.join(chapter_list)
        chapter_word = "chapter" if len(chapter_list) == 1 else "chapters"
        total_chapter_word = "chapter" if total_chapters == 1 else "chapters"

        print(
            f"\nCompressing {chapter_word} {chapters} "
            f"of season {series_season} ({total_chapters} "
            f"{total_chapter_word} total) in series '{series_name}'.")

        # Compress the video with progress bar
        try:
            compress_video(
                file_path, output_file, get_video_duration(file_path))
            print(
                f"\nCompression of {chapter_word} '{season}{chapters}' "
                f"from the series '{series_name}' completed.")
        except Exception as e:
            print(
                f"\nError compressing {chapter_word} "
                f"'{season}{chapters}': {e}")


# Process series
def process_series(input_dir, output_dir, name=None, list_file=None):
    series_to_process = []

    # Si se pasa una lista, cargarla
    if list_file:
        try:
            with open(list_file, 'r') as f:
                series_to_process = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: Could not find the file '{list_file}'.")
            sys.exit(1)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                path_parts = Path(file_path).parts

                if len(path_parts) >= 3:
                    series_name = path_parts[-3]  # Series name
                    series_season = path_parts[-2]  # Season

                    # Check if this series should be processed
                    if name and series_name != name:
                        continue
                    if (
                        series_to_process and
                        series_name not in series_to_process
                    ):
                        continue

                    # Count real number of chapters
                    total_chapters = 0
                    season_dir = os.path.join(
                        input_dir, series_name, series_season
                    )

                    for f in os.listdir(season_dir):
                        if f.endswith(".mkv"):
                            _, chapters = extract_season_and_chapters(f)
                            total_chapters += len(chapters)

                    process_chapter(file_path,
                                    series_name,
                                    series_season,
                                    total_chapters,
                                    output_dir)

    print("\nAll series have been fully compressed.\n")


# Process movies
def process_movies(input_dir, output_dir_base, name=None, list_file=None):
    movies_to_process = []

    # If a list is passed, load it
    if list_file:
        try:
            with open(list_file, 'r') as f:
                movies_to_process = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: Could not find the file '{list_file}'.")
            sys.exit(1)

    for dirpath, dirnames, _ in os.walk(input_dir):
        for movie_dir in dirnames:
            movie_name = os.path.basename(movie_dir)

            # Check if this movie should be processed
            if name and movie_name != name:
                continue
            if movies_to_process and movie_name not in map(movies_to_process):
                continue

            movie_path = os.path.join(dirpath, movie_dir)
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
                    f"\nThe movie '{movie_name}' has already "
                    "been compressed. Skipping."
                )
                continue

            print(f"\nCompressing the movie '{movie_name}'...")

            # Compress the movie with a progress bar
            try:
                compress_video(
                    input_file, output_file, get_video_duration(input_file)
                )
                print(f"\nCompression of the movie '{movie_name}' completed.")
            except Exception as e:
                print(f"\nError compressing movie '{movie_name}': {e}")

    print("\nAll movies have been fully compressed.\n")


# Main function to decide what to compress based on the argument
def main():
    try:
        parser = argparse.ArgumentParser(
            description=(
                "Compress series and movies from SMB shares using "
                "FFmpeg."
            )
        )
        parser.add_argument("type", choices=["series", "movies"],
                            help="Choose between 'series' or 'movies'")
        parser.add_argument("--name",
                            help="Specify the name of the series/movie")
        parser.add_argument("--list",
                            help="Specify a list of series/movies")
        args = parser.parse_args()

        # Check if both --name and --list are specified
        if args.name and args.list:
            print(
                "Error: You cannot specify both "
                "--name and --list at the same time."
            )
            sys.exit(1)

        # Register the SIGINT (Ctrl+C) signal handler
        signal.signal(signal.SIGINT, signal_handler)

        if args.type == "series":
            print("Processing series...\n")
            input_dir = mount_smb(
                SMB_INPUT_SERIES, SMB_USERNAME, SMB_PASSWORD, True
            )
            output_dir = mount_smb(
                SMB_OUTPUT_SERIES, SMB_USERNAME, SMB_PASSWORD, False
            )
            if input_dir and output_dir:
                process_series(
                    input_dir, output_dir, name=args.name, list_file=args.list
                )
                unmount_and_cleanup(input_dir)
                unmount_and_cleanup(output_dir)
        elif args.type == "movies":
            print("Processing movies...\n")
            input_dir = mount_smb(
                SMB_INPUT_MOVIES, SMB_USERNAME, SMB_PASSWORD, True
            )
            output_dir = mount_smb(
                SMB_OUTPUT_MOVIES, SMB_USERNAME, SMB_PASSWORD, False
            )
            if input_dir and output_dir:
                process_movies(
                    input_dir, output_dir, name=args.name, list_file=args.list
                )
                unmount_and_cleanup(input_dir)
                unmount_and_cleanup(output_dir)
    except KeyboardInterrupt:
        print("\n\nThe process was interrupted by the user. Exiting...")


# Execute the program
if __name__ == "__main__":
    main()
