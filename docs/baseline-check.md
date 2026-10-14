## ENGINEER A - OWOICHO FAITH
# CampusFlow Next — Baseline Check

## 1. Test command

`python3 -m unittest discover -s tests -v`

## 2. Test results

- Total tests: 29
- Passed: 29
- Failed: 0
- Errors: 0

## 3. Baseline observations

- Ticket creation and input validation tests passed.
- Assignment and status transition tests passed.
- Report generation and non-mutation tests passed.
- JSON storage and persistence tests passed.
- Further reliability testing is needed to identify scenarios not covered by the existing tests.


## ENGINEER B - OMALE MOSES

## Run command: 
python3 main.py

## Inputs on main.py:

## Input 1: To create a ticket with high urgency + 12 users

Title: Wi-fi down in ICT
Category: network (I entered it in lowercase)
Urgency: high
Affected users: 12

Observations:
ID T001 assigned
My lowercase category was normalised to Network 
Priority = critical which is correct (high urgency AND ≥10 users) 
Status open, assigned_to: None 


## Input 2: Create ticket with invalid affected_users
Title: Mouse in cluster four is tweaking
Category: Hardware
Urgency: low
Affected users: -3
Observations:
rejected with Please enter a number greater than zero. and re-prompted. No ticket created, collection unchanged and negative integer correctly rejected.

## Input 3: Attempt to move an unassigned ticket to in_progress
Ticket: T001 (open, assigned_to: None)

From the menu, I selected: Update status and picked 1 (In progress)

Observation: 
rejected with Cannot start an unassigned ticket. matching Requirement A ("Do not let an unassigned open ticket move to in_progress"). Data remain unchanged.