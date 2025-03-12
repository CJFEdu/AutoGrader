#!/usr/bin/env python3

import os
import re
import shutil
from config import Config

# Constants
ASSIGNMENT_NAME = "PA1"
TEST_FILE_NAME = "TestCorrectness"
MAIN_TEST_FOLDER = "full_test"
INPUT_DIR = "input"
OUTPUT_DIR = "output"

def reload_test_files():
    """
    Iterates over all the submission folders and copies the appropriate test files
    based on the file type detected in each submission.
    """
    # Get the absolute path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, INPUT_DIR)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    submissions_path = os.path.join(output_dir, "submissions")
    
    # Create necessary directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(submissions_path, exist_ok=True)
    
    # Check if submissions directory exists
    if not os.path.exists(submissions_path):
        print(f"Error: Submissions directory not found at {submissions_path}")
        return
    
    # Get all submission directories
    submission_dirs = [d for d in os.listdir(submissions_path) 
                       if os.path.isdir(os.path.join(submissions_path, d))]
    
    print(f"Found {len(submission_dirs)} submission directories")
    
    # Process each submission directory
    for username in submission_dirs:
        process_submission_directory(script_dir, input_dir, submissions_path, username)

def process_submission_directory(script_dir, input_dir, submissions_path, username):
    """
    Process a single submission directory.
    
    Args:
        script_dir (str): Path to the script directory
        input_dir (str): Path to the input directory
        submissions_path (str): Path to the submissions directory
        username (str): Username of the student
    """
    extraction_path = os.path.join(submissions_path, username)
    print(f"Processing submission directory for {username}")
    
    # Check if temp_test directory exists, create if not
    temp_test_dir = os.path.join(extraction_path, "temp_test")
    os.makedirs(temp_test_dir, exist_ok=True)
    
    # Detect file type
    file_types = detect_file_types(extraction_path)
    
    if not file_types:
        print(f"No recognized file types found for {username}")
        return
    
    print(f"Detected file types for {username}: {file_types}")
    
    # Process based on file type
    for file_type in file_types:
        if file_type == '.h':  # C++
            process_cpp_files(script_dir, input_dir, extraction_path, temp_test_dir, username)
        elif file_type == '.java':  # Java
            process_java_files(script_dir, input_dir, extraction_path, temp_test_dir, username)
        elif file_type == '.cs':  # C#
            process_csharp_files(script_dir, input_dir, extraction_path, temp_test_dir, username)

def detect_file_types(extraction_path):
    """
    Detect file types in the extraction path.
    
    Args:
        extraction_path (str): Path to the extracted submission
        
    Returns:
        list: List of detected file extensions (.java, .cs, .h)
    """
    file_types = set()
    
    # Walk through the directory
    for root, _, files in os.walk(extraction_path):
        for file in files:
            if any(file.startswith(req_file) for req_file in Config.REQUIRED_FILE_NAMES):
                _, ext = os.path.splitext(file)
                if ext in ['.java', '.cs', '.h']:
                    file_types.add(ext)
    
    return list(file_types)

def find_implementation_files(extraction_path, extension):
    """
    Find implementation files in the extraction path.
    
    Args:
        extraction_path (str): Path to the extracted submission
        extension (str): File extension to look for
        
    Returns:
        dict: Dictionary of found files mapping filename to file path
    """
    found_files = {}
    
    # Get all the required files
    required_files = [f"{file_name}{extension}" for file_name in Config.REQUIRED_FILE_NAMES]
    
    # Walk through the directory
    for root, _, files in os.walk(extraction_path):
        for file in files:
            if file in required_files and file not in found_files:
                found_files[file] = os.path.join(root, file)
    
    return found_files

def copy_test_files(test_dir, test_file, test_temp_dir, found_files, extraction_path):
    """
    Copy test files, student implementation files, and provided files to the test directory.
    
    Args:
        test_dir (str): Directory containing the test files
        test_file (str): Name of the test file to copy
        test_temp_dir (str): Temporary directory to copy files to
        found_files (dict): Dictionary of found student implementation files
        extraction_path (str): Path to the extracted submission
    """
    # Copy the test file
    source_file = os.path.join(test_dir, test_file)
    
    # If test_file has a number in it, remove the number for dest_test_file
    dest_file_name = re.sub(fr'({TEST_FILE_NAME})\d+(\.\w+)', r'\1\2', test_file)
    dest_test_file = os.path.join(test_temp_dir, dest_file_name)
    
    if os.path.exists(source_file):
        # Copy to the destination with the modified file name
        shutil.copy(source_file, dest_test_file)
        print(f"Copied test file: {source_file} -> {dest_test_file}")

    # Copy all found student implementation files to temp directory
    # for file, file_path in found_files.items():
    #     # Copy the file to the temp directory
    #     temp_file_path = os.path.join(test_temp_dir, file)
    #     shutil.copy2(file_path, temp_file_path)
    #     print(f"Copied implementation file: {file_path} -> {temp_file_path}")
    
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
            print(f"Skipping provided file: {provided_file}")
            continue
        
        source_file = os.path.join(test_dir, provided_file_with_ext)
        dest_file = os.path.join(test_temp_dir, provided_file_with_ext)
        if os.path.exists(source_file):
            shutil.copy(source_file, test_temp_dir)
            print(f"Copied provided file: {source_file} -> {test_temp_dir}")

def process_cpp_files(script_dir, input_dir, extraction_path, temp_test_dir, username):
    """
    Process CPP files for a submission.
    
    Args:
        script_dir (str): Path to the script directory
        input_dir (str): Path to the input directory
        extraction_path (str): Path to the extracted submission
        temp_test_dir (str): Path to the temporary test directory
        username (str): Username of the student
    """
    # Get test files directory
    test_dir = os.path.join(input_dir, f"{ASSIGNMENT_NAME}/CPP")
    
    # Find all CPP implementation files
    found_files = find_implementation_files(extraction_path, '.h')
    
    # Create test directories
    for i in range(1, 8):
        test_temp_dir = os.path.join(temp_test_dir, f"test_{i}")
        os.makedirs(test_temp_dir, exist_ok=True)
        
        # Copy test files to the test directory
        test_file = f"{TEST_FILE_NAME}{i}.cpp"
        copy_test_files(test_dir, test_file, test_temp_dir, found_files, extraction_path)
    
    # Create full test directory
    full_test_dir = os.path.join(temp_test_dir, MAIN_TEST_FOLDER)
    os.makedirs(full_test_dir, exist_ok=True)
    
    # Copy test files to the full test directory
    test_file = f"{TEST_FILE_NAME}.cpp"
    copy_test_files(test_dir, test_file, full_test_dir, found_files, extraction_path)

def process_java_files(script_dir, input_dir, extraction_path, temp_test_dir, username):
    """
    Process Java files for a submission.
    
    Args:
        script_dir (str): Path to the script directory
        input_dir (str): Path to the input directory
        extraction_path (str): Path to the extracted submission
        temp_test_dir (str): Path to the temporary test directory
        username (str): Username of the student
    """
    # Get test files directory
    test_dir = os.path.join(input_dir, f"{ASSIGNMENT_NAME}/JAVA")
    
    # Find all Java implementation files
    found_files = find_implementation_files(extraction_path, '.java')
    
    # Create test directories
    for i in range(1, 8):
        test_temp_dir = os.path.join(temp_test_dir, f"test_{i}")
        os.makedirs(test_temp_dir, exist_ok=True)
        
        # Copy test files to the test directory
        test_file = f"{TEST_FILE_NAME}{i}.java"
        copy_test_files(test_dir, test_file, test_temp_dir, found_files, extraction_path)
    
    # Create full test directory
    full_test_dir = os.path.join(temp_test_dir, MAIN_TEST_FOLDER)
    os.makedirs(full_test_dir, exist_ok=True)
    
    # Copy test files to the full test directory
    test_file = f"{TEST_FILE_NAME}.java"
    copy_test_files(test_dir, test_file, full_test_dir, found_files, extraction_path)

def process_csharp_files(script_dir, input_dir, extraction_path, temp_test_dir, username):
    """
    Process C# files for a submission.
    
    Args:
        script_dir (str): Path to the script directory
        input_dir (str): Path to the input directory
        extraction_path (str): Path to the extracted submission
        temp_test_dir (str): Path to the temporary test directory
        username (str): Username of the student
    """
    # Get test files directory
    test_dir = os.path.join(input_dir, f"{ASSIGNMENT_NAME}/C#")
    
    # Find all C# implementation files
    found_files = find_implementation_files(extraction_path, '.cs')
    
    # Create test directories
    for i in range(1, 8):
        test_temp_dir = os.path.join(temp_test_dir, f"test_{i}")
        os.makedirs(test_temp_dir, exist_ok=True)
        
        # Copy test files to the test directory
        test_file = f"{TEST_FILE_NAME}{i}.cs"
        copy_test_files(test_dir, test_file, test_temp_dir, found_files, extraction_path)
    
    # Create full test directory
    full_test_dir = os.path.join(temp_test_dir, MAIN_TEST_FOLDER)
    os.makedirs(full_test_dir, exist_ok=True)
    
    # Copy test files to the full test directory
    test_file = f"{TEST_FILE_NAME}.cs"
    copy_test_files(test_dir, test_file, full_test_dir, found_files, extraction_path)

if __name__ == "__main__":
    reload_test_files()
