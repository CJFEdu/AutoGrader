# Autograder Implementation Documentation

## Implementation Steps

### Step 1: Project Setup
- Create the `input` directory to store student submissions and test cases

### Step 2: Copy files
 - Copy PA zip file and submissions zip file to `input` directory
 - Extract PA zip file to folder of same name i.e. `PA4`

### Step 3: File Prep
 - Copy expected output to txt file
 - Add CSV file to `input` directory and update test names

### Step 4: Update config.py
 - Update config.py with TEST_HEADERS from expected output
 - Update config.py ASSIGNMENT_NAME with the name of the assignment
 - Update config.py REQUIRED_FILE_NAMES with the names of the files submitted by the students
 - Update config.py PROVIDED_FILE_NAMES with the names of the files provided by the instructor
 - Update config.py RESOURCE_FILE_NAMES with the names of the resource files
 
### Step 5: Run the File Prep Script
 - Run the file_prep.py script
 
### Step 6: Update TestCorrectness files
 - file_prep.py creates copies of TestCorrectness files for each language and each test
 - Go into each new TestCorrectness file and comment out the other tests

### Step 7: Update Time Test
 - At the bottom of the TestTime files and a printout to check for file completion
 - Add that line to to the config.py TIME_CHECK_STRINGS