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