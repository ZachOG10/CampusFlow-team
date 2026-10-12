# CampusFlow — Design Decisions

## 1. Overview

CampusFlow is a Python command-line ticket management system designed to help
Learn2Earn campus staff record, organize, assign, and track technical support
requests.

The system addresses problems caused by informal support requests, such as
lost reports, unclear responsibilities, difficulty prioritizing tasks, and
poor visibility into unresolved issues.

The application allows users to create support tickets, assign responsibility,
update ticket statuses, view work queues, and generate reports.

The project was developed as part of the AI-Native Engineering Sprint, with
an emphasis on modular design, separation of concerns, data persistence,
validation, testing, and collaborative software development.

## 2. Design Goals

The main design goals were:

- Make the application simple to operate through a command-line interface.
- Organize the code into modules with clearly defined responsibilities.
- Validate user input to reduce invalid or inconsistent ticket data.
- Support ticket assignment and status tracking.
- Make it possible to review outstanding work and ticket summaries.
- Preserve ticket data between program executions using JSON persistence.
- Make individual components easier to test and maintain.
- Support collaborative development by dividing responsibilities between
  two engineers.
- Use automated tests to verify expected behavior and identify regressions.

## 3. Modular Architecture

### Decision

The application was divided into separate Python modules based on
their responsibilities.

The project structure includes:

- `main.py`
- `campusflow/tickets.py`
- `campusflow/workflow.py`
- `campusflow/storage.py`
- `campusflow/reports.py`
- `tests/`
- `docs/`

### Rationale

Keeping the entire application in one file would make the code harder to
understand, test, debug, and extend as additional features were introduced.

Separating responsibilities into modules makes the codebase easier to
navigate and allows individual components to be developed and tested
independently.

### Responsibilities

**`main.py`**

Provides the application's entry point and coordinates the command-line
interaction with the underlying application logic.

**`campusflow/tickets.py`**

Handles ticket creation and the validation of ticket information, including
the fields required to represent a support request.

**`campusflow/workflow.py`**

Handles ticket workflow operations, including assignment, status updates,
and work queue management.

**`campusflow/storage.py`**

Handles saving ticket data to JSON and loading previously saved data.

**`campusflow/reports.py`**

Provides reporting functionality to help users understand the state of
support requests and outstanding work.

**`tests/`**

Contains automated tests used to verify ticket creation, workflow operations,
storage behavior, and other implemented functionality.

### Trade-off

A modular architecture introduces more files and requires the modules to
interact through clearly defined interfaces.

However, this additional organization improves maintainability, testability,
and the ability to extend the application.

## 4. Ticket Data Representation

### Decision

Tickets are represented using dictionaries, with each ticket containing
the fields needed to describe and manage a support request.

### Rationale

A dictionary provides named fields, making ticket information easier to read
and access than a list of positional values.

For example, named fields allow the application to distinguish a ticket's
identifier, title, description, priority, status, and assignment information.

This representation also makes it easier to serialize ticket data into JSON.

### Trade-off

Dictionaries are flexible, but they do not automatically enforce a fixed
schema or prevent unexpected keys and invalid values.

Therefore, validation is important to maintain consistent ticket records.

## 5. Ticket Validation

### Decision

Ticket information is validated before invalid data is accepted into the
application's workflow.

### Rationale

Support tickets must contain meaningful and consistent information to be
useful.

Without validation, tickets could contain missing required fields, invalid
priorities, or values that do not match the application's expectations.

Validation helps prevent these problems and makes the system more reliable.

### Trade-off

Validation introduces additional logic and requires the application to
define which values are acceptable.

However, rejecting invalid information early reduces the risk of errors
during assignment, status updates, reporting, and persistence.

## 6. Ticket Assignment and Status Management

### Decision

Workflow operations are separated from ticket creation.

Assignment, status updates, and work queue operations are handled by the
workflow module.

### Rationale

Creating a ticket and managing its progress are different responsibilities.

Ticket creation establishes a support request, while workflow operations
determine who is responsible for it and how its status changes over time.

Separating these responsibilities makes the system easier to understand
and allows workflow behavior to be tested independently.

### Trade-off

Separating workflow logic from ticket creation requires the modules to
share ticket data through defined interfaces.

This is preferable to placing all operations in one large function or module.

## 7. JSON Persistence

### Decision

JSON is used to store ticket data between program executions.

The storage module is responsible for reading and writing the persisted data.

### Rationale

Without persistence, tickets stored only in memory would be lost when the
program terminates.

JSON provides a human-readable format for storing structured data and is
supported by Python's standard library.

It is suitable for a small command-line application that does not require
a database server.

### Trade-off

JSON is simple to implement and inspect, but it is not designed for
concurrent database transactions or large-scale multi-user workloads.

As the application grows, a database such as SQLite or PostgreSQL could
provide stronger data management capabilities.

## 8. Separation of Storage and Application Logic

### Decision

File operations are kept in the storage module rather than being duplicated
throughout the application.

### Rationale

Centralizing persistence logic provides a consistent way to save and load
tickets.

It also makes storage behavior easier to test without requiring every
application component to implement its own file operations.

This separation reduces duplication and makes future storage changes easier.

### Trade-off

Other modules must use the storage interface instead of directly managing
the persistence file.

This introduces a dependency on the storage module but improves consistency
and maintainability.

## 9. Reporting

### Decision

Reporting functionality is separated into its own module.

### Rationale

Reports help users understand the overall state of the support system without
requiring them to inspect every ticket individually.

Keeping reporting separate from workflow operations allows the application
to organize ticket information for summaries without mixing reporting logic
with assignment and status-management logic.

### Trade-off

A separate reporting module introduces another component to maintain.

However, it provides a clear location for future reporting features and
makes report behavior easier to test independently.

## 10. Command-Line Interface

### Decision

A command-line interface is used for user interaction.

### Rationale

The project is a time-limited engineering challenge focused on demonstrating
programming fundamentals, application architecture, data management, and
testing.

A command-line interface allows these core requirements to be implemented
without the additional complexity of a graphical interface or web framework.

It also makes the application straightforward to run in a development
environment.

### Trade-off

The application does not provide the visual experience or accessibility
features that a dedicated graphical or web interface could offer.

However, the command-line interface keeps the project focused on its core
ticket-management functionality.

## 11. Automated Testing

### Decision

Python's `unittest` framework is used to test the application.

Tests are organized around the project's major components and behaviors.

### Rationale

Automated tests help verify that the application behaves as expected and
that changes do not unintentionally break existing functionality.

Testing individual components also helps identify whether a problem
originates in ticket handling, workflow management, storage, or reporting.

Persistence tests are particularly important because they verify that ticket
data can be saved and recovered rather than existing only in memory.

### Trade-off

Writing and maintaining tests requires additional development time.

However, automated testing improves confidence in the application and
makes future modifications safer.

### Verification

The project uses Python's standard testing tools to execute the test suite.

Tests should be run after significant changes and before submitting the
application.

Test results should be recorded accurately in the project's verification
notes. A successful test run means the tests that were discovered and
executed passed; it does not automatically prove that every possible
application behavior is correct.

## 12. Error Handling and Reliability

### Decision

The application should validate inputs and handle expected operational
errors at appropriate boundaries.

### Rationale

Users may provide invalid values, request operations involving nonexistent
tickets, or encounter file-related problems when loading or saving data.

Handling these situations deliberately makes the application easier to
use and prevents avoidable failures.

### Trade-off

Error handling introduces additional branches and requires decisions about
which errors should be rejected, reported, or recovered from.

The goal is to handle expected failures clearly without hiding unexpected
programming errors.

## 13. Collaborative Development

### Decision

Development responsibilities were divided between two engineers, with
different components assigned to each person.

The project uses Git branches to organize changes and GitHub to host the
shared repository.

### Rationale

Dividing responsibilities allows both engineers to work on different parts
of the application while reducing unnecessary overlap.

Separating the work into modules also supports parallel development because
each engineer can focus on a defined area of responsibility.

Version control provides a record of changes and a way to integrate
contributions.

### Trade-off

Parallel development requires coordination around module interfaces,
shared data structures, function behavior, and testing expectations.

Changes to shared interfaces may require additional communication and
integration testing.

## 14. Scope and Limitations

### Decision

The project focuses on a small, local command-line ticket management system.

It does not attempt to provide a complete enterprise help-desk platform.

### Rationale

The project was developed within a limited engineering sprint.

Prioritizing ticket creation, validation, workflow management, persistence,
reporting, and automated testing makes it possible to demonstrate important
software engineering principles within the available time.

### Limitations

Depending on the implemented behavior, the system may have limitations such
as:

- No graphical or web-based interface.
- No centralized database server.
- No built-in authentication or role-based access control.
- Limited support for concurrent users.
- No automatic email or messaging notifications.
- Limited scalability compared with a production help-desk platform.

These limitations define the current scope rather than implying that the
application is intended to support every enterprise requirement.

## 15. Future Improvements

Possible future improvements include:

- Introducing a database for more robust data management.
- Adding user authentication and role-based permissions.
- Providing a graphical or web-based interface.
- Adding search and filtering capabilities.
- Expanding reporting and analytics.
- Improving recovery from corrupted or inaccessible storage files.
- Adding more comprehensive integration tests.
- Supporting concurrent users and shared access to tickets.

These improvements could be introduced incrementally as the application
evolves.

## 16. Conclusion

CampusFlow was designed around modularity, clear responsibilities,
validation, persistence, and automated testing.

The separation of ticket handling, workflow operations, storage, and reporting
helps keep the codebase understandable and maintainable.

Using JSON provides a lightweight persistence mechanism, while automated
tests help verify important application behaviors.

Together, these decisions provide a foundation for a small but structured
ticket management system and demonstrate practical software engineering
principles.