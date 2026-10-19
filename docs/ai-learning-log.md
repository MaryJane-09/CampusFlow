## Fellow: Nzekwe Chinaza

### Interaction #1 — Python Ticket ID Consistency and Workflow Debugging

**Problem:**  
My CampusFlow application used both `"id"` and `"ID"` as dictionary keys. This caused issues with loading tickets, displaying ticket IDs, and updating ticket statuses through the workflow.

**My initial understanding:**  
I knew the application was having problems with ticket IDs and workflow transitions, but I had not identified that different modules were using different dictionary keys. I also needed to understand how status capitalization affected workflow comparisons.

**Prompt to AI:**  
"My workflow is having some issues."

I then shared the error message and my `campusflow/workflow.py` code to investigate the problem.

**Useful AI guidance:**  
The AI helped me identify that `tickets.py` stored ticket IDs using the lowercase key `"id"`, while `workflow.py` and some test fixtures expected `"ID"`. It suggested using `ticket.get("id", ticket.get("ID"))` to support both formats. It also explained how normalizing status strings with `.lower().strip()` makes comparisons consistent.

**My independent experiment/test:**  
I inspected `campusflow/workflow.py` and located the ticket lookup and work queue display sections. I was guided through updating the ID lookups to support both key formats and normalizing the current ticket status before comparing workflow transitions.

**Verification source or result:**  
The observed error was `Error: Unrecognized workflow.` when I attempted to update ticket `T004`, whose displayed status was `open`. The suggested changes addressed likely causes, but I still need to rerun the workflow and relevant unit tests to confirm the fix.

**Decision:**  
Accepted the proposed approach provisionally because it addresses the inconsistency between the ticket data and the workflow code. I will verify it with tests before considering the issue fully resolved.

**Related file/commit:**  
- `campusflow/tickets.py`
- `campusflow/workflow.py`
- `campusflow/storage.py`
- `campusflow/list_view.py`
- Commit SHA/PR: Recorded in the audit form.

**What I can now explain without AI:**  
Python dictionary keys are case-sensitive, so `"id"` and `"ID"` are different keys. The `.get()` method lets me retrieve a value without raising a `KeyError` when a key is missing. I can also normalize strings using `.lower().strip()` so differences in capitalization and surrounding whitespace do not interfere with status comparisons. I understand that I must run tests to verify a proposed fix rather than assuming it works.

# Interaction #2 — Event Recording, Persistence, and Workflow Consistency

**Problem:**

My CampusFlow application needed to record successful ticket actions, preserve event history, and keep ticket data consistent when saving failed. I also needed to display ticket history in chronological order.

**My initial understanding:**

I had implemented ticket status transitions and an event-recording function. However, I needed to understand how a failed save could leave the in-memory ticket state and event history inconsistent with the persisted JSON data.

**Prompt to AI:**

I shared my existing `workflow.py`, `history.py`, and `storage.py` implementations and asked for help finishing the required Engineer B features.

**Useful AI guidance:**

The AI helped me identify that my workflow changed the ticket status and recorded an event before saving the database. It guided me toward using a rollback approach to restore the previous status and event history when a handled error occurs.

I also learned that my storage implementation uses a temporary JSON file, flushes the file, calls `os.fsync()`, and replaces the original file with `os.replace()`. This helps prevent a partially written file from replacing the existing database.

The AI also identified that sample event-recording calls at the bottom of `history.py` could create unintended events when the module was imported.

**My independent experiment/test:**

I updated my workflow to use a shared transition helper, added rollback handling, and changed the work queue to load ticket data through the existing storage function. I confirmed that the application continued working afterward.

**Verification source or result:**

My application continued working after the changes. However, I still need a dedicated test that simulates a save failure and verifies that both the ticket status and event history are restored.

**Decision:**

I accepted the suggested approach while recognizing that a successful normal workflow does not, by itself, prove that rollback works under every failure condition.

**Related files:**

- `workflow.py`
- `history.py`
- `storage.py`
- `show_ticket.py`

**What I can now explain without AI:**

I can explain why changing a ticket's status and recording its event must be treated as one logical operation. If saving fails, the application should restore the previous in-memory state so the ticket and event history remain consistent. I also understand the purpose of temporary-file replacement and why importing a module should not automatically create sample records.

---

# Interaction #3 — Ticket History Display and Chronological Ordering

**Problem:**

I needed to implement a history-display function that shows the event sequence for a ticket, including creation, assignment, starting work, resolution, and reopening.

**My initial understanding:**

I already had an `Event` dataclass and a `campus.events` collection. However, I initially approached history display as though it required creating a new event from user input.

**Prompt to AI:**

I shared my initial `show_history()` function and asked for guidance on implementing the history-display requirement.

**Useful AI guidance:**

The AI explained the difference between recording an event and displaying an existing event. It guided me toward filtering the stored events by ticket ID, checking whether the ticket exists, sorting matching events by timestamp, and displaying the recorded information without modifying the event history.

**My independent experiment/test:**

I rewrote `show_history()` to:

- Normalize the ticket ID using `.upper().strip()`.
- Check whether the ticket exists in `campus.tickets`.
- Collect matching records from `campus.events`.
- Sort matching events by timestamp.
- Display the event ID, action, operator, timestamp, status transition, and details.
- Handle tickets without recorded events.

**Verification source or result:**

I completed the revised function. I still need to verify its behavior using dedicated tests for multiple events, tickets without events, and nonexistent ticket IDs.

**Decision:**

I accepted the read-only history-display approach because event creation and event display have different responsibilities.

**Related files:**

- `history.py`
- The module containing `show_history()`
- `storage.py`

**What I can now explain without AI:**

I can explain why filtering events by ticket ID prevents unrelated events from appearing in a ticket's history. I understand why matching events should be collected before sorting and why displaying history should not create new events or change existing records.

---

# Interaction #4 — Duplicate Ticket Detection and Title Normalization

**Problem:**

CampusFlow needed to warn users about unresolved tickets with matching titles in the same category.

**My initial understanding:**

I understood that duplicate detection required comparing ticket titles, but I needed to determine how to handle differences in capitalization and whitespace.

**Prompt to AI:**

I asked how to normalize ticket titles so that titles such as `Printer is not working` and ` printer IS NOT WORKING ` would be treated as equivalent.

**Useful AI guidance:**

The AI explained that `lower()` converts text to lowercase, while `split()` without an argument separates words and handles repeated whitespace. Joining the resulting words with a single space creates a normalized title.

I then received guidance on checking the normalized title, category, and ticket status when searching for duplicates.

**My independent experiment/test:**

I identified the normalization operations and received a `detect_duplicates()` implementation that:

- Normalizes the new and existing ticket titles.
- Compares categories without case sensitivity.
- Checks for unresolved tickets.
- Excludes the current ticket when its ID is supplied.
- Returns matching tickets so the creation workflow can ask the user whether to continue.

**Verification source or result:**

The function was written, but its integration into ticket creation and its behavior under dedicated duplicate-detection tests still need verification.

**Decision:**

I accepted the normalization approach because it allows the application to detect equivalent titles despite differences in capitalization and repeated whitespace. Duplicate detection should warn users rather than automatically prevent creation.

**Related files:**

- `duplicate.py`
- The ticket-creation module
- `show_ticket.py`

**What I can now explain without AI:**

I can explain how normalization makes string comparisons more consistent. I understand that matching titles alone is insufficient: the category must also match, and resolved tickets should not trigger an unresolved-ticket warning.

---

# Interaction #5 — JSON Schema Migration and Test Verification

**Problem:**

My application reported `JSON root must be a dictionary object` because my existing `ticket.json` contained a list of tickets, while the updated storage layer expected a dictionary containing a schema version, tickets, and events.

**My initial understanding:**

I knew that ticket loading had failed, but I needed to identify the mismatch between the existing JSON structure and the structure expected by `load_json()`.

**Prompt to AI:**

I shared the error message and the contents of my existing `ticket.json` file.

**Useful AI guidance:**

The AI identified the schema mismatch and explained that the storage layer expected an object with `schema_version`, `tickets`, and `events` fields. It guided me in preserving the existing ticket records while placing them inside the expected structure.

**My independent experiment/test:**

I updated the JSON structure to include `schema_version: 2`, preserved the existing tickets, and added an empty events list because no historical events needed to be retained in that file.

I then reran the application.

**Verification source or result:**

The application loaded successfully after the JSON structure was corrected. My subsequent test run produced:

- 77 tests run.
- 77 tests passed.
- 0 failures.
- 0 errors.

The test output included checks involving invalid categories, urgency, user counts, and simulated disk failure. The complete feature coverage still needs to be compared with the Engineer B requirements.

**Decision:**

I accepted the schema correction because it matched the storage layer's validation requirements and preserved the existing tickets.

**Related files:**

- `ticket.json`
- `storage.py`
- `show_ticket.py`
- `tests/`

**What I can now explain without AI:**

I can explain the difference between a JSON list and a JSON object, why the outermost structure must match what the loader expects, and why changing a storage schema requires preserving existing records rather than simply replacing them with empty data. I also understand that passing tests provides evidence for the behaviors tested, not proof that every feature is complete.



## Fellow: Andrew Otokpa

### Interaction #1 — Python for/else and Ticket Searching (F2)

***Problem:** I needed to implement a function that searches for a ticket by ID and displays its details without producing incorrect error messages.

***My initial understanding:*** I understood how to loop through tickets and compare IDs, but I initially placed the "Ticket not found" message inside the loop. This could display an error before the search was completed.

***Prompt to AI:*** I submitted my view_ticket() function for review, including the ticket search loop and the "Ticket not found" condition.

***Useful AI guidance:*** AI explained how Python's for/else works and why using return after finding a matching ticket prevents unnecessary searching. It also explained how .strip() and .upper() improve input handling.

***My independent experiment/test:*** I revised the function, added input validation, and ran automated tests covering existing IDs, unknown IDs, lowercase input, extra spaces, and empty input.

***Verification source or result:*** All 9 F2 LIST/VIEW tests passed.

***Decision:** Accepted and applied the guidance because testing confirmed that the function correctly handles ticket searches and invalid input.

***Related file/commit:*** campusflow/tickets.py — F2 LIST/VIEW implementation and associated tests.

***What I can now explain without AI:*** I can explain how to search a list of dictionaries, validate input, use return to stop a function, and apply for/else so an error message appears only when no matching ticket is found.

### Interaction #2 — Counting Tickets and Generating Reports (F6)

***Problem:*** I needed to develop reports showing the total number of tickets and their distribution by status and priority.

***My initial understanding:*** I initially attempted to use campus.ticket.count() to calculate the total number of tickets. I also made mistakes when increasing counters and accessing dictionary keys.

***Prompt to AI:***

def generate_report(campus: CampusFlow):

    campus.ticket.count()

I subsequently shared updated implementations for review.

***Useful AI guidance:*** AI explained the difference between len() and .count(), how to increment numerical counters, and why report results should be printed after the loop rather than during each iteration.

***My independent experiment/test:*** I implemented the total ticket count, three status counters, and four priority counters. I ran six automated reporting tests against different ticket datasets.

***Verification source or result:*** All 6 F6 tests passed when run individually using unittest discover. A later combined suite reported failures and errors, so project-wide integration remains under investigation.

***Decision:*** Accepted and applied the explanations after correcting my implementation. I retained the straightforward loop-and-counter approach because it produces the required statistics without modifying ticket records.

***Related file/commit:*** campusflow/reports.py — generate_report(); test_reports.py — reporting tests.

***What I can now explain without AI:*** I understand the difference between counting the length of a list and counting occurrences of a value. I can also explain how to calculate statistics from dictionaries using loops, conditions, and counters.

### Interaction #3 — JSON Persistence and Error Handling (F7)

***Problem:*** I needed to ensure CampusFlow could save tickets, reload them after restarting, and reject invalid ticket data.

***My initial understanding:*** I understood basic JSON reading and writing but needed to improve error handling and validation for missing files, malformed JSON, and duplicate ticket IDs.

***Prompt to AI:*** I shared my persistence implementation during development and later asked:

"can will make this test to be using unittest"

I provided my existing persistence test script using json, tempfile, and Python assertions.

***Useful AI guidance:*** AI explained how to organize persistence tests using unittest.TestCase, setUp(), tearDown(), assertions, and assertRaises(). It also helped explain why temporary directories are useful for preventing tests from changing real application data.

***My independent experiment/test:*** I tested missing files, saving tickets, reloading tickets, malformed JSON, preservation of existing in-memory records, and duplicate IDs.

***Verification source or result:*** The original persistence test script passed all six checks. The converted unittest version was provided, but a successful run of that converted version has not yet been confirmed in this log.

***Decision:*** Accepted the JSON storage approach because it is simple and suitable for the project's CLI scope. I also chose to improve test organization using unittest. Further verification of the converted tests is still needed.

***Related file/commit:*** campusflow/storage.py and test_persistence.py.

***What I can now explain without AI:*** I can explain how to serialize Python data to JSON, restore it into an application object, handle missing or malformed files, and detect duplicate ticket IDs before loading data.

### Interaction #4 — Improving AI-Recommended Testing Commands

***Problem:*** I wanted a standard command to discover and run automated tests rather than executing each test file separately.

***My initial understanding:*** I knew that Python supported unittest discover, but I was unsure about the correct command syntax and directory arguments.

***Prompt to AI:***

"why cant i use this to run my test file python3 -m unittest discover -s tests -v "test_reports.py""

Useful AI guidance: AI explained that -s specifies the test directory, -p specifies the filename pattern, and -v enables verbose test output.

***My independent experiment/test:*** Instead of continuing to use the previously suggested direct-script approach, I ran:

python3 -m unittest discover -s test -p "test_reports.py" -v

Verification source or result: My terminal returned:

Ran 6 tests in 0.002s

OK

***Decision:*** Improved the original AI recommendation. The initial guidance used commands that executed individual test files directly. I preferred unittest discover because it provides a consistent way to select test files and run the test suite. I verified the revised command by running the six reporting tests successfully.

***Related file/commit:*** Reporting test file and README testing instructions.

***What I can now explain without AI:*** I understand how Python discovers automated tests, what the -s, -p, and -v arguments do, and how to interpret passing and failing test results.

### Interaction #5 - datetime

***Problem:** I needed to learn how to represent UTC timestamps and calculate ticket deadlines.

***My initial understanding:*** I knew how to get the current time, but I didn’t understand naive and timezone-aware datetimes. My first attempt used datetime.now() without a timezone.

***Prompt to AI:*** what is naive and aware

***Useful AI guidance:*** AI explained that aware datetimes include timezone information, timedelta represents a duration, and fixed starting times make tests predictable.

***My independent experiment/test:*** I wrote a small program that created an aware UTC datetime and added 60 minutes. I then used a fixed starting time of 14 October 2026 at 10:00 UTC and predicted an 11:00 UTC result.

***Verification source or result:*** ran my test and it past python3 -m unittest discover -s tests -p "test_sla.py" -v

***Decision:** I accepted the guidance to pass the starting time into calculate_due_at instead of reading the current time inside it. This lets the same function work with real creation times and fixed test times.

***Related file/commit:*** campusflow/sla.py, tests/test_sla.py

***What I can now explain without AI:*** I can explain the difference between datetime and duration, why timezone information matters

### Interaction #6 - unittest

***Problem:** I needed to learn how to use Python’s unittest to verify my SLA deadline function.


***My initial understanding:***I knew how to define a test class, but I wasn’t sure what inputs to pass or how to write the expected result. My first attempt passed 60 as the cycle start instead of a datetime.

***Prompt to AI:*** “explain better”

I asked this after being guided to write my first SLA test.

***Useful AI guidance:*** AI explained three steps: prepare known inputs, call the function, and compare its actual result with an independently chosen expected value. It also explained how to use self.assertEqual.

***My independent experiment/test:*** I wrote a critical-priority test using 14 October 2026 at 10:00 UTC as the starting time. I initially made the expected deadline equal to the starting time. After reviewing the requirement, I changed the expected deadline to 11:00 UTC and ran the test.

***Verification source or result:*** I ran python3 -m unittest discover -s tests -p "test_sla.py"

***Decision:** I accepted the advice to use fixed UTC inputs and explicit expected datetimes. This makes the tests repeatable and avoids copying the function’s calculation into the expected result.

***Related file/commit:*** campusflow/sla.py, tests/test_sla.py 

***What I can now explain without AI:*** I can explain what unittest is and how to use their basic assert such as asserEqual() etc.