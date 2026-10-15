# CampusFlow

## Problem Statement
Learn2Earn campus faces challenges in managing technical issues such as Wi-Fi failures, faulty laptops, and software problems due to poor tracking, prioritization, and assignment. CampusFlow aims to solve this by providing an organized ticket management system for reporting, tracking, and resolving issues efficiently.

## Project Objective
To develop a simple, reliable, and organized ticket management system that improves how technical support issues are reported, prioritized, assigned, tracked, and resolved within the Learn2Earn campus.

## Authors 
### 1. Andrew Otokpa: 
Developed F2 (List/View Tickets), F6 (Reports), and F7 (JSON Persistence). Also wrote the README documentation and tested the implemented features.

***PR Links***

https://github.com/MaryJane-09/CampusFlow/pull/2

https://github.com/MaryJane-09/CampusFlow/pull/9

https://github.com/MaryJane-09/CampusFlow/pull/5

https://github.com/MaryJane-09/CampusFlow/pull/3

https://github.com/MaryJane-09/CampusFlow/pull/4

### 2. Chinaza Nzekwe:
 Developed F1 (Ticket Creation), F3 (Ticket Assignment), F4 (Ticket Workflow), and F5 (Priority Queue) and also contribute to the README documentation and tested the implemented features.

 ***PR Links*** 

https://github.com/MaryJane-09/CampusFlow/pull/7

https://github.com/MaryJane-09/CampusFlow/pull/6

https://github.com/MaryJane-09/CampusFlow/pull/10

https://github.com/MaryJane-09/CampusFlow/pull/8

https://github.com/MaryJane-09/CampusFlow/pull/1

https://github.com/MaryJane-09/CampusFlow/pull/11

https://github.com/MaryJane-09/CampusFlow/pull/18

 ### Python Version - python 3.12.3

 ### setup: 
 Clone or download the CampusFlow project from GitHub.

Open a terminal and navigate to the project directory.

Verify Python is installed using python3 --version.

Run the application using python3 main.py.

Follow the CLI menu to create, view, assign, and manage tickets.

### Available menu
How to run the CLI and available menu options.

How to run the tests and what they cover.

How ticket priority and status rules work.

Where tickets are saved and how to start fresh.

Known limitations and future improvements.


### Test Coverage 
F1 (8 tests): generate first ticket id, ticket with valid input, check if category is valid, urgency validation, affected users validations, next ticket id, 

F3 (5 tests): assigned validation, case insensitive, empty name, invalid id.

F4(12 tests): ticket validations

F2 (9 tests): Ticket listing, searching, invalid IDs, empty input, and case-insensitive searches.

F6 (6 tests): Total tickets, status counts, priority counts, empty datasets, and data integrity.

F7 (6 tests): JSON saving, loading, missing files, malformed JSON, and duplicate-ID validation.

F5 (10 tests): if ticket are displayed, if resolved is excluded, sort by top most priority, the same priority sorted by ID, unassigned ticket displaying unassigned, ticket that are been worked on.

### Data Storage 
CampusFlow stores tickets in the ticket.json file located in the project directory.

Ticket records are saved in JSON format and reloaded when the application starts.

To start with an empty ticket collection:

Close the application.

Back up ticket.json if you want to keep the existing records.

Delete ticket.json.

Restart the application.

CampusFlow will initialize an empty ticket list if the file is missing.

### Known Limitation 
CampusFlow currently operates through a command-line interface.

Ticket data is stored locally in JSON rather than a database.

The application is designed primarily for single-user operation.

Project-wide workflow and priority integration tests are still needed.

### Future Improvements
Build a web-based dashboard using FastAPI.

Integrate SQLite or PostgreSQL for more reliable storage.

Add user authentication and role-based access.

Introduce ticket search filters and notifications.

Add automated tests for all ticket creation, assignment, workflow, and queue requirements.

Improve JSON saving with atomic file writes to reduce data-loss risks.