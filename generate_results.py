#!/usr/bin/env python3

import os
from typing import List
from config import Config
from results import Results, Student, Test

class HTMLGenerator:
    def __init__(self, test_names: List[str], results: Results):
        self.test_names = test_names
        self.results = results
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def read_template(self, filename: str) -> str:
        """Read template file content."""
        file_path = os.path.join(self.script_dir, filename)
        with open(file_path, 'r') as f:
            return f.read()
            
    def generate_student_row(self, student: Student) -> str:
        """Generate HTML for a single student row."""
        # If no tests, show simplified "Not submitted" row
        if not student.tests:
            return f"""
    <div class="row">
        <div class="left-content">
            <span style="margin-left: 70px">{student.first_name} {student.last_name}</span>
            <span class="status">Not submitted</span>
        </div>
    </div>"""
            
        # Count passed and failed tests
        passed_count = sum(1 for test in student.tests if test.passed)
        failed_count = len(student.tests) - passed_count
        
        # Generate status text
        status_parts = []
        if failed_count > 0:
            status_parts.append(f'<span class="status-failed">{failed_count} failed</span>')
        if passed_count > 0:
            status_parts.append(f'<span class="status-passed">{passed_count} passed</span>')
        if student.full_output_passed:
            status_parts.append(f'<span class="status-passed">Full output passed</span>')
        if not student.full_output_passed:
            status_parts.append(f'<span class="status-failed">Full output failed</span>')
        status_text = ", ".join(status_parts) if status_parts else "Not submitted"
        
        # Generate the main row content
        student_id = student.username.replace(" ", "_").lower()
        row = f"""
    <div class="row">
        <div class="left-content">
            <button class="button" onclick="copyToClipboard('{student_id}-content')">
                📋
            </button>
            <button class="button" onclick="toggleExpand('{student_id}-expanded')">
                ▶
            </button>
            <span>{student.first_name} {student.last_name}</span>
            <span style="margin: 0 20px">{student.file_type}</span>
            <span class="status">{status_text}</span>
            <div id="{student_id}-content" class="hidden">{self.student_correlated_output(student)}</div>
        </div>
    </div>
    
    <div id="{student_id}-expanded" class="expanded-content hidden">
        {self.generate_expanded_content(student)}
    </div>
"""
        return row
        
    def student_correlated_output(self, student: Student) -> str:
        """Generate student correlated output."""
        lines = []
        for test in student.tests:
            lines.append(f"{test.output}")
        return "".join(lines)
            
    def generate_expanded_content(self, student: Student) -> str:
        """Generate expanded content showing test details."""
        content = []
        
        # Add file types if present
        content.append(f"""
        <div class="row">
            <div class="left-content">Notes: </div>
        </div>""")
            
        content.append(f"""
        <div class="row">
            <div class="left-content">Unedited Output: </div>""")
        content.append(f"""<button class="button" onclick="copyToClipboard('{student.username}-full_output')">
            📋
        </button>""")
        content.append(f"""<div id="{student.username}-full_output" class="hidden">\n""")
        content.append(f"""{student.full_output}""")
        content.append(f"""</div></div>""")
            
        # Add each test's details
        for i, test in enumerate(student.tests):
            test_id = f"{student.username}-test{i+1}".replace(" ", "_").lower()
            status_class = "status-passed" if test.passed else "status-failed"
            status_text = "Passed" if test.passed else "Failed"
            
            content.append(f"""
        <div class="row">
            <div class="left-content">""")
            if not test.passed:
                content.append(f"""<button class="button" onclick="copyToClipboard('{test_id}-output')">
                    📋
                </button>""")
            content.append(f"""<button class="button" onclick="toggleExpand('{test_id}-output')">
                    ▶
                </button>
                <span>{test.name}</span>
                <span class="status {status_class}">{status_text}</span>
            </div>
        </div>
        <div id="{test_id}-output" class="test-output hidden">{test.output}</div>""")
            
        return "\n".join(content)
        
    def generate_html(self) -> str:
        """Generate the complete HTML content."""
        # Read templates
        top_template = self.read_template("results_html_top.txt")
        bottom_template = self.read_template("results_html_bottom.txt")
        
        # Add headers
        html_content = top_template
        html_content += f"""
    <div class="headers">
        <h1>{Config.CLASS_NAME}</h1>
        <h2>{Config.ASSIGNMENT_NAME}</h2>
        <h3>Section {Config.SECTION}</h3>
    </div>
"""
        
        # Generate rows for each student
        rows = []
        for username, student in self.results.students.items():
            rows.append(self.generate_student_row(student))
        
        # Combine all parts
        html_content += "\n".join(rows)
        html_content += bottom_template
        
        return html_content
        
    def save_html(self, output_path: str):
        """Save the generated HTML to a file."""
        html_content = self.generate_html()
        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"Results HTML saved to: {output_path}")

def generate_results_html(test_names: List[str], results: Results, output_path: str):
    """
    Generate an HTML results file from the given test names and results.
    
    Args:
        test_names: List of test names
        results: Results object containing student data
        output_path: Path where the HTML file should be saved
    """
    generator = HTMLGenerator(test_names, results)
    generator.save_html(output_path)

if __name__ == "__main__":
    print("Starting script...")
    
    from results import Results, Student, Test
    
    print("Creating sample results...")
    results = Results(["Test 1", "Test 2"])
    
    print("Adding students...")
    student1 = Student("John", "Smith", "jsmith")
    student1.file_types = ".java, .class"
    student1.tests = [
        Test("Test 1", True, "All test cases passed successfully"),
        Test("Test 2", False, "Expected: [1, 2, 3]\nActual: [3, 2, 1]")
    ]
    student1.full_output = "Full output for student 1"
    results.add_student(student1)

    student2 = Student("Jane", "Doe", "jdoe")
    student2.tests = []
    results.add_student(student2)
    
    print("Generating HTML...")
    generate_results_html(
        test_names=["Test 1", "Test 2"],
        results=results,
        output_path="results.html"
    )
    print("Script completed.")
