#!/usr/bin/env python3

class Config:
    """
    Configuration class for assignment settings.
    """
    CLASS_NAME = "CompSci 233"
    SECTION = "Section 001"
    ASSIGNMENT_NAME = "PA1"
    REQUIRED_FILE_NAMES = ["MedianOfMedians", "Partition", "QuickSort", "RadixSort", "Selection"]
    PROVIDED_FILE_NAMES = ["ClosestPairOfPoints", "GenericMergeSort", "IntegerComparator",
        "InversionCounting", "MergeSort", "Point", "PointComparator"]
    OUTPUT_FILE_NAME = "ExpectedOutput.txt"
    TEST_HEADERS = [
        "*** Sorting/Selection Test Without Duplicates ***",
        "****************** Two-Index Partition with Duplicates ******************",
        "****************** Randomized Quick-Sort with Duplicates ******************",
        "****************** Median of 3 Quick-Sort with Duplicates ******************",
        "****************** Radix-sort with Duplicates ******************",
        "****************** Randomized Quick-Select with Duplicates ******************",
        "****************** Median of Medians with Duplicates ******************",
    ]
    SEARCH_PATTERN_USE_FIRST_NAME_FIRST = False
    CLEAN_START = False
    TIME_CHECK_STRINGS = ["points using divide & conquer strategy ="]    
    #TIME_CHECK_STRINGS = ["*** Time Test Sorting ***"]
    IGNORE_NAMES = [
    # #     "pontytony",
    #     "andersonmitchell",
    #     "aroncameron",
    # #     "barbiannathan",
    #     "bruskybella",
    #     "crawfordmatthew",
    #     "desormeaukade",
    #     "eggertcarson",
    #     "eversontrenton",
    #     "fryconnor",
    #     "haggertyfletcher",
    #     "hammbrayden",
    #     "kurtzjack",
    #     "leeashley",
    #     "lomaxnehemiah",
    #     "mauricemichael",
    #     "michaelbrian",
    #     "muthscott",
    #     "neumannjordan",
    #     "nguyentommy",
    #     "nussbailey",
    #     "patelansh"
    ]

