#!/usr/bin/env python3
import os
import csv
import re
import subprocess
import shutil
import datetime
import time
import json
from typing import List
from config import Config
from results import Results, Student, Test
from config import Config
from generate_results import generate_results_html

class SubmissionChecker:
    """
    A class to check if students have submitted their assignments.
    """
    
    # Class variables
    ASSIGNMENT_NAME = Config.ASSIGNMENT_NAME
    REQUIRED_FILE_NAMES = Config.REQUIRED_FILE_NAMES
    TEST_NAMES = []  # Will be populated from CSV header
    NUM_TEST_FILES = 0  # Will be set based on TEST_NAMES length
    PREFERRED_FILE_TYPE_ORDER = ['.java', '.cs', '.h']  # Order of preference: Java, C#, C++
    TEST_FILE_NAME = "TestCorrectness"
    MAIN_TEST_FOLDER = "full_test"
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    
    
    def __init__(self, csv_file=f"{ASSIGNMENT_NAME}.csv", submissions_dir="submissions"):
        """
        Initialize the SubmissionChecker with file paths.
        
        Args:
            csv_file (str): Path to the CSV file containing student names
            submissions_dir (str): Path to the directory containing submissions
        """
        # Get the absolute path to the script's directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(self.script_dir, self.INPUT_DIR)
        self.output_dir = os.path.join(self.script_dir, self.OUTPUT_DIR)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Construct absolute paths
        self.csv_path = os.path.join(self.input_dir, csv_file)
        self.csv_results_file = "results.csv"
        self.submissions_path = os.path.join(self.output_dir, submissions_dir)
        self.results_path = os.path.join(self.output_dir, "results")
        self.full_output_path = os.path.join(self.output_dir, "full_output")
        self.notes_path = os.path.join(self.output_dir, "notes")
        
        # Initialize Results object (will populate TEST_NAMES later)
        self.results = Results([])
        
        # List to store submission files
        self.submission_files = []
    
    def get_submission_files(self):
        """
        Get a list of all zip files in the submissions directory.
        If the submissions directory doesn't exist, try to extract submissions.zip.
        
        Returns:
            list: List of zip filenames
        """
        # Check if submissions directory exists
        if Config.CLEAN_START and os.path.exists(self.submissions_path):
            print(f"CLEAN_START enabled: Deleting existing submissions directory at: {self.submissions_path}")
            shutil.rmtree(self.submissions_path)
            print(f"Creating submissions directory at: {self.submissions_path}")
            os.makedirs(self.submissions_path, exist_ok=True)
        elif not os.path.exists(self.submissions_path):
            print(f"Creating submissions directory at: {self.submissions_path}")
            os.makedirs(self.submissions_path, exist_ok=True)
        
        # Check if submissions.zip exists
        submissions_zip = os.path.join(self.input_dir, "submissions.zip")
        
        # Only extract if CLEAN_START is enabled or the submissions directory is empty
        if os.path.exists(submissions_zip) and (Config.CLEAN_START or not os.listdir(self.submissions_path)):
            print(f"Found submissions.zip. Extracting to: {self.submissions_path}")
            
            # Extract the zip file
            import zipfile
            with zipfile.ZipFile(submissions_zip, 'r') as zip_ref:
                zip_ref.extractall(self.submissions_path)
                
            print(f"Extraction complete.")
        elif not os.path.exists(submissions_zip) and not os.listdir(self.submissions_path):
            print(f"Error: submissions.zip not found and submissions directory is empty.")
            return []
        
        # Get list of all zip files in submissions directory
        if os.path.exists(self.submissions_path):
            self.submission_files = [f for f in os.listdir(self.submissions_path) if f.endswith('.zip')]
            return self.submission_files
        else:
            return []
    
    def parse_student_name(self, name_string):
        """
        Parse a student name from the CSV format.
        
        Args:
            name_string (str): The name string from the CSV
            
        Returns:
            tuple: (last_name, first_name, search_pattern) or (None, None, None) if invalid
        """
        # Remove quotes and split by comma
        student_name = name_string.strip('"').split(',')
        
        if len(student_name) < 1:
            print(f"Warning: Invalid name format for {name_string}")
            return None, None, None
        
        # If only one part is available (e.g., "Group 1")
        if len(student_name) < 2:
            # Use the first part as the search name
            search_name = student_name[0].strip().lower().replace(" ", "")
            return student_name[0].strip(), "", search_name
        
        # Get last name and first name
        last_name = student_name[0].strip()
        first_name = student_name[1].strip()
        
        # Create the search pattern based on configuration
        if Config.SEARCH_PATTERN_USE_FIRST_NAME_FIRST:
            # First name + last name
            search_name = (first_name + last_name).lower().replace(" ", "")
        else:
            # Last name + first name
            search_name = (last_name + first_name).lower().replace(" ", "")
        
        # Limit to 8 characters or the length of the string, whichever is less
        search_length = min(len(search_name), 8)
        search_pattern = search_name[:search_length]
        
        return last_name, first_name, search_pattern
    
    def find_matching_submission(self, search_pattern):
        """
        Find a submission file that matches the search pattern.
        If found, extract the zip file into a folder with the student's username.
        
        Args:
            search_pattern (str): The pattern to search for
            
        Returns:
            tuple: (submission_filename, username, extraction_path) or (None, None, None) if not found
        """
        for submission in self.submission_files:
            # Check if the submission filename starts with the search pattern
            if submission.lower().startswith(search_pattern):
                # Split the submission filename on "_" to get the username
                parts = submission.split("_")
                if parts:
                    username = parts[0]
                    
                    # Create the extraction path within the submissions directory
                    extraction_path = os.path.join(self.submissions_path, username)
                    
                    # Check if the folder already exists
                    if not os.path.exists(extraction_path):
                        # print(f"Creating folder and extracting submission for: {username} in submissions directory")
                        
                        # Create the folder
                        os.makedirs(extraction_path, exist_ok=True)
                        
                        # Extract the zip file
                        import zipfile
                        submission_path = os.path.join(self.submissions_path, submission)
                        try:
                            with zipfile.ZipFile(submission_path, 'r') as zip_ref:
                                zip_ref.extractall(extraction_path)
                            print(f"Extraction complete for: {username} in submissions directory")
                        except Exception as e:
                            print(f"Error extracting {submission}: {e}")
                    else:
                        print(f"Folder already exists for: {username} in submissions directory")
                
                return submission, username, extraction_path
        return None, None, None
    
    def process_csv(self):
        """
        Process the CSV file and check for matching submissions.
        
        Returns:
            dict: Dictionary of student names and their submission details
        """
        # Get submission files
        self.get_submission_files()

        if not os.path.exists(self.notes_path):
            print(f"Creating notes directory at: {self.notes_path}")
            os.makedirs(self.notes_path, exist_ok=True)
        
        # Create or clean results directory
        if not os.path.exists(self.results_path):
            print(f"Creating results directory at: {self.results_path}")
            os.makedirs(self.results_path, exist_ok=True)
        else:
            print(f"Cleaning existing results directory at: {self.results_path}")
            # Only delete files that aren't in IGNORE_NAMES
            for file in os.listdir(self.results_path):
                file_path = os.path.join(self.results_path, file)
                if os.path.isfile(file_path):
                    # Extract username from filename (remove .txt extension)
                    username = os.path.splitext(file)[0]
                    if hasattr(Config, 'IGNORE_NAMES') and username in Config.IGNORE_NAMES:
                        print(f"Preserving: {file_path}")
                    else:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
        
        # Create or clean full output directory
        if not os.path.exists(self.full_output_path):
            print(f"Creating full output directory at: {self.full_output_path}")
            os.makedirs(self.full_output_path, exist_ok=True)
        else:
            print(f"Cleaning existing full output directory at: {self.full_output_path}")
            # Only delete files that aren't in IGNORE_NAMES
            for file in os.listdir(self.full_output_path):
                file_path = os.path.join(self.full_output_path, file)
                if os.path.isfile(file_path):
                    # Extract username from filename (remove .txt extension)
                    username = os.path.splitext(file)[0]
                    if hasattr(Config, 'IGNORE_NAMES') and username in Config.IGNORE_NAMES:
                        print(f"Preserving: {file_path}")
                    else:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
        
        # Read the CSV file
        with open(self.csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            # Read header row to get test names
            header = next(csv_reader)
            # Get test names from header (columns between the first and 'Language')
            language_index = header.index('Language')
            self.TEST_NAMES = [name.strip() for name in header[1:language_index]]
            self.NUM_TEST_FILES = len(self.TEST_NAMES)
            
            # Initialize Results object with test names
            self.results = Results(self.TEST_NAMES)

            # Process each student
            for row in csv_reader:
                if not row or not row[0]:
                    continue
                
                # Parse student name
                last_name, first_name, search_pattern = self.parse_student_name(row[0])
                
                if not search_pattern:
                    continue
                
                # Look for matching submission
                submission_file, username, extraction_path = self.find_matching_submission(search_pattern)
                
                # Check if a notes file exists for this student, and create one if not
                if username:
                    notes_file_path = os.path.join(self.notes_path, f"{username}.txt")
                    if not os.path.exists(notes_file_path):
                        # Create an empty notes file
                        open(notes_file_path, 'w').close()

                # Create Student object
                student = Student(first_name, last_name, username)

                self.results.add_student(student)
                # Ignore student
                if username in Config.IGNORE_NAMES:
                    print(f"Ignoring student: {last_name}, {first_name}")
                    continue

                if submission_file:
                    # Check for file types in the extraction path
                    file_types = self.check_file_types(extraction_path)

                    # Initialize tests as empty list
                    status = 'Not graded'
                    test_passed = [False] * self.NUM_TEST_FILES
                    
                    if len(file_types) > 1:
                        # Create initial message about multiple file types
                        output_message = f"WARNING: Multiple file types found for {last_name}, {first_name}: {', '.join(file_types)}\n"
                        output_message += "Trying each file type in order: Java, C#, C++\n\n"
                        print(f"\n{'='*80}\n{output_message}\n{'='*80}\n")
                        
                        # Try each file type until one passes or all fail
                        test_passed, was_tested = self.try_grade_with_file_types(extraction_path, file_types, username, output_message)
                        if was_tested:
                            status = "Tested"
                    elif len(file_types) == 0:
                        output_message = f"WARNING: No recognized file types found for {last_name}, {first_name}"
                        print(f"\n{'='*80}\n{output_message}\n{'='*80}\n")
                        # Save the results to a file
                        self.save_results(username, output_message)
                        # Don't call any grading function for no file types
                        status = 'Not submitted'
                    elif len(file_types) == 1:
                        # Call the appropriate grading function based on file type
                        student.file_type = file_types[0]
                        status = "Tested"
                        if student.file_type == '.h':
                            test_passed = self.grade_cpp_submission(extraction_path, username)
                        elif student.file_type == '.java':
                            test_passed = self.grade_java_submission(extraction_path, username)
                        elif student.file_type == '.cs':
                            test_passed = self.grade_csharp_submission(extraction_path, username)
                    
                    test_passed = self.verify_test_pased(test_passed)

                    # Add test results to the student
                    # output_file_path = os.path.join(self.full_output_path, f"{username}.txt")
                    # if os.path.exists(output_file_path):
                    #     with open(output_file_path, 'r') as f:
                    #         student.full_output = f.read()
                    # else:
                    #     student.full_output = "Output file not found. Test may have failed to generate output."

                else:
                    # Student with no submission still gets a Student object
                    pass

                # Add the student to results
                self.results.add_student(student)
        
        return self.results

    def verify_test_pased(self, test_passed):
        if not isinstance(test_passed, list):
            test_passed = [False] * self.NUM_TEST_FILES
        return test_passed

    def save_results(self, name, output):
        """
        Save the output string to a text file in the results folder.
        
        Args:
            name (str): The name to use for the file
            output (str): The content to write to the file
        """
        # Create a valid filename from the name
        name_parts = name.split(",")
        if len(name_parts) > 1:
            name = name_parts[1] + name_parts[0]
        filename = name.replace(" ", "_").lower() + ".txt"
        file_path = os.path.join(self.results_path, filename)
        
        try:
            # Replace literal \n with actual newlines
            # This is needed because some strings might contain \n that should be rendered as newlines
            formatted_output = output.replace('\\n', '\n')
            
            with open(file_path, 'w') as file:
                file.write(formatted_output)
            # print(f"Results saved to: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error saving results to {file_path}: {e}")
    
    def try_grade_with_file_types(self, extraction_path, file_types, username, initial_message=""):
        """
        Try grading the submission with each file type until one passes or all fail.
        
        Args:
            extraction_path (str): Path to the extracted files
            student_full_name (str): Name of the student
            file_types (list): List of file types found in the submission
            username (str): Username for saving results
            initial_message (str): Initial message to include in the results
            
        Returns:
            str: Pass/fail status
        """
        
        # Try each file type in order of preference
        # This order is defined in the class variable PREFERRED_FILE_TYPE_ORDER
        preferred_order = self.PREFERRED_FILE_TYPE_ORDER
        
        # Filter file_types to only include those in preferred_order
        ordered_types = [ft for ft in preferred_order if ft in file_types]
        
        # Save the initial message
        self.save_results(username, initial_message)
        
        # Try each file type
        for file_type in ordered_types:
            if file_type == '.h':
                test_results = self.grade_cpp_submission(extraction_path, username)
            elif file_type == '.java':
                test_results = self.grade_java_submission(extraction_path, username)
            elif file_type == '.cs':
                test_results = self.grade_csharp_submission(extraction_path, username)
            else:
                continue
            
            if not isinstance(test_results, list):
                continue

            # If the grading passed, return immediately
            for result in test_results:
                if result:
                    additional_msg = f"Successfully graded {self.results.students[username].get_full_name()} using {file_type} files.\n"
                    self.append_to_results(username, additional_msg)
                    self.results.students[username].file_type = file_type
                    return test_results, True
        
        # If we get here, all file types failed
        fail_msg = f"All file types failed for {self.results.students[username].get_full_name()}.\n"
        self.append_to_results(username, fail_msg)
        return [False] * self.NUM_TEST_FILES, False
    
    def append_to_results(self, name, output):
        """
        Append output to an existing results file.
        
        Args:
            name (str): Name of the file to append to
            output (str): Output string to append
        """
        # Create a valid filename from the name
        filename = name.replace(" ", "_").replace(",", "").lower() + ".txt"
        file_path = os.path.join(self.results_path, filename)
        
        try:
            # Replace literal \n with actual newlines
            formatted_output = output.replace('\\n', '\n')
            
            with open(file_path, 'a') as file:
                file.write(formatted_output)
        except Exception as e:
            print(f"Error appending to results file {file_path}: {e}")
    
    def java_remove_package(self, file_path, file_name, results_message):
        """
        Remove package declaration from a Java file.
        
        Args:
            file_path (str): Path to the Java file
            file_name (str): Name of the file (for results message)
            results_message (str): Current results message
            
        Returns:
            str: Updated results message
        """
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        # Check if the file has a package declaration
        if content and content[0].strip().startswith('package '):
            # Remove the package line
            content = content[1:]
            
            # Write the modified content back to the file
            with open(file_path, 'w') as f:
                f.writelines(content)
            
            # Update the results message to indicate package declaration was removed
            # Find the line with "Found {file_name}" and replace it
            old_line = f"Found {file_name}\n"
            new_line = f"Found {file_name} (removed package declaration)\n"
            results_message = results_message.replace(old_line, new_line)
        
        return results_message
    
    def copy_test_files(self, test_dir, test_file, test_temp_dir, found_files, extraction_path, results_message):
        """
        Copy test files, student implementation files, and provided files to the test directory.
        
        Args:
            test_dir (str): Directory containing the test files
            test_file (str): Name of the test file to copy
            test_temp_dir (str): Temporary directory to copy files to
            found_files (dict): Dictionary of found student implementation files
            extraction_path (str): Path to the extracted submission
            results_message (str): Current results message to append to
            
        Returns:
            str: Updated results message
        """
        # Copy the test file
        source_file = os.path.join(test_dir, test_file)
        
        # If test_file has a number in it, remove the number for dest_test_file
        import re
        dest_file_name = re.sub(fr'({self.TEST_FILE_NAME})\d+(\.\w+)', r'\1\2', test_file)
        dest_test_file = os.path.join(test_temp_dir, dest_file_name)
        
        if os.path.exists(source_file) and (Config.CLEAN_START or not os.path.exists(dest_test_file)):
            # Copy to the destination with the modified file name
            shutil.copy(source_file, dest_test_file)

        # Copy all found student implementation files to temp directory
        for file, file_path in found_files.items():
            # Copy the file to the temp directory
            temp_file_path = os.path.join(test_temp_dir, file)
            if Config.CLEAN_START or not os.path.exists(temp_file_path):
                shutil.copy2(file_path, temp_file_path)
        
        # Copy provided files
        for provided_file in Config.PROVIDED_FILE_NAMES:
            # Determine language from test_dir path
            if '/JAVA' in test_dir:
                provided_file_with_ext = f"{provided_file}.java"
            elif '/CPP' in test_dir:
                provided_file_with_ext = f"{provided_file}.h"
            elif '/C#' in test_dir:
                provided_file_with_ext = f"{provided_file}.cs"
            else:
                # Skip if language is not recognized
                results_message += f"Skipping provided file: {provided_file}\n"
                continue
            
            source_file = os.path.join(test_dir, provided_file_with_ext)
            dest_file = os.path.join(test_temp_dir, provided_file_with_ext)
            if os.path.exists(source_file) and (Config.CLEAN_START or not os.path.exists(dest_file)):
                shutil.copy(source_file, test_temp_dir)
        
        return results_message
    
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
            # Create a directory for each test
            for i in range(1, self.NUM_TEST_FILES + 1):
                test_file = f"{self.TEST_FILE_NAME}{i}{file_extension}"
                test_temp_dir = os.path.join(temp_dir, f"test_{i}")
                # Only remove the directory if CLEAN_START is true
                if Config.CLEAN_START and os.path.exists(test_temp_dir):
                    shutil.rmtree(test_temp_dir)
                # Only create the directory if it doesn't exist
                if not os.path.exists(test_temp_dir):
                    os.makedirs(test_temp_dir, exist_ok=True)
                
                # Copy test files, student files, and provided files
                results_message = self.copy_test_files(test_dir, test_file, test_temp_dir, found_files, extraction_path, results_message)

                
            # Create a directory for the full test
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            # Only remove the directory if CLEAN_START is true
            if Config.CLEAN_START and os.path.exists(full_test_dir):
                shutil.rmtree(full_test_dir)
            # Only create the directory if it doesn't exist
            if not os.path.exists(full_test_dir):
                os.makedirs(full_test_dir, exist_ok=True)
            
            # Copy test files, student files, and provided files for the full test
            full_test_file = f"{self.TEST_FILE_NAME}" + file_extension
            results_message += self.copy_test_files(test_dir, full_test_file, full_test_dir, found_files, extraction_path, results_message)
        except Exception as e:
            results_message += f"Error copying files: {str(e)}\n"
            print(f"Error copying files: {str(e)}\n")
            self.save_results(username, results_message)
            return 'ERROR'
        
            
        return temp_dir, results_message
    
    def check_file_types(self, extraction_path):
        """
        Check for specific file types in the extraction path.
        
        Args:
            extraction_path (str): Path to the extracted files
            
        Returns:
            list: List of file types found (.h, .java, .cs)
        """
        file_types = []
        
        # Check if the extraction path exists
        if not os.path.exists(extraction_path):
            return file_types
        
        # Define file extensions to check
        extensions = {
            '.h': "C++",
            '.java': "Java",
            '.cs': "C#"
        }
        
        # Walk through all files in the extraction path
        for root, dirs, files in os.walk(extraction_path):
            for file in files:
                # Check for each file extension
                for ext in extensions:
                    if file.endswith(ext) and ext not in file_types:
                        file_types.append(ext)
                        break
        
        return file_types
    
    def save_results_to_csv(self):
        """
        Save the results to a CSV file.
        """
        # Save to a specific file called results.csv
        csv_filename = os.path.join(self.output_dir, self.csv_results_file)
        
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Student'] + self.TEST_NAMES + ['Language', 'Comments']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            # Create a list of rows to write, so we can sort them
            rows_to_write = []

            print("*" * 120)
            print("Saving results to CSV file...")
            print("*" * 120)
            print(f"Number of students: {len(self.results.students)}")

            
            for username, student in self.results.students.items():
                first_name = student.first_name
                last_name = student.last_name
                student_full_name = f"{last_name}, {first_name}"
                print(f"Processing student: {student_full_name}")

                has_tests = len(student.tests) > 0

                if has_tests:
                    print(f"Student {student_full_name} has tests.")
                    row = {'Student': student_full_name}
                    # Add test results
                    for test_name in self.TEST_NAMES:
                        test_result = next((test for test in student.tests if test.name == test_name), None)
                        if test_result:
                            row[test_name] = 'Works correctly' if test_result.passed else 'Does not produce correct output'
                        else:
                            row[test_name] = 'N/A'
                    
                    # Add language based on file types
                    languages = {'.java': 'Java', '.cs': 'C#', '.h': 'C++'}
                    row['Language'] = languages.get(student.file_type, '')

                    # Add comments (could be expanded in the future)
                    row['Comments'] = ''
                else:
                    # For students with no submission
                    row = {'Student': student_full_name}
                    
                    # Set all test results to N/A
                    for test_name in self.TEST_NAMES:
                        row[test_name] = 'Not submitted'
                    
                    # Set language and comments
                    row['Language'] = ''
                    row['Comments'] = 'No submission'
                    
                rows_to_write.append(row)
                        
            # Write the sorted rows
            for row in rows_to_write:
                writer.writerow(row)
        
        print(f"\nResults saved to CSV file: {csv_filename}")
        return csv_filename
    
    def print_results(self):
        """
        Print the results of the submission check.
        """
        print("\nSubmission Check Results:")
        print("-" * 120)
        print(f"{'Student Name':<30} {'Submission File':<30} {'Extraction Path':<20} {'File Types':<20} {'Status':<15}")
        print("-" * 120)
        
        for username, student in self.results.students.items():
            first_name = student.first_name
            last_name = student.last_name
            student_full_name = f"{last_name}, {first_name}"

            has_submission = len(student.tests) > 0

            if has_submission:
                # Find submission file and extraction path
                submission_file = "Unknown"
                extraction_path = "Unknown"
                for root, _, files in os.walk(self.submissions_path):
                    if os.path.basename(root) == username:
                        extraction_path = os.path.basename(root)
                        for file in files:
                            if file.endswith('.zip'):
                                submission_file = file
                                break
                        break

                file_types_str = student.file_type if student.file_type else 'None'
                status = 'Tested' if student.tests else 'Not submitted'
                
                # Create test results string
                test_results_str = ""
                for test in student.tests:
                    test_result = "PASS" if test.passed else "FAIL"
                    test_results_str += f"{test.name}: {test_result}  "
                
                print(f"{student_full_name:<30} {submission_file:<30} {extraction_path:<20} {file_types_str:<20} {status:<15} {test_results_str}")
            else:
                print(f"{student_full_name:<30} {'No submission found':<30} {'':<20} {'':<20} {'N/A':<15}")
        
        # Save results to CSV
        self.save_results_to_csv()
        
        # Zip the contents of results and full_output directories
        import zipfile
        
        # Zip results directory
        results_zip_path = os.path.join(self.output_dir, 'results.zip')
        with zipfile.ZipFile(results_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.results_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(self.results_path)))
        
        # Zip full_output directory
        full_output_zip_path = os.path.join(self.output_dir, 'full_output.zip')
        with zipfile.ZipFile(full_output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.full_output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(self.full_output_path)))
    
    def compare_results(self, output, expected_file):
        """
        Compare the output string with the content of the expected file.
        Ignores blank lines.
        
        Args:
            output (str): The output string to compare
            expected_file (str): Path to the expected output file
            
        Returns:
            tuple: (bool, str) - (True if match, error message if any)
        """
        try:
            with open(expected_file, 'r') as f:
                expected_content = f.read()
            
            # Filter out blank lines
            output_lines = [line.strip() for line in output.split('\n') if line.strip()]
            expected_lines = [line.strip() for line in expected_content.split('\n') if line.strip()]
            
            if output_lines == expected_lines:
                return True, ""
            else:
                # Find differences for error message
                error_msg = "Output does not match expected output:\n"
                error_msg += "Actual output:\n" + output + "\n"
                return False, error_msg
        except Exception as e:
            return False, f"Error comparing results: {str(e)}"

    def compile_cpp(self, dest_test_file, temp_dir) -> (bool, str):
        """
        Compile a C++ source file.
        
        Args:
            dest_test_file (str): Path to the destination test file
            temp_dir (str): Path to the temporary directory
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Generate output file path
            output_file = os.path.join(temp_dir, 'test')
            
            compile_process = subprocess.run(
                ['g++', '-o', output_file, dest_test_file], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            if compile_process.returncode != 0:
                # Get both stdout and stderr for more complete error information
                error_output = compile_process.stdout + "\n" + compile_process.stderr
                
                # Replace absolute paths with just the filename to make errors more readable
                error_output = re.sub(r'/home/[^:]+/([^:/]+\.\w+)', r'\1', error_output)
                
                # Create a detailed error message
                error_msg = f"Compilation failed with the following errors:\n{error_output}"
                return (False, f"FAILED - Compilation Error\n{error_output}")
            
            # Run the compiled test with a 15-minute timeout
            try:
                run_process = subprocess.run(
                    [output_file], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=temp_dir,
                    timeout=900  # 15 minutes in seconds
                )
            except subprocess.TimeoutExpired:
                return (False, "TIMEOUT")
            
            return (True, run_process.stdout)
                
        except Exception as e:
            return (False, f"ERROR - {str(e)}")
    
    def grade_submission(self, extraction_path, username, language):
        """
        Generic submission grading method that handles the common workflow for all languages
        
        Args:
            extraction_path (str): Path to the extracted files
            username (str): Student username
            language (str): Language type ('cpp', 'java', 'csharp')
            
        Returns:
            list or bool: Test results
        """
        # Map language to file extension and compiler function
        lang_map = {
            'cpp': ('.h', '.cpp', self.compile_cpp),
            'java': ('.java', '.java', self.compile_java),
            'csharp': ('.cs', '.cs', self.compile_csharp)
        }
        
        if language not in lang_map:
            raise ValueError(f"Unsupported language: {language}")
            
        file_ext, test_ext, compile_func = lang_map[language]
        
        # Results collection
        results_message = f"Grading {language.upper()} submission for {self.results.students[username].get_full_name()}\n\n"
        
        # Required implementation files
        required_files = [f"{file_name}{file_ext}" for file_name in self.REQUIRED_FILE_NAMES]
        
        # Get language-specific directory
        lang_dir_map = {
            'cpp': 'CPP',
            'java': 'JAVA',
            'csharp': 'C#'
        }
        
        # Test directory
        test_dir = os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/{lang_dir_map[language]}")
        
        # Special handling for Java package declarations
        preprocess_func = None
        if language == 'java':
            # Check if Java compiler is available
            try:
                subprocess.run(["javac", "-version"], capture_output=True, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                results_message += "Java compiler not found. Please install OpenJDK: sudo apt install openjdk-21-jdk\n"
                print(results_message)
                self.save_results(username, results_message)
                return 'COMPILER_MISSING'
            preprocess_func = self.java_remove_package
        elif language == 'csharp':
            # Check if .NET SDK is available
            try:
                check_compiler = subprocess.run(
                    ['dotnet', '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if check_compiler.returncode != 0:
                    results_message += ".NET SDK not found on this system. Cannot compile C# code.\n"
                    results_message += "To grade C# submissions, please install .NET SDK: https://dotnet.microsoft.com/download\n"
                    print(results_message)
                    self.save_results(username, results_message)
                    return 'COMPILER_MISSING'
                    
            except Exception as e:
                results_message += f"Error checking for .NET SDK: {str(e)}\n"
                print(f"Error checking for .NET SDK: {str(e)}\n")
                self.save_results(username, results_message)
                return 'ERROR'
                
        # Set up testing environment
        result = self.setup_testing_environment(extraction_path, required_files, test_dir, username, test_ext, results_message)
        if isinstance(result, tuple):
            temp_dir, results_message = result
        else:
            # If result is not a tuple, it's a status code indicating an error
            return result
            
        test_results = []
        test_passed = [False] * self.NUM_TEST_FILES  # Track which tests passed
        
        # For each test file
        for i in range(0, self.NUM_TEST_FILES):
            test_results.append(f"Test {i+1}: ")
            
            # Create a separate test directory for each test to avoid naming conflicts
            test_temp_dir = os.path.join(temp_dir, f"test_{i+1}")
            
            # Get the full path to the test file in the test directory
            dest_test_file = os.path.join(test_temp_dir, f"{self.TEST_FILE_NAME}{test_ext}")
            output_file = os.path.join(test_temp_dir, f'test')
            
            # Preprocess files if needed (e.g., Java package removal)
            if preprocess_func and language == 'java':
                for file in os.listdir(test_temp_dir):
                    if file.endswith(file_ext):
                        file_path = os.path.join(test_temp_dir, file)
                        preprocess_func(file_path, file, results_message)
            
            # Try up to 3 times if we get a timeout
            max_attempts = 3
            attempt = 1
            msg = ""
            while attempt <= max_attempts:
                # All compile functions now take the same parameters
                test_passed[i], msg = compile_func(dest_test_file, test_temp_dir)
                
                if msg != "TIMEOUT" or attempt >= max_attempts:
                    break
                    
                print(f"Timeout detected for test {i+1}, attempt {attempt} of {max_attempts}. Retrying...")
                attempt += 1
                
            test_result_obj = Test(self.TEST_NAMES[i], test_passed[i], msg)
            
            if test_passed[i]:
                # Compare output with expected output
                test_passed[i], error_msg = self.compare_results(msg, os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/expectedoutput{i+1}.txt"))
                test_result_obj.passed = test_passed[i]
                if test_passed[i]:
                    msg = "PASSED"
                else:
                    msg = f"FAILED - {error_msg}"
            
            # Check for compiler missing error
            if not test_passed[i]:
                if language == 'cpp' and "C++ compiler not found" in msg:
                    print(results_message)
                    self.save_results(username, results_message)
                    return 'COMPILER_MISSING'
                elif language == 'java' and "Java compiler not found" in msg:
                    print(results_message)
                    self.save_results(username, results_message)
                    return 'COMPILER_MISSING'
                elif language == 'java' and "Java runtime not found" in msg:
                    print(results_message)
                    self.save_results(username, results_message)
                    return 'ERROR'
            
            self.results.students[username].tests.append(test_result_obj)
            test_results.append(msg+"\n")
            
        # Write full test results to a file in the full_output directory
        full_output_file = os.path.join(self.full_output_path, f"{username}.txt")
        with open(full_output_file, 'w') as f:
            # Create a separate test directory for the full output to avoid conflicts
            full_test_dir = os.path.join(temp_dir, self.MAIN_TEST_FOLDER)
            
            # Compile the test file
            output_file = os.path.join(full_test_dir, f'test_full')
            dest_test_file = os.path.join(full_test_dir, f"{self.TEST_FILE_NAME}{test_ext}")

            # Preprocess files if needed (e.g., Java package removal)
            if preprocess_func and language == 'java':
                for file in os.listdir(full_test_dir):
                    if file.endswith(file_ext):
                        file_path = os.path.join(full_test_dir, file)
                        preprocess_func(file_path, file, results_message)
            
            # All compile functions now take the same parameters
            _, msg = compile_func(dest_test_file, full_test_dir)
                
            self.results.students[username].full_output = msg
            self.results.students[username].full_output_passed, _ = self.compare_results(msg, os.path.join(self.input_dir, f"{self.ASSIGNMENT_NAME}/expectedoutput.txt"))

            f.write(f"{msg}")
        
        # Format the results - slightly different between languages
        if language == 'cpp':
            for i in range(0, len(test_results), 2):
                results_message += test_results[i] + "\n"
                if i+1 < len(test_results):
                    results_message += "  " + test_results[i+1] + "\n\n"
        else:  # Java and C#
            for i in range(0, len(test_results), 2):
                if i+1 < len(test_results):
                    results_message += f"{test_results[i]}{test_results[i+1]}"
                else:
                    results_message += f"{test_results[i]}"
            results_message += "\n"
                
        # Print and save the results
        # print(results_message)
        self.save_results(username, results_message)
        
        return test_passed
        
    def grade_cpp_submission(self, extraction_path, username):
        """
        Grade a C++ submission.
        
        Args:
            extraction_path (str): Path to the extracted files
            username (str): Name of the student
            
        Returns:
            list or str: Test results or status code
        """
        return self.grade_submission(extraction_path, username, 'cpp')
    
    def compile_java(self, dest_test_file, temp_dir) -> (bool, str):
        """Compile a Java source file.

        Args:
            src_test_file (str): Path to the source test file
            dest_test_file (str): Path to the destination test file
            temp_dir (str): Path to the temporary directory
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Compile the test file with the student's implementation
            compile_cmd = ["javac", dest_test_file]
            compile_result = subprocess.run(
                compile_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )
            
            if compile_result.returncode != 0:
                # Get both stdout and stderr for more complete error information
                error_output = compile_result.stdout + "\n" + compile_result.stderr
                
                # Replace absolute paths with just the filename to make errors more readable
                error_output = re.sub(r'/home/[^:]+/([^:/]+\.\w+)', r'\1', error_output)
                
                # Create a detailed error message
                error_msg = f"Compilation failed with the following errors:\n{error_output}"
                return (False, f"FAILED - Compilation Error\n{error_output}")
            
            # Run the compiled test with a 15-minute timeout
            run_cmd = ["java", f"{self.TEST_FILE_NAME}"]
            try:
                run_result = subprocess.run(
                    run_cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=temp_dir,
                    timeout=900  # 15 minutes in seconds
                )
            except subprocess.TimeoutExpired:
                return (False, "TIMEOUT")
            
            if run_result.returncode != 0:
                return (False, f"FAILED - Runtime error: {run_result.stderr}")
                
            return (True, run_result.stdout)
                
        except Exception as e:
            return (False, f"ERROR - {str(e)}")

    def grade_java_submission(self, extraction_path, username):
        """
        Grade a Java submission.
        
        Args:
            extraction_path (str): Path to the extracted files
            username (str): Name of the student
            
        Returns:
            list or str: Test results or status code
        """
        return self.grade_submission(extraction_path, username, 'java')
    
    def compile_csharp(self, dest_test_file, temp_dir) -> (bool, str):
        """
        Compile a C# source file.
        
        Args:
            dest_test_file (str): Path to the destination test file
            temp_dir (str): Path to the temporary directory
            
        Returns:
            tuple: (success, message)
        """
        # Copy the test file to the temp directory
        try:
            # Read the test file from the test directory
            with open(dest_test_file, 'r') as f:
                content = f.read()
            
            # Add System namespace if not present
            if 'using System;' not in content:
                content = 'using System;\n' + content
                            
            # Write the modified test file to the test temp directory
            with open(dest_test_file, 'w') as f:
                f.write(content)
        except Exception as e:
            return (False, f"FAILED - Error copying test file: {str(e)}")
            
        try:
            # Get all .cs files in this test temp directory
            cs_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.cs')]
            
            # Generate output file path
            output_file = os.path.join(temp_dir, 'test.exe')
            
            # Create a temporary directory for compilation
            project_dir = temp_dir
            
            # Create a simple project file
            csproj_path = os.path.join(temp_dir, "TestProject.csproj")
            with open(csproj_path, 'w') as f:
                f.write('<Project Sdk="Microsoft.NET.Sdk">\n')
                f.write('  <PropertyGroup>\n')
                f.write('    <OutputType>Exe</OutputType>\n')
                f.write('    <TargetFramework>net8.0</TargetFramework>\n')
                f.write('    <ImplicitUsings>enable</ImplicitUsings>\n')
                f.write('    <Nullable>enable</Nullable>\n')
                f.write('    <WarningLevel>0</WarningLevel>\n')
                f.write('  </PropertyGroup>\n')
                f.write('</Project>\n')
            
            # Compile using dotnet build with warning suppression but showing detailed errors
            compile_process = subprocess.run(
                ['dotnet', 'build', csproj_path, '-c', 'Release', '--verbosity', 'quiet'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )
            
            if compile_process.returncode != 0:
                # Get both stdout and stderr for more complete error information
                error_output = compile_process.stdout + "\n" + compile_process.stderr
                
                # Replace absolute paths with just the filename to make errors more readable
                error_output = re.sub(r'/home/[^:]+/([^:/]+\.\w+)', r'\1', error_output)
                
                # Create a detailed error message
                error_msg = f"Compilation failed with the following errors:\n{error_output}"
                return (False, f"FAILED - Compilation Error\n{error_output}")
            
            # Run using dotnet run with a 15-minute timeout
            try:
                run_process = subprocess.run(
                    ['dotnet', 'run', '--project', csproj_path, '-c', 'Release', '--verbosity', 'quiet'], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=temp_dir,
                    timeout=900  # 15 minutes in seconds
                )
            except subprocess.TimeoutExpired:
                return (False, "TIMEOUT")
            
            return (True, run_process.stdout)
                
        except FileNotFoundError as e:
            if 'dotnet' in str(e):
                return (False, f"FAILED - .NET SDK not found. Please install .NET SDK: https://dotnet.microsoft.com/download")
            else:
                return (False, f"FAILED - Error: {str(e)}")
        except Exception as e:
            return (False, f"ERROR - {str(e)}")
    
    def grade_csharp_submission(self, extraction_path, username):
        """
        Grade a C# submission.
        
        Args:
            extraction_path (str): Path to the extracted files
            username (str): Name of the student
            
        Returns:
            list or str: Test results or status code
        """
        return self.grade_submission(extraction_path, username, 'csharp')
    
    def run(self):
        """
        Run the complete submission check process.
        """
        # Create time tracker file if it doesn't exist
        tracker_file = os.path.join(self.output_dir, "time_tracker.txt")
        
        # Record start time
        start_time = time.time()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append start time to tracker file
        with open(tracker_file, 'a') as f:
            f.write(f"\n=== Correctness Check Started: {timestamp} ===\n")
        
        # Run the actual processing
        self.process_csv()
        self.print_results()
        generate_results_html(self.TEST_NAMES,self.results,output_path=os.path.join(self.output_dir, "results.html"))
        
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
            f.write(f"=== Correctness Check Completed: {end_timestamp} ===\n")
            f.write(f"=== Total Duration: {duration_formatted} ({duration:.2f} seconds) ===\n")
        
        print(f"Correctness checks completed. Total duration: {duration_formatted}")


def main():
    """
    Main function to run the submission checker.
    """
    checker = SubmissionChecker()
    checker.run()


if __name__ == "__main__":
    main()
