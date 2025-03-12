#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from check_submissions import SubmissionChecker

class CorrectnessChecker(SubmissionChecker):
    """
    A child class of SubmissionChecker that focuses on checking correctness.
    """
    def __init__(self):
        super().__init__()
        self.TEST_FILE_NAME = "TestCorrectness"
        self.results_path = os.path.join(self.script_dir, "results")
        self.full_output_path = os.path.join(self.script_dir, "full_output")

        print("Initializing Correctness Checker...")
        
        
    def run(self):
        """
        Run the correctness checker.
        """
        print("Running correctness checks...")
        self.process_csv()
        print("Correctness checks completed.")
                
    def grade_cpp_submission(self, extraction_path, student_full_name):
        """
        Override the parent method to handle C++ correctness-based testing.
        """
        print(f"Correctness Checker: Grading C++ submission for {student_full_name}")
        # For now, just call the parent method
        return super().grade_cpp_submission(extraction_path, student_full_name)
        
    def grade_java_submission(self, extraction_path, student_full_name):
        """
        Override the parent method to handle Java correctness-based testing.
        """
        print(f"Correctness Checker: Grading Java submission for {student_full_name}")
        # For now, just call the parent method
        return super().grade_java_submission(extraction_path, student_full_name)
        
    def grade_csharp_submission(self, extraction_path, student_full_name):
        """
        Override the parent method to handle C# correctness-based testing.
        """
        print(f"Correctness Checker: Grading C# submission for {student_full_name}")
        # For now, just call the parent method
        return super().grade_csharp_submission(extraction_path, student_full_name)

def main():
    """
    Main function to run the correctness checker.
    """
    checker = CorrectnessChecker()
    checker.run()

if __name__ == "__main__":
    main()
