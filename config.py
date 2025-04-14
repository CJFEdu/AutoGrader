#!/usr/bin/env python3

class Config:
    """
    Configuration class for assignment settings.
    """
    CLASS_NAME = "CompSci 233"
    SECTION = "Section 001"

    ASSIGNMENT_NAME = "PA4"
    REQUIRED_FILE_NAMES = ["BST", "HashingWithChaining", "HashingWithProbing"]
    PROVIDED_FILE_NAMES = ["BSTNode"]
    OUTPUT_FILE_NAME = "ExpectedOutput.txt"

    TEST_HEADERS = [
        "****************** Hashing with Chaining ******************",
        "****************** Hashing with Probing ******************",
        "****************** BST ******************"
    ]
    SEARCH_PATTERN_USE_FIRST_NAME_FIRST = True
    CLEAN_START = False
    TIME_CHECK_STRINGS = ["End Test Time"]    
    IGNORE_NAMES = []
    TIMEOUT = 10

