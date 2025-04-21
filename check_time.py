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
        self.results_path = os.path.join(self.output_dir, "time_results")
        self.full_output_path = os.path.join(self.output_dir, "time_full_output")
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
        
        for username, student_obj in self.results.students.items():
            # Get student name
            student_name = student_obj.get_full_name()
            
            # Get file type
            file_type = student_obj.file_type
            
            # Check if the student passed the time test
            # For TimeChecker, we consider a student to have passed if full_output_passed is True
            tests_passed = "PASS" if student_obj.full_output_passed else "FAIL"
            
            # Extract runtime from the results file
            runtime = 'N/A'
            results_file = os.path.join(self.results_path, f"{username}.txt")
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    content = f.read()
                    import re
                    runtime_match = re.search(r'Runtime: ([0-9.]+) seconds', content)
                    if runtime_match:
                        runtime = runtime_match.group(1)
            
            print(f"{student_name:<30}  {tests_passed:<15} {file_type:<20} {runtime:<15}")
        
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

    def grade_submission(self, extraction_path, student_name, language):
        """
        Unified method to grade a submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            language (str): Programming language ('cpp', 'java', or 'csharp')
            
        Returns:
            bool or str: True/False for Java/C#, 'PASS'/'FAIL'/'ERROR'/'COMPILER_MISSING' for C++
        """
        # Map language to file extension, test file extension, and compiler function
        lang_map = {
            'cpp': {
                'header_ext': '.h',
                'impl_ext': '.cpp',
                'compile_func': self.compile_cpp,
                'test_dir': os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/CPP"),
                'preprocess_func': None,
                'prefix': "",
                'compiler_check': None,
                'compiler_error_msg': "C++ compiler not found"
            },
            'java': {
                'header_ext': '.java',
                'impl_ext': '.java',
                'compile_func': self.compile_java,
                'test_dir': os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/JAVA"),
                'preprocess_func': self.java_remove_package,
                'prefix': "Time Checker: ",
                'compiler_check': lambda: subprocess.run(["javac", "-version"], capture_output=True, check=True),
                'compiler_error_msg': "Java compiler not found. Please install OpenJDK: sudo apt install openjdk-21-jdk"
            },
            'csharp': {
                'header_ext': '.cs',
                'impl_ext': '.cs',
                'compile_func': self.compile_csharp,
                'test_dir': os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/C#"),
                'preprocess_func': None,
                'prefix': "Time Checker: ",
                'compiler_check': lambda: subprocess.run(["mcs", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True),
                'compiler_error_msg': "C# compiler (mcs) not found. Please install Mono: sudo apt install mono-complete"
            }
        }
        
        if language not in lang_map:
            raise ValueError(f"Unsupported language: {language}")
        
        # Get language-specific settings
        header_ext = lang_map[language]['header_ext']
        impl_ext = lang_map[language]['impl_ext']
        compile_func = lang_map[language]['compile_func']
        test_dir = lang_map[language]['test_dir']
        preprocess_func = lang_map[language]['preprocess_func']
        prefix = lang_map[language]['prefix']
        compiler_check = lang_map[language]['compiler_check']
        compiler_error_msg = lang_map[language]['compiler_error_msg']
        
        # Extract username from extraction_path
        username = os.path.basename(extraction_path)
        
        # Results message with appropriate prefix
        results_message = f"{prefix}Grading {language.upper()} submission for {student_name}\n\n"
        
        # Required implementation files
        required_files = [f"{file_name}{header_ext}" for file_name in self.REQUIRED_FILE_NAMES]
        
        # Check if compiler is available
        if compiler_check:
            try:
                compiler_check()
            except (subprocess.SubprocessError, FileNotFoundError):
                results_message += f"{compiler_error_msg}\n"
                print(results_message)
                self.save_results(username, results_message)
                return False if language != 'cpp' else 'COMPILER_MISSING'
        
        # Set up testing environment
        result = self.setup_testing_environment(extraction_path, required_files, test_dir, username, impl_ext, results_message)
        if isinstance(result, tuple):
            temp_dir, results_message = result
        else:
            # If result is not a tuple, it's a status code indicating an error
            return False if language != 'cpp' else result
        
        test_passed = False
        
        # Write full test results to a file in the full_output directory
        full_output_file = os.path.join(self.full_output_path, f"{username}.txt")
        with open(full_output_file, 'w') as f:
            # Create a separate test directory for the full output to avoid conflicts
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            
            # Get the full path to the test file in the test directory
            dest_test_file = os.path.join(full_test_dir, f"{self.TEST_FILE_NAME}{impl_ext}")
            
            # Preprocess files if needed (e.g., Java package removal)
            if preprocess_func:
                for file in os.listdir(full_test_dir):
                    if file.endswith(impl_ext):
                        file_path = os.path.join(full_test_dir, file)
                        preprocess_func(file_path, file, results_message)
            
            # Try up to 3 times if we get a timeout
            max_attempts = 3
            attempt = 1
            msg = ""
            runtime = 0
            
            while attempt <= max_attempts:
                # Record start time
                import time
                start_time = time.time()
                
                # Compile and run the test file
                test_passed, msg = compile_func(dest_test_file, full_test_dir)
                
                # Record end time and calculate runtime
                end_time = time.time()
                runtime = end_time - start_time
                
                if msg != "TIMEOUT" or attempt >= max_attempts:
                    break
                    
                print(f"Timeout detected, attempt {attempt} of {max_attempts}. Retrying...")
                attempt += 1
            
            # Check for compiler missing error (specific to C++)
            if language == 'cpp' and not test_passed and compiler_error_msg in msg:
                print(results_message)
                self.save_results(username, results_message)
                return 'COMPILER_MISSING'
            
            results_message += f"\nRuntime: {runtime:.2f} seconds\n"
            
            # Check if all expected strings are in the output
            if test_passed:
                for string in Config.TIME_CHECK_STRINGS:
                    if string not in msg:
                        test_passed = False
                        break
            
            # Write output to file
            f.write(f"{msg}")

            # Add test result to results message
            if test_passed:
                time_result = "Time Test passed!\n"
                results_message += time_result
            else:
                time_result = "Time Test failed!\n"
                results_message += time_result
            
            # Write time test result to notes file
            notes_dir = os.path.join(self.output_dir, "notes")
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir, exist_ok=True)
            
            notes_file = os.path.join(notes_dir, f"{username}.txt")
            
            # Update existing notes file or create new one
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    notes_content = f.read()
                
                # Check if time test result already exists in the file
                if "Time Test passed!" in notes_content or "Time Test failed!" in notes_content:
                    # Replace existing time test result
                    notes_content = notes_content.replace("Time Test passed!", time_result.strip())
                    notes_content = notes_content.replace("Time Test failed!", time_result.strip())
                else:
                    # Append time test result to file
                    if notes_content:
                        notes_content += "\n"
                    notes_content += time_result
                
                with open(notes_file, 'w') as f:
                    f.write(notes_content)
            else:
                # Create new notes file with time test result
                with open(notes_file, 'w') as f:
                    f.write(time_result)
        
        # Print and save the results
        print(results_message)
        self.save_results(username, results_message)
        
        # Update the Student object in the results with the test outcome
        if username in self.results.students:
            student_obj = self.results.students[username]
            student_obj.full_output_passed = test_passed
            student_obj.full_output = msg
            
            # Set file type based on language
            if language == 'cpp':
                student_obj.file_type = '.h'
            elif language == 'java':
                student_obj.file_type = '.java'
            elif language == 'csharp':
                student_obj.file_type = '.cs'
        
        return test_passed

    def grade_cpp_submission(self, extraction_path, student_name):
        """
        Grade a C++ submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            bool or str: True/False or 'COMPILER_MISSING'
        """
        return self.grade_submission(extraction_path, student_name, 'cpp')

    def grade_java_submission(self, extraction_path, student_name):
        """
        Grade a Java submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            bool: True if the time test passed, False otherwise
        """
        return self.grade_submission(extraction_path, student_name, 'java')
        
    def grade_csharp_submission(self, extraction_path, student_name):
        """
        Grade a C# submission for time-based testing.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_name (str): Name of the student
            
        Returns:
            bool: True if the time test passed, False otherwise
        """
        return self.grade_submission(extraction_path, student_name, 'csharp')

def main():
    """
    Main function to run the time checker.
    """
    checker = TimeChecker()
    checker.run()

if __name__ == "__main__":
    main()
