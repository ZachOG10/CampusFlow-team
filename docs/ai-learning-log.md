# AI Learning Log — CampusFlow

**Project:** CampusFlow — CLI Ticket Management System
**Contributor:** Aondowase Zachariah 
**Role:** Engineer B — ticket assignment, workflow/status management, queue and reports
**Purpose:** Record how AI was used as a learning and engineering aid during the development of this project.

## Interaction 1 — Understanding the workflow requirements

**Prompt / goal**
I asked for guidance on implementing the ticket workflow feature at a beginner-friendly level.

**AI assistance received**
The guidance broke the workflow into status transitions and highlighted important rules:
- Tickets normally move from `open` to `in_progress`, then to `resolved`.
- An unassigned ticket must not move to `in_progress`.
- A resolved ticket must be explicitly reopened before it can be changed again.
- Invalid transitions should leave the ticket's existing status unchanged.

**What I learned**
I learned to treat ticket status changes as controlled state transitions rather than allowing any status to be assigned at any time.
I also learned why validation should happen before mutating a ticket.

**My contribution / verification**
I used the rules to guide the workflow implementation and considered the expected result for valid and invalid transitions.
I remained responsible for checking that the implementation matched the project requirements.

## Interaction 2 — Organising the workflow module

**Prompt / goal**
I asked whether the ticket assignment feature and the new workflow code should be placed in the same file.

**AI assistance received**
The recommendation was to keep related workflow functions in `campusflow/workflow.py` as separate functions:
- `assign_ticket(tickets)`
- `update_ticket_status(tickets)`
- `reopen_ticket(tickets)`

**What I learned**
A Python module can contain multiple related functions. A separate file is not required for every function; modules should group related responsibilities.

**My contribution / verification**
I kept the assignment and status-management responsibilities organised in the workflow module and treated the main menu as the place that calls the appropriate function.

## Interaction 3 — Creating tests for workflow behaviour

**Prompt / goal**
I asked for an automated test file that would report `OK` when the workflow tests passed.

**AI assistance received**
The suggested tests used Python's `unittest` framework, `unittest.TestCase`, `setUp()` for fresh sample tickets, assertions to check ticket state, and `unittest.mock.patch` to provide simulated input without typing into the terminal.

**What I learned**
Automated tests should check the result of an operation, not merely whether a function printed a message. For example, after an invalid transition, a test should confirm that the ticket's status remains unchanged.

**My contribution / verification**
I ran the test command in the terminal and checked the actual output rather than assuming the suggested test file was working.

## Interaction 4 — Challenging an unverified test result

**Prompt / goal**
After running `python3 -m unittest test -v`, I reported this output:

```text
Ran 0 tests in 0.000s

NO TESTS RAN
```

**What happened**
The command did not discover or run any tests. This was not evidence that the workflow passed.

**How I responded**
I brought the result back for troubleshooting instead of treating it as a successful test run. The next diagnostic steps were to inspect the project files and the contents of `test.py`, and to try a minimal `unittest` example or automatic discovery to isolate the problem.

**What I learned**
A test command completing without an exception does not necessarily mean tests ran.
I need to check the number of tests executed and the final result.
I should not report a test suite as passing when the output says `Ran 0 tests`.

**Verification note**
Automated testing and verification: I ran python3 -m unittest discover -s tests -v to discover and execute the project's unit tests. I reviewed the individual test results and final summary to determine whether the tests passed. I also ran python3 -m compileall -q . to check Python syntax and tested the application through its command-line interface.
Actual test result:----------------------------------------------------------------------
Ran 29 tests in 0.007s

OK

## Engineering takeaways

- I used AI to clarify requirements and explain implementation concepts, not as a substitute for understanding the code.
- I learned to validate a requested status transition before changing the ticket.
- I learned how to test both successful operations and rejected operations.
- I checked terminal output and challenged a result that did not demonstrate successful testing.
- AI-generated suggestions still require review against the assignment and test results.

## Final verification checklist

- I reviewed my codes and can explain the functions I implemented.
- I ran the automated tests and confirmed that tests were actually discovered.
- I recorded the real test command, test count, and result above.
- I verified the required workflow rules, including unassigned-ticket rejection and explicit reopening.