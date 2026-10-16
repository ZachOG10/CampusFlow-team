# CampusFlow — Campus Technical Support Ticket Manager

## About the Project

CampusFlow is a Python-based command line application designed to help campus technical support teams manage technical support requests efficiently.
The application allows users to create support tickets, calculate their priority, add notes, assign tickets to staff members, track their progress, organize a work queue, generate reports, and save ticket records for future use.
Common problems managed by CampusFlow include Wi-Fi is down, broken laptops, software issues, and inaccessible development platforms.

This project was developed as part of an engineering sprint to demonstrate problem-solving, modular programming, workflow management, data persistence, automated testing, and collaborative software development.

## Project Objectives
The main objectives of CampusFlow are to:

- Record technical support requests in a structured format with rigorous validation.

- Generate unique identifiers for tickets (`T001`, etc.) and notes (`N001`, etc.).

- Calculate ticket priority based on urgency and the number of affected users.

- Add validated notes to open tickets to track collaborative troubleshooting.

- Assign tickets to responsible staff members.

- Track ticket progress through defined statuses.

- Organize open tickets by priority.

- Generate reports showing ticket statistics.

- Save ticket information using JSON persistence.

- Load previously saved tickets when the application starts.

- Validate user input and handle errors appropriately.

- Apply software engineering practices, including unit testing and version control.

## Features

## 1. Ticket Creation and Validation

Users can create support tickets by providing:

- Ticket title (non-empty string validation)

- Ticket category (Network, Hardware, Software, Other)

- Urgency level (low, medium, high)

- Number of affected users (positive integer validation, safeguarding against boolean subclasses)

Each ticket receives a unique ticket ID.

### 2. Automatic Priority Calculation

CampusFlow calculates ticket priority using the urgency level and the number of affected users.

The supported priority levels are:

# Critical

# High

# Medium

# Low
This helps support teams identify and prioritize important issues.

## 3. Ticket Notes Logic

Users can add timestamped notes to open tickets with strict author and message length validation (5 to 300 characters). 
Notes use independent sequential IDs starting with an `N` prefix (`N001`), and failed validations do not consume ID counters. Notes cannot be added to resolved tickets.

### 4. Ticket Assignment and Reassignment

Tickets can be assigned to staff members responsible for resolving reported problems.
Existing assignments can also be changed when responsibility needs to be transferred.

### 5. Ticket Status Management

CampusFlow supports three ticket statuses:

- open — The ticket has been created and is awaiting work.

- in_progress — A staff member is working on the ticket.

- resolved — The reported issue has been resolved.

Resolved tickets can be reopened when further work is required.

### 6. Priority-Based Work Queue
The work queue organizes open tickets according to priority.
Tickets are arranged in the following order:

1. Critical
2. High
3. Medium
4. Low
When tickets have the same priority, their numeric ticket IDs determine their order.

### 7. Ticket Reports
The reporting feature summarizes ticket information, including:

- Total number of tickets

- Number of open tickets

- Number of in-progress tickets

- Number of resolved tickets

- Priority breakdowns (Critical, High, Medium, Low)

These reports help users understand the current state of the support workload.

### 8. JSON Data Persistence

CampusFlow stores ticket records in JSON format.

The application loads previously saved tickets when it starts and saves ticket changes so that records remain available after the application closes.
If the data file does not exist, the application starts with an empty collection of tickets.

### 9. Input Validation and Error Handling
The application validates ticket and note information to reduce invalid entries, handles invalid menu selections, and reports problems encountered when loading saved JSON data.

### 10. Automated Testing
CampusFlow uses Python's built-in `unittest` framework to test application functionality across dedicated test modules, ensuring high code reliability.

## Technologies Used
- **Python 3:** Main programming language.

- **JSON:** Format for storing ticket records.

- **unittest:** Framework for automated testing.

- **Git:** Version control system.

- **GitHub:** Platform for collaborative development and code hosting.

- **Visual Studio Code:** Development environment.


## Project Structure

```text
CampusFlow-team/
│
├── main.py
│
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   ├── notes.py
│   ├── workflow.py
│   ├── storage.py
│   └── reports.py
│
├── tests/
│   ├── __init__.py
│   ├── test_tickets.py
│   ├── test_notes.py
│   ├── test_workflow.py
│   ├── test_storage.py
│   ├── test_reports.py
│   └── test_storage_persistence.py
│
├── data/
│   └── tickets.json
│
├── docs/
│
├── .gitignore
└── README.md