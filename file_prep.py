#!/usr/bin/env python3
import os
import csv
import shutil
import re
from config import Config

class FilePrep:
    """
    A class to prepare test files for each test in the assignment.
    """
    
    def __init__(self, csv_file=f"{Config.ASSIGNMENT_NAME}.csv"):
        """
        Initialize the FilePrep with file paths.
        
        Args:
            csv_file (str): Path to the CSV file containing test names
        """
        # Constants for directory names
        self.INPUT_DIR = "input"
        self.OUTPUT_DIR = "output"
        
        # Get the absolute path to the script's directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(self.script_dir, self.INPUT_DIR)
        self.output_dir = os.path.join(self.script_dir, self.OUTPUT_DIR)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Construct absolute paths
        self.csv_path = os.path.join(self.input_dir, csv_file)
        self.assignment_dir = os.path.join(self.input_dir, Config.ASSIGNMENT_NAME)
        
        # Paths to language directories
        self.java_dir = os.path.join(self.assignment_dir, "JAVA")
        self.cpp_dir = os.path.join(self.assignment_dir, "CPP")
        self.csharp_dir = os.path.join(self.assignment_dir, "C#")
        
        # Path to expected output file
        self.expected_output_path = os.path.join(self.assignment_dir, Config.OUTPUT_FILE_NAME)
        
        # Test names and count
        self.test_names = []
        self.num_tests = 0
    
    def read_test_names(self):
        """
        Read the CSV file to get the test names and count.
        
        Returns:
            list: List of test names
        """
        # Read the CSV file
        with open(self.csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            # Read header row to get test names
            header = next(csv_reader)
            # Get test names from header (columns between the first and 'Language')
            language_index = header.index('Language')
            self.test_names = [name.strip() for name in header[1:language_index]]
            self.num_tests = len(self.test_names)
            
            print(f"Found {self.num_tests} tests: {', '.join(self.test_names)}")
            return self.test_names
    
    def create_test_files(self):
        """
        Create copies of TestCorrectness files for each test.
        """
        # Read test names if not already done
        if not self.test_names:
            self.read_test_names()
        
        # Create test files for Java
        self._create_test_files_for_language(self.java_dir, ".java")
        
        # Create test files for C++
        self._create_test_files_for_language(self.cpp_dir, ".cpp")
        
        # Create test files for C#
        self._create_test_files_for_language(self.csharp_dir, ".cs")
        
        print("Test files creation completed.")
    
    def _create_test_files_for_language(self, language_dir, extension):
        """
        Create test files for a specific language.
        
        Args:
            language_dir (str): Path to the language directory
            extension (str): File extension for the language
        """
        # Check if directory exists
        if not os.path.exists(language_dir):
            print(f"Warning: Directory {language_dir} does not exist.")
            return
        
        # Path to the original test file
        original_file = os.path.join(language_dir, f"TestCorrectness{extension}")
        
        # Check if original file exists
        if not os.path.exists(original_file):
            print(f"Warning: File {original_file} does not exist.")
            return
        
        print(f"Creating test files in {language_dir}...")
        
        # Create a copy for each test
        for i in range(1, self.num_tests + 1):
            new_file = os.path.join(language_dir, f"TestCorrectness{i}{extension}")
            shutil.copy2(original_file, new_file)
            print(f"Created {os.path.basename(new_file)}")

    def split_expected_output(self):
        """
        Split the ExpectedOutput.txt file into separate files for each test based on headers.
        """
        # Check if expected output file exists
        if not os.path.exists(self.expected_output_path):
            print(f"Warning: Expected output file {self.expected_output_path} does not exist.")
            return
        
        print(f"Reading expected output file: {self.expected_output_path}")
        
        # Read the entire file content
        with open(self.expected_output_path, 'r') as file:
            content = file.read()
        
        # Create a list of headers and their positions in the file
        header_positions = []
        for i, header in enumerate(Config.TEST_HEADERS):
            # Escape special regex characters in the header
            escaped_header = re.escape(header)
            # Find the position of the header in the content
            match = re.search(escaped_header, content)
            if match:
                header_positions.append((i, match.start()))
                print(f"Found header {i+1}: {header} at position {match.start()}")
            else:
                print(f"Warning: Header {i+1}: {header} not found in the expected output file.")
        
        # Sort by position in the file
        header_positions.sort(key=lambda x: x[1])
        
        # Create output files for each section
        for i in range(len(header_positions)):
            current_index, current_pos = header_positions[i]
            
            # Determine the end position of this section
            if i < len(header_positions) - 1:
                next_pos = header_positions[i + 1][1]
                section_content = content[current_pos:next_pos]
            else:
                # Last section goes to the end of the file
                section_content = content[current_pos:]
            
            # Create the output file
            output_file = os.path.join(self.assignment_dir, f"expectedoutput{current_index+1}.txt")
            with open(output_file, 'w') as file:
                file.write(section_content)
            
            print(f"Created {os.path.basename(output_file)}")
        
        full_expected_output = os.path.join(self.assignment_dir, "expectedoutput.txt")
        with open(full_expected_output, 'w') as file:
            file.write(content)

def main():
    """
    Main function to run the file preparation.
    """
    file_prep = FilePrep()
    file_prep.create_test_files()
    file_prep.split_expected_output()

if __name__ == "__main__":
    main()
