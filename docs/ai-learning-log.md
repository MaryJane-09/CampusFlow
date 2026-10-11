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