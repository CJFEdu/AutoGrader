#!/usr/bin/env python3

class Config:
    """
    Configuration class for assignment settings.
    """
    CLASS_NAME = "CompSci 433"
    SECTION = "Section 001"

    ASSIGNMENT_NAME = "PA3"
    REQUIRED_FILE_NAMES = ["Knapsack01", "LIS", "LCS", "MWIS", "MWVC"]
    PROVIDED_FILE_NAMES = ["SubsetSum","Tree", "VankinsMile"]
    RESOURCE_FILE_NAMES = ["mis1.txt", "mis2.txt", "mis3.txt", "mis4.txt"]
    OUTPUT_FILE_NAME = "ExpectedOutput.txt"

    TEST_HEADERS = [
        "****************** Subset Sum ******************",
        "****************** 0-1 Knapsack ******************",
        "****************** Longest Increasing Subsequence ******************",
        "****************** Longest Common Subsequence ******************",
        "****************** Maximum Weighted Independent Set ******************",
        "****************** Minimum Weighted Vertex Cover ******************",
        "****************** Test Vankin's Mile ******************"
    ]
    SEARCH_PATTERN_USE_FIRST_NAME_FIRST = False
    CLEAN_START = False
    TIME_CHECK_STRINGS = ["End Test Time"]    
    IGNORE_NAMES = []
    TIMEOUT = 10

