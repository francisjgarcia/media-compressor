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

# Flag to track if an interruption has occurred
interrupted = False


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
        print(f"Folder {temp_dir} unmounted and deleted\n")
    except subprocess.CalledProcessError as e:
        print(f"Error unmounting {temp_dir}: {e}\n")


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


# Get the bitrate of a video using ffprobe
def get_video_bitrate(file_path):
    command = (
        f"ffprobe -v error -show_entries format=bit_rate -of "
        f"default=noprint_wrappers=1:nokey=1 {shlex.quote(file_path)}"
    )
    bitrate_str = run_command(command)
    if bitrate_str:
        try:
            bitrate = int(bitrate_str) / 1000000
            return bitrate
        except ValueError:
            print(
                f"Warning: Invalid bitrate value '{bitrate_str}' "
                f"for file '{file_path}'.")
            return None
    return None


# Get the duration of a video using ffprobe
def get_video_duration(file_path):
    command = (
        "ffprobe -v error -show_entries format=duration "
        f"-of default=noprint_wrappers=1:nokey=1 {shlex.quote(file_path)}"
    )
    duration_str = run_command(command)
    if duration_str:
        try:
            duration = float(duration_str)
            return duration
        except ValueError:
            print(
                f"Warning: Invalid duration value '{duration_str}' "
                f"for file '{file_path}'.")
            return None
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


def kill_ffmpeg_processes():
    """Terminate all ffmpeg processes."""
    try:
        # Get the PIDs of all ffmpeg processes
        pids = subprocess.check_output(
            ['pgrep', 'ffmpeg']
        ).decode('utf-8').strip().split('\n')

        for pid in pids:
            print(f"Terminating ffmpeg process with PID: {pid}")
            subprocess.run(['kill', pid])  # Terminate the process

        time.sleep(2)  # Wait a bit to ensure processes have terminated
    except subprocess.CalledProcessError:
        print("No ffmpeg processes found.")


# Compress a file using ffmpeg
def compress_video(input_file, output_file, duration, compress_bitrate=None):
    global interrupted

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
        f"-stats {shlex.quote(output_file)} "
    )

    # Check if the compress_bitrate is specified
    if compress_bitrate is not None:
        # Convert the bitrate to kbps
        bitrate_kbps = compress_bitrate * 1000
        # Add the bitrate to the ffmpeg command
        ffmpeg_command += f"-b:v {bitrate_kbps}k"

    process = None

    # Start ffmpeg in a separate thread to allow interruption
    def run_ffmpeg():
        nonlocal process
        process = subprocess.Popen(
            ffmpeg_command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        process.communicate()  # Wait for process to finish

    ffmpeg_thread = threading.Thread(target=run_ffmpeg)
    ffmpeg_thread.start()

    # Progress bar
    with tqdm(total=duration, unit="s", desc="Progress", ncols=80) as pbar:
        while ffmpeg_thread.is_alive():
            if interrupted:
                print("\nStopping FFmpeg process...")
                if process:
                    process.terminate()  # Kill the FFmpeg process
                break  # Exit the loop and end the thread

            try:
                with open(progress_file, "r") as f:
                    lines = f.readlines()

                # Search for the line that indicates elapsed time
                for line in lines:
                    if "out_time_ms" in line:
                        # Extract elapsed time in milliseconds
                        try:
                            elapsed_time = line.split("=")[1].strip()
                            # Check if the elapsed_time is a valid number
                            if elapsed_time.isdigit():
                                elapsed_time = int(elapsed_time) / 1000000
                                pbar.n = elapsed_time  # Update progress bar
                                pbar.refresh()  # Refresh the bar
                            else:
                                continue
                        except (IndexError, ValueError):
                            continue

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


# Check if a directory is empty
def is_empty(directory):
    return not any(os.scandir(directory))


# Process a chapter of a series
def process_chapter(file_path, series_name, series_season,
                    total_chapters, output_dir, show_bitrate=None,
                    filter_bitrate=None, compress_bitrate=None):
    global interrupted
    file_name = os.path.basename(file_path)
    season, chapter_list = extract_season_and_chapters(file_name)

    if show_bitrate:
        print(
            f"File '{file_name}' has a bitrate of "
            f"{get_video_bitrate(file_path)} Mbps.")
        return

    # Get the video bitrate and compare it with the specified bitrate
    if filter_bitrate:
        video_bitrate = get_video_bitrate(file_path)
        if video_bitrate and video_bitrate < filter_bitrate:
            print(
                f"\nSkipping {file_name} (bitrate {video_bitrate} Mbps "
                f", lower than {filter_bitrate} Mbps).")
            return
        print(
            f"\nFile '{file_name}' has a bitrate of "
            f"{video_bitrate} Mbps, processing...")

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
                "been compressed; skipping."
            )
            return

        # Indicate whether to use "chapter" or "chapters"
        chapters = ', '.join(chapter_list)
        chapter_word = "chapter" if len(chapter_list) == 1 else "chapters"
        total_chapter_word = "chapter" if total_chapters == 1 else "chapters"

        if compress_bitrate:
            print(
                f"Compressing {chapter_word} {chapters} "
                f"of season {series_season} ({total_chapters} "
                f"{total_chapter_word} total) in series '{series_name}' "
                f"with a bitrate of {compress_bitrate} Mbps."
            )
        else:
            print(
                f"\nCompressing {chapter_word} {chapters} "
                f"of season {series_season} ({total_chapters} "
                f"{total_chapter_word} total) in series '{series_name}'."
            )

        # Get original file size
        original_size = os.path.getsize(file_path)

        # Get video duration
        duration = get_video_duration(file_path)

        if duration is None:
            print(
                f"Skipping {chapter_word} '{season}{chapters}' "
                "due to ffprobe failure."
            )
            return

        try:
            compress_video(file_path, output_file, duration, compress_bitrate)

            if interrupted:
                print(
                    f"\nCompression interrupted for file '{file_name}', "
                    "deleting incomplete output file.\n"
                )
                if os.path.exists(output_file):
                    os.remove(output_file)

                # Check if the season directory is empty to delete
                if is_empty(output_dir):
                    print(f"Deleting empty directory: {output_dir}")
                    os.rmdir(output_dir)

                    # Check if the series directory is empty to delete
                    series_dir = os.path.dirname(os.path.dirname(output_dir))

                    if is_empty(os.path.join(series_dir, series_name)):
                        print(
                            "Deleting empty series directory: "
                            f"{os.path.join(series_dir, series_name)}"
                        )
                        os.rmdir(os.path.join(series_dir, series_name))
                return

            new_size = os.path.getsize(output_file)

            # Calculate reduction
            reduction = (
                ((original_size - new_size) / original_size) * 100
                if original_size > 0 else 0
            )

            original_size_display = (
                f"{original_size / (1024 * 1024):.2f} MB"
                if original_size < 1024 * (1024 * 1024)
                else f"{original_size / (1024 * 1024 * 1024):.2f} GB"
            )

            new_size_display = (
                f"{new_size / (1024 * 1024):.2f} MB"
                if new_size < 1024 * (1024 * 1024)
                else f"{new_size / (1024 * 1024 * 1024):.2f} GB"
            )

            print(
                f"\nCompression of {chapter_word} '{season}{chapters}' "
                f"from the series '{series_name}' completed. "
                f"Original size: {original_size_display}, "
                f"New size: {new_size_display}, "
                f"Reduction: {reduction:.2f}%."
            )

        except Exception as e:
            print(
                f"\nError compressing {chapter_word} "
                f"'{season}{chapters}': {e}"
            )
            kill_ffmpeg_processes()
            if os.path.exists(output_file):
                os.remove(output_file)


# Process series
def process_series(input_dir, output_dir, name=None, list_file=None,
                   show_bitrate=None, filter_bitrate=None,
                   compress_bitrate=None):
    global interrupted
    series_to_process = []

    # If a list is passed, load it
    if list_file:
        try:
            with open(list_file, 'r') as f:
                series_to_process = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: Could not find the file '{list_file}'.")
            sys.exit(1)

    for root, _, files in os.walk(input_dir):
        if interrupted:
            break  # Exit immediately if interrupted
        for file in files:
            if interrupted:
                break  # Exit immediately if interrupted
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                path_parts = Path(file_path).parts

                if len(path_parts) >= 3:
                    series_name = path_parts[-3]  # Series name
                    series_season = path_parts[-2]  # Season
                    total_chapters = len(files)

                    if name and name.lower() in series_name.lower():
                        process_chapter(
                            file_path, series_name, series_season,
                            total_chapters, output_dir,
                            show_bitrate=show_bitrate,
                            filter_bitrate=filter_bitrate,
                            compress_bitrate=compress_bitrate
                        )

                    elif not name and not series_to_process:
                        process_chapter(
                            file_path, series_name, series_season,
                            total_chapters, output_dir,
                            show_bitrate=show_bitrate,
                            filter_bitrate=filter_bitrate,
                            compress_bitrate=compress_bitrate
                        )

                    elif not name and series_to_process:
                        if any(
                            series_name.lower() in s.lower()
                            for s in series_to_process
                        ):
                            process_chapter(
                                file_path, series_name, series_season,
                                total_chapters, output_dir,
                                show_bitrate=show_bitrate,
                                filter_bitrate=filter_bitrate,
                                compress_bitrate=compress_bitrate
                            )

    print("\nAll series have been fully compressed.\n")


# Process movies
def process_movies(input_dir, output_dir, name=None, list_file=None,
                   show_bitrate=None, filter_bitrate=None,
                   compress_bitrate=None):
    global interrupted
    movies_to_process = []

    # Load movies from list if provided
    if list_file:
        try:
            with open(list_file, 'r') as f:
                movies_to_process = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: Could not find file '{list_file}'.")
            sys.exit(1)

    # Iterate over the movie directory
    for root, _, files in os.walk(input_dir):
        if interrupted:
            break  # Exit immediately if interrupted
        for file in files:
            if interrupted:
                break  # Exit immediately if interrupted
            if file.endswith(".mkv") or file.endswith(".mp4"):
                file_path = os.path.join(root, file)
                movie_name = Path(file_path).stem

                # Check if the name matches the provided one
                if name and name.lower() not in movie_name.lower():
                    continue

                # Create the output path for the compressed movie
                output_file = os.path.join(output_dir, f"{movie_name}.mkv")
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                # Skip already compressed movies
                if os.path.exists(output_file):
                    print(
                        f"\nMovie '{output_file}' has already "
                        "been compressed. Skipping."
                    )
                    continue

                # Check if this movie is in the list of movies to process
                if (movies_to_process and
                        movie_name.lower() not in
                        map(str.lower, movies_to_process)):
                    continue

                if show_bitrate:
                    print(
                        f"File '{movie_name}' has a bitrate of "
                        f"{get_video_bitrate(file_path)} Mbps.")
                    break

                # Check if the bitrate is lower than the specified bitrate
                if filter_bitrate:
                    video_bitrate = get_video_bitrate(file_path)
                    if video_bitrate and video_bitrate < filter_bitrate:
                        print(
                            f"\nSkipping {movie_name} (bitrate "
                            f"{video_bitrate} Mbps, lower than "
                            f"{filter_bitrate} Mbps).")
                        break
                    print(
                        f"\nFile '{movie_name}' has a bitrate of "
                        f"{video_bitrate} Mbps, processing...")

                if compress_bitrate:
                    print(
                        f"Compressing movie '{movie_name}' with a bitrate of "
                        f"{compress_bitrate} Mbps."
                    )
                else:
                    print(f"\nCompressing movie: '{movie_name}'")

                # Get the original file size
                original_size = os.path.getsize(file_path)

                try:
                    # Compress the video with a progress bar
                    compress_video(
                        file_path, output_file, get_video_duration(file_path),
                        compress_bitrate
                    )

                    # If interrupted during compression remove the output file
                    if interrupted:
                        print(
                            "\nCompression interrupted for movie "
                            f"'{movie_name}', deleting incomplete "
                            "output file. \n"
                        )
                        if os.path.exists(output_file):
                            os.remove(output_file)
                        return

                    # Get the size of the compressed file
                    new_size = os.path.getsize(output_file)

                    # Calculate the size reduction
                    reduction = (
                        ((original_size - new_size) / original_size) * 100
                        if original_size > 0 else 0
                    )

                    # Display original and new sizes in a readable format
                    original_size_display = (
                        f"{original_size / (1024 * 1024):.2f} MB"
                        if original_size < 1024 * (1024 * 1024)
                        else f"{original_size / (1024 * 1024 * 1024):.2f} GB"
                    )

                    new_size_display = (
                        f"{new_size / (1024 * 1024):.2f} MB"
                        if new_size < 1024 * (1024 * 1024)
                        else f"{new_size / (1024 * 1024 * 1024):.2f} GB"
                    )

                    print(
                        f"\nCompression of movie '{movie_name}' completed. "
                        f"\nOriginal size: {original_size_display}, "
                        f"New size: {new_size_display}, "
                        f"Reduction: {reduction:.2f}%."
                    )
                except Exception as e:
                    # Handle errors and delete the output file
                    print(f"\nError compressing movie '{movie_name}': {e}")
                    kill_ffmpeg_processes()
                    if os.path.exists(output_file):
                        os.remove(output_file)

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
        parser.add_argument("--show-bitrate", action="store_true",
                            help="Show the bitrate of the video files.")
        parser.add_argument("--filter-bitrate",
                            type=int,
                            help="Specify a minimum bitrate (in Mbps) "
                            "to filter files.")
        parser.add_argument("--compress-bitrate",
                            type=int,
                            help="If set, compress files with bitrate higher "
                            "than --filter-bitrate to the specified bitrate.")
        args = parser.parse_args()

        # Check if both --name and --list are specified
        if args.name and args.list:
            print(
                "Error: You cannot specify both "
                "--name and --list at the same time."
            )
            sys.exit(1)

        # Check if --compress-bitrate is specified without --filter-bitrate
        if args.filter_bitrate and not args.compress_bitrate:
            print(
                "Error: --compress-bitrate must be "
                "specified when --filter-bitrate is used.")
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
                    input_dir, output_dir, name=args.name,
                    list_file=args.list, show_bitrate=args.show_bitrate,
                    filter_bitrate=args.filter_bitrate,
                    compress_bitrate=args.compress_bitrate
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
                    input_dir, output_dir, name=args.name,
                    list_file=args.list, show_bitrate=args.show_bitrate,
                    filter_bitrate=args.filter_bitrate,
                    compress_bitrate=args.compress_bitrate
                )
                unmount_and_cleanup(input_dir)
                unmount_and_cleanup(output_dir)
    except KeyboardInterrupt:
        print("\n\nThe process was interrupted by the user. Exiting...")


# Execute the program
if __name__ == "__main__":
    main()
