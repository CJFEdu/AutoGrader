#!/usr/bin/env python3

class Config:
    """
    Configuration class for assignment settings.
    """
    CLASS_NAME = "CompSci 233"
    SECTION = "Section 001"
    ASSIGNMENT_NAME = "PA2"
    REQUIRED_FILE_NAMES = ["BinarySearchApplications", "LinkedList", "DynamicArray"]
    PROVIDED_FILE_NAMES = ["ListNode"]
    OUTPUT_FILE_NAME = "ExpectedOutput.txt"
    TEST_HEADERS = [
        "****************** Finding Predecessor ******************",
        "****************** Test Linked List Correctness ******************",
        "****************** Test Dynamic Array Correctness ******************"
    ]
    SEARCH_PATTERN_USE_FIRST_NAME_FIRST = True
    CLEAN_START = False
    TIME_CHECK_STRINGS = ["End Test Time"]    
    IGNORE_NAMES = []

