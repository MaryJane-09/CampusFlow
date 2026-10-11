# CampusFlow  Design Decisions Log

**Project:** CampusFlow  Campus Technical Support Ticket Manager  
**Purpose:** Record *what we decided, why we decided it, and how we verified it.*  
**Last updated:** 11 October 2026  
**Status:** Draft for team review. Entries marked **Implemented** describe the features developed and tested so far; **To confirm** items require team agreement.

## 1. Project architecture

### D01  Share one CampusFlow object across features
- **Decision:** Create one `CampusFlow` instance in `main.py` and pass it to feature functions instead of creating separate ticket lists in each module.
- **Why:** Listing, viewing, reporting, and saving should all work with the same up-to-date tickets. This reduces inconsistency between modules.
- **Implementation:** The shared object's `campus.ticket` list stores ticket dictionaries; functions receive `campus` as a parameter.
- **Status:** Implemented in the current application design.

### D02  Use ticket dictionaries with agreed field names
- **Decision:** Represent each ticket as a dictionary containing `ID`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, and `assigned_to`.
- **Why:** All feature modules must read and update the same fields consistently.
- **Important detail:** Use **`affected_users`** (plural), **`status`** for workflow state, and **`priority`** for severity ranking.
- **Status:** Implemented schema convention; confirm that all teammate modules use the same keys.

## 2. F2 List and view tickets

### D03 Read tickets from memory, not directly from JSON
- **Decision:** `list_ticket(campus)` and `view_ticket(campus)` read the shared `campus.ticket` list.
- **Why:** Storage is responsible for loading tickets. F2 should display the current state, including unsaved changes in memory if any, without duplicating file-handling logic.
- **Status:** Implemented; **9 automated F2 tests passed**.

### D04 — Search by ticket ID and provide clear error messages
- **Decision:** Ask for a ticket ID, remove surrounding whitespace, and compare it without lowercase/uppercase differences. Display one matching ticket or a not-found message. Reject empty input.
- **Why:** It improves usability and avoids accidental failed searches caused by typing variations.
- **Implementation note:** Stop immediately after a match, so the search does not incorrectly print "Ticket not found."
- **Status:** Implemented; covered by F2 tests.

## 3. F6  Ticket reports

### D05  Calculate reports from current tickets
- **Decision:** Calculate total tickets using the list length and count tickets separately by `status` (`open`, `in_progress`, `resolved`) and `priority` (`critical`, `high`, `medium`, `low`).
- **Why:** Reports show the current workload and distribution without storing redundant counters that might become outdated.
- **Implementation note:** Print results after the counting loop; empty collections should report zero counts.
- **Status:** Implemented; **6 automated F6 tests passed**.
- **Boundary:** F6 **reports** existing priorities; it does not **calculate** a new ticket's priority. That belongs to ticket creation.

## 4. F7  JSON persistence

### D06  Store tickets in `ticket.json`
- **Decision:** Serialize the shared ticket list as a JSON array of ticket objects and reload it at startup.
- **Why:** JSON is easy to inspect, portable, and needs no external database for this CLI project.
- **Status:** Implemented; **6 automated F7 tests passed**.

### D07  Handle missing and invalid save data differently
- **Decision:** If `ticket.json` does not exist, begin with an empty list. If the JSON is malformed, has the wrong overall structure, or contains duplicate/missing ticket IDs, reject loading instead of silently replacing data.
- **Why:** A missing file is normal on first use; corrupted or inconsistent data should be surfaced so existing tickets are not accidentally lost.
- **Status:** Implemented and tested for missing files, malformed JSON, non-list records, and duplicate IDs. Confirm remaining validation rules as a team.

### D08  Check ticket IDs during loading
- **Decision:** Track IDs already encountered during loading and reject duplicates.
- **Why:** Ticket IDs uniquely identify records for viewing, assignments, and updates.
- **Status:** Implemented and tested for duplicate IDs in existing JSON.
- **Follow-up:** Separately test that ticket creation generates a new unique ID **after loading existing tickets**; load-time duplicate detection alone does not prove this.


## 6. Testing evidence

| Feature | Test result | What it establishes |
|---|---|---|
| F1 - Create | **8/8 passed** | generate first ticket id, ticket with valid input, check if category is valid, urgency validation, affected users validations, next ticket id

| F2 — List / View | **9/9 passed** | Display, search, empty input, case/space handling, missing IDs |
| F3 - Assign | **5/5 paased** | assigned validation, case insensitive, empty name, invalid id.
| F4 - Work Flow | **12/12 passed** | ticket validations
| F5 - Work Queue | **10/10 passed** | if ticket are displayed, if resolved is excluded, sort by top most priority, the same priority sorted by ID, unassigned ticket displaying unassigned, ticket that are been worked on.
| F6 — Reports | **6/6 passed** | Total/status/priority counts and report read-only behavior |
| F7 — Persistence | **6/6 passed** | Missing file, save/reload, malformed data, preservation of in-memory data on load error, duplicate IDs |


## 8. Items for a final team review

- Confirm the exact priority calculation rule and test boundary values.
- Agree on ticket ID generation after restart and on whether IDs can ever be reused.
- Confirm the only allowed status transitions and who may perform them.
- Agree on queue tie-breaking for numeric IDs.
- Ensure all modules use matching dictionary field names.
- Confirm when saves happen following successful changes and how failed saves are handled.
- Run the ten acceptance-checklist scenarios end to end, and record actual results.