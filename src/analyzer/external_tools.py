# src/analyzer/external_tools.py

import subprocess
import json
import os
import time


def run_jfr_profiler(java_app_path: str, architecture: str, duration: int = 60) -> dict:
    """
    Run the Java application with Java Flight Recorder enabled.
    This function assumes you have a command-line tool to convert the .jfr file to JSON.

    :param java_app_path: Path to the Java application jar.
    :param architecture: The target architecture (used for logging or simulation setup).
    :param duration: Duration in seconds for which to record.
    :return: A dict of performance metrics parsed from the profiler output.
    """
    # Generate a unique filename for the recording
    recording_file = f"recording_{architecture}.jfr"

    # Construct the command to run the Java app with JFR enabled.
    # For example, the JVM flag '-XX:StartFlightRecording' starts a recording.
    java_cmd = [
        "java",
        f"-XX:StartFlightRecording=duration={duration}s,filename={recording_file}",
        "-jar",
        java_app_path
    ]

    try:
        # Run the Java application (this call may block until the recording completes)
        subprocess.run(java_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during JFR profiling for {architecture}: {e}")
        return {}

    # Give some time for the file to be written (or check for file existence)
    time.sleep(2)

    # Convert the JFR recording to JSON.
    # This assumes you have a tool (e.g. jfr tool available in your JDK)
    # For example: `jfr print --json recording_file`
    json_cmd = ["jfr", "print", "--json", recording_file]
    try:
        result = subprocess.run(json_cmd, capture_output=True, text=True, check=True)
        metrics = json.loads(result.stdout)
    except Exception as e:
        print(f"Error converting JFR recording to JSON: {e}")
        metrics = {}

    # Optionally, delete the recording file after processing.
    if os.path.exists(recording_file):
        os.remove(recording_file)

    return metrics
