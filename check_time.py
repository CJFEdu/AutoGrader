#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
import time
import datetime
from check_submissions import SubmissionChecker
from config import Config

class TimeChecker(SubmissionChecker):
    """
    A child class of SubmissionChecker that focuses on checking execution time.
    """
    def __init__(self):
        super().__init__()
        self.TEST_FILE_NAME = "TestTime"
        Config.CLEAN_START = False
        self.results_path = os.path.join(self.script_dir, "time_results")
        self.full_output_path = os.path.join(self.script_dir, "time_full_output")
        self.csv_results_file = "time_results.csv"
        self.MAIN_TEST_FOLDER = "time_test"
        print("Initializing Time Checker...")
        
    def run(self):
        """
        Run the time checker.
        """
        print("Running time checks...")
        
        # Create time tracker file if it doesn't exist
        tracker_file = os.path.join(self.script_dir, "time_tracker.txt")
        
        # Record start time
        start_time = time.time()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append start time to tracker file
        with open(tracker_file, 'a') as f:
            f.write(f"\n=== Time Check Started: {timestamp} ===\n")
        
        # Run the actual processing
        self.process_csv()
        self.print_results()
        
        # Record end time and calculate duration
        end_time = time.time()
        end_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = end_time - start_time
        
        # Format duration as hours:minutes:seconds
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
        # Append end time and duration to tracker file
        with open(tracker_file, 'a') as f:
            f.write(f"=== Time Check Completed: {end_timestamp} ===\n")
            f.write(f"=== Total Duration: {duration_formatted} ({duration:.2f} seconds) ===\n")
        
        print(f"Time checks completed. Total duration: {duration_formatted}")

    def print_results(self):
        """
        Print the results of the submission check.
        """
        print("\nSubmission Check Results:")
        print("-" * 120)
        print(f"{'Student Name':<30} {'Result':<15} {'File Types':<20} {'Runtime (s)':<15}")
        print("-" * 120)
        
        for student, submission_data in self.results.items():
            if submission_data:
                file_types = submission_data.get('file_types', [])
                file_types_str = ', '.join(file_types) if file_types else 'None'
                tests_passed = submission_data.get('tests_passed', False)
                
                # Extract runtime from the results file
                username = submission_data.get('username', '')
                runtime = 'N/A'
                if username:
                    results_file = os.path.join(self.results_path, f"{username}.txt")
                    if os.path.exists(results_file):
                        with open(results_file, 'r') as f:
                            content = f.read()
                            import re
                            runtime_match = re.search(r'Runtime: ([0-9.]+) seconds', content)
                            if runtime_match:
                                runtime = runtime_match.group(1)
                
                print(f"{student:<30}  {tests_passed:<15} {file_types_str:<20} {runtime:<15}")
            else:
                print(f"{student:<30} {'No submission found':<15}")
        
        # # Save results to CSV
        # self.save_results_to_csv()
        
        # Zip the contents of results and full_output directories
        import zipfile
        
        # Zip full_output directory
        with zipfile.ZipFile('time_full_output.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.full_output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(self.full_output_path)))


    def setup_testing_environment(self, extraction_path, required_files, test_dir, username, file_extension, results_message):
        """
        Set up the testing environment by finding required files and copying test files.
        
        Args:
            extraction_path (str): Path to the extracted submission
            required_files (list): List of required implementation files
            test_dir (str): Directory containing the test files
            username (str): Student's username
            results_message (str): Current results message to append to
            
        Returns:
            If successful: A tuple containing (temp_dir, found_files, updated_results_message)
            If failed: A status code string ('FAIL' or 'ERROR')
        """
        # Check if student has implemented the required files
        missing_files = []
        found_files = {}
        
        # Create a temporary directory for testing
        temp_dir = os.path.join(extraction_path, "temp_test")
        # Only create the directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        
        # Recursively search for required files in the extraction path
        for root, _, files in os.walk(extraction_path):
            # Skip the temp directory
            if "temp_test" in root:
                continue
                
            for file in files:
                if file in required_files and file not in found_files:
                    found_files[file] = os.path.join(root, file)
                    results_message += f"Found {file}\n"

        
        # Check which files are still missing
        for file in required_files:
            if file not in found_files:
                missing_files.append(file)
        
        if missing_files:
            results_message += f"Missing required implementation files: {', '.join(missing_files)}\n"
            results_message += "Cannot proceed with grading without these files.\n"
            print(results_message)
            self.save_results(username, results_message)
            return 'FAIL'
        
        # Create separate test directories for each test
        try:
            # Create a directory for the full test
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            # Only remove the directory if CLEAN_START is true
            if os.path.exists(full_test_dir):
                shutil.rmtree(full_test_dir)
            # Only create the directory if it doesn't exist
            if not os.path.exists(full_test_dir):
                os.makedirs(full_test_dir, exist_ok=True)
            
            # Copy test files, student files, and provided files for the full test
            full_test_file = f"{self.TEST_FILE_NAME}" + file_extension
            results_message = self.copy_test_files(test_dir, full_test_file, full_test_dir, found_files, extraction_path, results_message)
        except Exception as e:
            results_message += f"Error copying files: {str(e)}\n"
            print(results_message)
            self.save_results(username, results_message)
            return 'ERROR'
        
            
        return temp_dir, results_message
    
    def verify_test_pased(self, test_passed):
        if not isinstance(test_passed, bool) or test_passed is False:
            return False
        return True

    def grade_cpp_submission(self, extraction_path, student_name):
        """
        Grade a C++ submission.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            str: Pass/fail status ('PASS', 'FAIL', or 'ERROR')
        """
        # Extract username from extraction_path
        username = os.path.basename(extraction_path)
        
        # Results collection
        results_message = f"Grading C++ submission for {student_name}\n\n"
        
        # Required implementation files
        required_files = [f"{file_name}.h" for file_name in self.REQUIRED_FILE_NAMES]
        
        # Test directory
        test_dir = os.path.join(self.script_dir, f"{self.ASSIGNMENT_NAME}/CPP")
                
        # Set up testing environment
        result = self.setup_testing_environment(extraction_path, required_files, test_dir, username, ".cpp", results_message)
        if isinstance(result, tuple):
            temp_dir, results_message = result
        else:
            # If result is not a tuple, it's a status code indicating an error
            return result
        test_passed = False
            
        # Write full test results to a file in the full_output directory
        full_output_file = os.path.join(self.full_output_path, f"{username}.txt")
        with open(full_output_file, 'w') as f:
            # Create a separate test directory for the full output to avoid conflicts
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            
            # Compile the test file
            output_file = os.path.join(full_test_dir, f'test_full')
            
            # Get the full path to the test file in the test directory
            dest_test_file = os.path.join(full_test_dir, f"{self.TEST_FILE_NAME}.cpp")

            # Record start time
            import time
            start_time = time.time()
            
            test_passed, msg = self.compile_cpp(dest_test_file,output_file,full_test_dir)
            
            # Record end time and calculate runtime
            end_time = time.time()
            runtime = end_time - start_time
            results_message += f"\nRuntime: {runtime:.2f} seconds\n"
            
            if test_passed:
                for string in Config.TIME_CHECK_STRINGS:
                    if string not in msg:
                        test_passed = False
            f.write(f"{msg}")

            if test_passed:
                results_message += "Test passed!\n"
            else:
                results_message += "Test failed!\n"
        # Print and save the results
        print(results_message)
        self.save_results(username, results_message)
        return test_passed
        
    def grade_java_submission(self, extraction_path, student_name):
        """
        Grade a Java submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            bool: True if the time test passed, False otherwise
        """
        # Extract username from extraction_path
        username = os.path.basename(extraction_path)
        
        # Results message
        results_message = f"Time Checker: Grading Java submission for {student_name}\n\n"
        
        # Required implementation files
        required_files = [f"{file_name}.java" for file_name in self.REQUIRED_FILE_NAMES]
        
        # Source directory for test files
        test_dir = os.path.join(self.script_dir, self.ASSIGNMENT_NAME, "JAVA")
        
        # Check if Java compiler is available
        try:
            subprocess.run(["javac", "-version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            results_message += "Java compiler not found. Please install OpenJDK: sudo apt install openjdk-21-jdk\n"
            print(results_message)
            self.save_results(username, results_message)
            return False
        
        # Find required files and set up testing environment
        result = self.setup_testing_environment(extraction_path, required_files, test_dir, username, ".java", results_message)
        if isinstance(result, tuple):
            temp_dir, results_message = result
        else:
            # If result is not a tuple, it's a status code indicating an error
            return False
        
        test_passed = False
        
        # Write full test results to a file in the full_output directory
        full_output_file = os.path.join(self.full_output_path, f"{username}.txt")
        with open(full_output_file, 'w') as f:
            # Create a separate test directory for the full output to avoid conflicts
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            
            dest_test_file = os.path.join(full_test_dir, f"{self.TEST_FILE_NAME}.java")
            
            # Check for and remove package declarations from all Java files in the full test directory
            for file in os.listdir(full_test_dir):
                if file.endswith('.java'):
                    file_path = os.path.join(full_test_dir, file)
                    # We don't need to update results_message for test files
                    self.java_remove_package(file_path, file, results_message)

            # Record start time
            import time
            start_time = time.time()
            
            test_passed, msg = self.compile_java(dest_test_file, full_test_dir)
            
            # Record end time and calculate runtime
            end_time = time.time()
            runtime = end_time - start_time
            results_message += f"\nRuntime: {runtime:.2f} seconds\n"
            
            if test_passed:
                for string in Config.TIME_CHECK_STRINGS:
                    if string not in msg:
                        test_passed = False
                        
            f.write(f"{msg}")
        
            if test_passed:
                results_message += "Test passed!\n"
            else:
                results_message += "Test failed!\n"
        # Print and save the results
        print(results_message)
        self.save_results(username, results_message)

        return test_passed
        
    def grade_csharp_submission(self, extraction_path, student_name):
        """
        Grade a C# submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            bool: True if the time test passed, False otherwise
        """
        # Extract username from extraction_path
        username = os.path.basename(extraction_path)
        
        # Results message
        results_message = f"Time Checker: Grading C# submission for {student_name}\n\n"
        
        # Required implementation files
        required_files = [f"{file_name}.cs" for file_name in self.REQUIRED_FILE_NAMES]
        
        # Test directory
        test_dir = os.path.join(self.script_dir, f'{self.ASSIGNMENT_NAME}/C#')
        
        # Check if C# compiler is available
        try:
            check_compiler = subprocess.run(
                ["mcs", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            results_message += "C# compiler (mcs) not found. Please install Mono: sudo apt install mono-complete\n"
            print(results_message)
            self.save_results(username, results_message)
            return False
        
        # Set up testing environment
        result = self.setup_testing_environment(extraction_path, required_files, test_dir, username, ".cs", results_message)
        if isinstance(result, tuple):
            temp_dir, results_message = result
        else:
            # If result is not a tuple, it's a status code indicating an error
            return False
        
        test_passed = False
            
        # Write full test results to a file in the full_output directory
        full_output_file = os.path.join(self.full_output_path, f"{username}.txt")
        with open(full_output_file, 'w') as f:
            # Create a separate test directory for the full output to avoid conflicts
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            
            # Compile the test file
            output_file = os.path.join(full_test_dir, f'test_full.exe')
            dest_test_file = os.path.join(full_test_dir, f"{self.TEST_FILE_NAME}.cs")

            # Record start time
            import time
            start_time = time.time()
            
            test_passed, msg = self.compile_csharp(dest_test_file, output_file, full_test_dir)
            
            # Record end time and calculate runtime
            end_time = time.time()
            runtime = end_time - start_time
            results_message += f"\nRuntime: {runtime:.2f} seconds\n"
            
            if test_passed:
                for string in Config.TIME_CHECK_STRINGS:
                    if string not in msg:
                        test_passed = False

            f.write(f"{msg}")
            if test_passed:
                results_message += "Test passed!\n"
            else:
                results_message += "Test failed!\n"
        
        # Print and save the results
        print(results_message)
        self.save_results(username, results_message)

        return test_passed

def main():
    """
    Main function to run the time checker.
    """
    checker = TimeChecker()
    checker.run()

if __name__ == "__main__":
    main()
