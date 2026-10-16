# CampusFlow — Campus Technical Support Ticket Manager

## About the Project

CampusFlow is a Python command line application that helps campus technical support teams manage requests such as Wi-Fi outages, broken laptops, software installation problems and inaccessible learning tools.

Staff can create tickets, calculate priority automatically, assign tickets, track progress, add follow up notes, search, view a work queue, generate reports and save records to a JSON file. A built-in Engineering Understanding Check quizzes the team on how the application behaves.

The project uses only the Python standard library. It was built as an engineering sprint to practice modular design, validation, safe data handling, automated testing and collaboration through GitHub pull requests.

## Features

### 1. Ticket Creation and Validation

A ticket is created from:

- **Title:** cannot be empty (or spaces only) and cannot contain numbers. If the title is invalid, the program prints `Enter a valid title.` and asks again; it does not continue until a valid title is entered.
- **Category:** Network, Hardware, Software or Other (input such as `network` is accepted and stored as `Network`).
- **Urgency:** low, medium or high.
- **Affected users:** a strictly positive whole number. Zero, negatives, decimals, text and booleans are rejected.

Each ticket gets a unique ID (`T001`, `T002`, ...). IDs continue after the highest saved ticket, so reopening the program never reuses an ID.

### 2. Automatic Priority Calculation

Priority is worked out in this order:

1. `critical`: urgency is high **and** affected users ≥ 10
2. otherwise `high`: urgency is high **or** affected users ≥ 10
3. otherwise `medium`: urgency is medium **or** affected users ≥ 3
4. otherwise `low`

### 3. Assignment and Status Management

- Tickets can be assigned and reassigned to a staff member. The staff name cannot be blank.
- **Resolved tickets cannot be assigned or reassigned.** They must be reopened first.
- Statuses are `open`, `in_progress` and `resolved`.
- Allowed moves: open → in_progress → resolved, and resolved → open (reopen).
- An unassigned ticket cannot move to `in_progress`.

### 4. Follow-up Notes

Staff can leave structured notes on a ticket and read them later.

- Each note has a `note_id` (`N001`, `N002`, ...), an `author` and a `message`.
- Note IDs are **per ticket**: the first note on every ticket is `N001`. Numbering continues correctly after the tickets are saved and loaded again.
- Only `open` or `in_progress` tickets accept new notes. A resolved ticket must be reopened first.
- The author cannot be blank. The message must be 5–300 characters after trimming spaces.
- A rejected note does not use up an ID and does not change the ticket.
- Notes are kept when a ticket is resolved and reopened. *View Ticket Notes* shows them in note_ID order, including notes on resolved tickets.

### 5. Priority Based Work Queue

The work queue shows **only open tickets**, ordered critical, high, medium, low. Tickets with the same priority are ordered by numeric ticket ID, so `T2` comes before `T10`. Tickets that are `in_progress` or `resolved` never appear here.

### 6. Search Tickets

A read-only search that never changes a ticket.

- **Title:** case insensitive substring match, so `wifi`, `WIFI` and `WiFi` all find "Wifi down".
- **Optional filters:** category, status and priority. Press Enter to skip any filter.
- **All supplied filters must match (AND).** Searching `wifi` + `Network` + `open` returns only open network tickets with "wifi" in the title.
- An invalid filter value (for example the category `Banana`) shows a message and asks again.
- After a search you may sort the results by priority, then ticket ID. This is a separate view and does not replace the work queue.
- Results show ID, title, category, priority, status and assigned staff.

Matching is by substring only. There is no fuzzy spelling correction, so `wi-fi` does not match `wifi`.

### 7. Ticket Reports

The report shows:

- total tickets
- counts by status, by priority and by category
- unresolved tickets (open + in progress) and resolved tickets
- resolution percentage (resolved ÷ total × 100)

Each ticket is counted once, by its **current** status, so a reopened ticket counts as open. With no tickets, the report shows `0.0%` and does not crash.

Sample output:

```text
****** TICKET REPORT *******
Total tickets: 6

Tickets by status:
Open: 2
In progress: 1
Resolved: 3

Tickets by priority:
Critical: 1
High: 2
Medium: 1
Low: 2

Tickets by category:
Network: 3
Hardware: 1
Software: 1
Other: 1

Unresolved (open + in progress): 3
Resolved: 3
Resolution rate: 50.0%
```

### 8. Engineering Understanding Check

An interactive quiz with six scenario questions about how CampusFlow behaves.

- Answers must be `A`, `B`, `C` or `D`. Anything else is rejected and the question is asked again.
- One point per correct answer, for a final score from 0 to 6. The score uses the first valid answer given for each question.
- Feedback is shown after each answer but never changes the recorded answer.
- You choose two of your answers and explain them in your own words. The explanations are saved to `docs/understanding-check-notes.md` for mentor discussion and are never auto-graded.

### 9. JSON Persistence

Tickets are loaded when the program starts and saved after changes, so records survive closing the program. If the data file does not exist, the program starts with no tickets. Invalid JSON, a file that is not a list, entries that are not dictionaries, a ticket without an ID, or duplicate ticket IDs are rejected with a clear message.

## Menu

```text
1. Create a ticket
2. View all tickets
3. Assign or reassign a ticket
4. Update ticket status
5. View work queue
6. Generate ticket report
7. Search tickets
8. Add follow-up note
9. View ticket notes
10. Engineering Understanding Check
11. Exit
```
Entering anything other than a whole number from 1 to 11 shows a message and shows the menu again.

## Design

New features keep **decisions** separate from **prompting and printing**, so each part can be tested on its own.

| Layer | File | Job |
|---|---|---|
| Rules | `campusflow/tickets.py` | Creates tickets, validates input, calculates priority and IDs. |
| Rules | `campusflow/notes.py` | Validates and adds notes, per-ticket note IDs. |
| Rules | `campusflow/workflow.py` | Assignment, status changes, reopening, work queue. |
| Rules | `campusflow/search.py` | Decides which tickets match; sorts results. |
| Rules | `campusflow/reports.py` | Counts tickets and formats the report text. |
| Rules | `campusflow/understanding_check.py` | Question bank, scoring and explanations. |
| Rules | `campusflow/validation.py` | Reusable validation helpers (affected users, category, urgency). |
| Storage | `campusflow/storage.py` | Saves and loads the JSON file. |
| Screens | `campusflow/cli_views.py` | Prompts the user, calls the rules, shows results. Takes `input_fn` and `output_fn` so tests can script answers. |
| Menu | `main.py` | Shows the menu and routes each choice. |

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
│   ├── search.py
│   ├── reports.py
│   ├── understanding_check.py
│   ├── validation.py
│   ├── storage.py
│   └── cli_views.py
│
├── tests/
│   ├── __init__.py
│   ├── test_tickets.py
│   ├── test_notes.py
│   ├── test_workflow.py
│   ├── test_search.py
│   ├── test_reports.py
│   ├── test_understanding.py
│   ├── test_validation.py
│   ├── test_cli.py
│   ├── test_storage.py
│   └── test_storage_persistence.py
│
├── data/
│   └── tickets.json
│
├── docs/
│   ├── baseline-check.md
│   ├── design-decisions.md
│   ├── ai-learning-log.md
│   └── understanding-check-notes.md
│
├── .gitignore
└── README.md
```

**Note:** `data/` is created on your computer when the program saves tickets. It is excluded from version control.

## Requirements

- Python 3 (tested with Python 3.12)
- A terminal
- Git, to clone and contribute

No third-party packages are needed.

## Installation and Running (fresh clone)

```bash
git clone https://github.com/ZachOG10/CampusFlow-team.git
cd CampusFlow-team
python3 main.py
```

On systems where Python is started with `python`, use `python main.py`.

## Running the Tests

From the project root:

```bash
python3 -m unittest discover -s tests -v
```

`-v` lists every test. A successful run ends with `OK`. Some original tests print messages such as `Invalid category.` between results. That is normal output, not a failure.

| Test file | Covers |
|---|---|
| `test_tickets.py` | Ticket creation, validation, priority rules, ID continuity. |
| `test_notes.py` | Note validation, per-ticket IDs, rejected notes, resolve and reopen. |
| `test_workflow.py` | Assignment, status transitions, reopening, work queue, resolved tickets cannot be reassigned. |
| `test_search.py` | Case-insensitive search, AND filters, invalid filters, search is read-only, sorting. |
| `test_reports.py` | Report counts, empty report, resolve and reopen counts, no double counting. |
| `test_understanding.py` | Question bank, scoring, invalid answers, explanations. |
| `test_validation.py` | Validation helpers. |
| `test_cli.py` | Menu choices, title prompt, search and notes screens, understanding check, using scripted input. |
| `test_storage_persistence.py` | Saving, loading and rejecting bad JSON. |

## Data Format

`data/tickets.json` holds a JSON list of ticket dictionaries:

| Field | Meaning |
|---|---|
| `id` | Unique ID such as `T001` |
| `title` | Ticket title |
| `category` | `Network`, `Hardware`, `Software` or `Other` |
| `urgency` | `low`, `medium` or `high` |
| `affected_users` | Strictly positive whole number |
| `priority` | `critical`, `high`, `medium` or `low` |
| `status` | `open`, `in_progress` or `resolved` |
| `assigned_to` | Staff name, or `null` when unassigned |
| `notes` | List of notes (empty for a new ticket) |

Each note is `{"note_id": "N001", "author": "...", "message": "..."}`.

## Git and Pull Request Workflow

- No feature work is committed directly to `main`.
- Each piece of work lives on its own branch with focused commits such as `fix: ...`, `feat: ...` and `test: ...`.
- Every pull request is reviewed and approved by the other engineer, who reads the diff and runs the tests before merging.
- After each merge, update `main` with `git pull origin main` and run the full test suite again.

## Contributors

**Engineer A — Ticket Safety and Storage:** Aondowase Zachariah Ticket creation and validation, notes, assignment and status rules, JSON persistence, and their tests.

**Engineer B — Search, Reporting and CLI:** Bartholomew Akor. Search, reports, CLI screens, the Engineering Understanding Check, and their tests.

## Learning Outcomes

- Separating input and output from business rules.
- Validating before changing data, and proving a rejected action changed nothing.
- Filtering, sorting and counting without double-counting.
- Safe file handling and JSON error handling.
- Writing unit tests, including negative tests and scripted CLI tests.
- Collaborating with Git: branches, pull requests and reciprocal review.
- Using AI to learn and checking its suggestions with tests.

## Future Improvements

- Check every field of every ticket and note when loading JSON (required keys, valid statuses and categories, note shapes).
- A graphical or web interface.
- Staff authentication.
- Ticket creation times and an activity history.
- Fuzzy search.