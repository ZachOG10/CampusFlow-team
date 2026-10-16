# CampusFlow Baseline Check

# Baseline Version: Before Today's Improvements

## Date: 14th October, 2026

## Purpose:
This baseline check records the condition of the CampusFlow application
before implementing today's improvements. It provides a reference point
for comparing the application's behavior before and after the changes.

### Unit Test Verification

## Command executed:

python3 -m unittest discover -s tests -v

## Expected baseline result:
- 29 tests passed.

## Actual baseline test Results:
- Total Tests Run: 29
- Passed: 29
- Failed: 0

## Features Covered by the Existing Implementation:
- Ticket creation and input validation.
- Ticket priority calculation.
- Ticket assignment and reassignment.
- Ticket status updates and reopening.
- Work queue generation and priority sorting.
- Ticket reporting by status and priority.
- JSON-based ticket storage and loading.
- Ticket ID generation using existing ticket records.

## Baseline Status:
The existing version serves as the reference point for today's
improvements. The unit test results will be compared with the results
obtained after implementing the new changes.

## Manual Inputs Tested
To verify the starting behavior of the old application before making changes, the following three test inputs were manually tried:
1. Valid Ticket Creation: created a high-urgency ticket with 10 affected users and verified it correctly calculated priority as `critical`.
2. Status Transition: The previous version already handled this filed graciously.
3. Edge Case / Invalid Input: Entered an invalid string for affected users and empty spaces without selecting an option or inserting the required input to observe how the legacy application handled non-numeric values.

## Audit Observations & Improvement Focus
According to the preliminary peer feedback from the audit band, the following areas were flagged for improvement:
- Missing Feature: Absence of error notes immediately a user entered an invalid input or an empty space instead of waiting for them to enter other fileds before catching a previous error message
which will be included in the enhanced version.