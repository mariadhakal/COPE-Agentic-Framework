import os
import subprocess
import tempfile
import argparse
import time
import json
from pathlib import Path


class JavaProfiler:
    def __init__(self, output_dir=None):
        """Initialize the Java profiler with an optional output directory."""
        self.output_dir = output_dir or os.path.join(os.getcwd(), "jfr_profiles")
        os.makedirs(self.output_dir, exist_ok=True)

    def profile_code(self, java_code, class_name, duration_seconds=10, recording_name=None):
        """Profile the provided Java code using JFR.

        Args:
            java_code (str): The Java source code to profile
            class_name (str): The main class name in the code
            duration_seconds (int): How long to record JFR data
            recording_name (str): Optional name for the recording files

        Returns:
            dict: Results including paths to JFR file and basic metrics
        """
        timestamp = int(time.time())
        recording_name = recording_name or f"{class_name}_{timestamp}"
        temp_dir = tempfile.mkdtemp()

        # Create Java file
        java_file_path = os.path.join(temp_dir, f"{class_name}.java")
        with open(java_file_path, "w") as f:
            f.write(java_code)

        # Compile the Java file
        try:
            subprocess.run(
                ["javac", java_file_path],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stage": "compilation",
                "error": e.stderr
            }

        # Run with JFR enabled
        jfr_file = os.path.join(self.output_dir, f"{recording_name}.jfr")

        try:
            # Start the Java process with JFR recording
            jfr_cmd = [
                "java",
                f"-XX:StartFlightRecording=name={recording_name},duration={duration_seconds}s,filename={jfr_file},settings=profile",
                "-cp", temp_dir,
                class_name
            ]

            process = subprocess.run(
                jfr_cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Allow some time for JFR file to be written completely
            time.sleep(1)

            # Run JFR print to get summary data
            if os.path.exists(jfr_file):
                jfr_summary = self._analyze_jfr(jfr_file)

                return {
                    "success": True,
                    "jfr_file": jfr_file,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "metrics": jfr_summary
                }
            else:
                return {
                    "success": False,
                    "stage": "jfr_recording",
                    "error": "JFR file was not created"
                }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stage": "execution",
                "error": e.stderr
            }

    def _analyze_jfr(self, jfr_file):
        """Extract basic metrics from JFR file using jfr tool."""
        try:
            # Use JFR print to get summary information
            jfr_summary_cmd = [
                "jfr", "summary", jfr_file
            ]

            summary_process = subprocess.run(
                jfr_summary_cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Use JFR metadata to get event counts
            jfr_metadata_cmd = [
                "jfr", "metadata", jfr_file
            ]

            metadata_process = subprocess.run(
                jfr_metadata_cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Extract CPU and memory metrics using jfr print (simplified)
            metrics = {
                "summary": summary_process.stdout,
                "metadata": metadata_process.stdout,
                "cpu": self._extract_cpu_metrics(jfr_file),
                "memory": self._extract_memory_metrics(jfr_file),
                "file_size_bytes": os.path.getsize(jfr_file)
            }

            return metrics

        except subprocess.CalledProcessError as e:
            return {
                "error": "Failed to analyze JFR file",
                "details": e.stderr
            }

    def _extract_cpu_metrics(self, jfr_file):
        """Extract CPU metrics from JFR file."""
        try:
            # Use jfr print to extract CPU-related events
            cpu_cmd = [
                "jfr", "print",
                "--events", "jdk.CPULoad,jdk.ThreadCPULoad",
                jfr_file
            ]

            cpu_process = subprocess.run(
                cpu_cmd,
                check=True,
                capture_output=True,
                text=True
            )

            return cpu_process.stdout
        except:
            return "CPU metrics extraction failed"

    def _extract_memory_metrics(self, jfr_file):
        """Extract memory metrics from JFR file."""
        try:
            # Use jfr print to extract memory-related events
            memory_cmd = [
                "jfr", "print",
                "--events", "jdk.GarbageCollection,jdk.ObjectAllocationInNewTLAB,jdk.ObjectAllocationOutsideTLAB",
                jfr_file
            ]

            memory_process = subprocess.run(
                memory_cmd,
                check=True,
                capture_output=True,
                text=True
            )

            return memory_process.stdout
        except:
            return "Memory metrics extraction failed"

    def view_with_jmc(self, jfr_file):
        """Open the JFR file with Java Mission Control."""
        try:
            subprocess.Popen(["jmc", "-open", jfr_file])
            return True
        except Exception as e:
            print(f"Failed to open JMC: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Profile Java code with JFR and JMC")
    parser.add_argument("--file", help="Java source file to profile")
    parser.add_argument("--code", help="Java code as a string")
    parser.add_argument("--class-name", help="Main class name", required=True)
    parser.add_argument("--duration", type=int, default=10, help="Recording duration in seconds")
    parser.add_argument("--output-dir", help="Directory to store JFR files")
    parser.add_argument("--open-jmc", action="store_true", help="Open JMC after recording")
    args = parser.parse_args()

    profiler = JavaProfiler(output_dir=args.output_dir)

    # Get code from file or command line
    java_code = ""
    if args.file:
        with open(args.file, "r") as f:
            java_code = f.read()
    elif args.code:
        java_code = args.code
    else:
        print("Error: Must provide either --file or --code")
        return

    # Run profiling
    print(f"Profiling Java code with class {args.class_name} for {args.duration} seconds...")
    results = profiler.profile_code(
        java_code=java_code,
        class_name=args.class_name,
        duration_seconds=args.duration
    )

    # Print results
    if results["success"]:
        print(f"Profiling completed successfully!")
        print(f"JFR file: {results['jfr_file']}")
        print("\nProgram output:")
        print(results["stdout"])

        print("\nBasic metrics summary:")
        print(results["metrics"]["summary"][:500] + "..." if len(results["metrics"]["summary"]) > 500 else
              results["metrics"]["summary"])

        # Save full results to JSON
        results_file = os.path.splitext(results["jfr_file"])[0] + "_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to: {results_file}")

        # Open with JMC if requested
        if args.open_jmc:
            print("\nLaunching Java Mission Control...")
            profiler.view_with_jmc(results["jfr_file"])
    else:
        print(f"Profiling failed at stage: {results['stage']}")
        print(f"Error: {results['error']}")


if __name__ == "__main__":
    main()