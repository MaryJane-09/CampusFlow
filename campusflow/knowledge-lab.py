import json
import os
from datetime import datetime, timezone

LAB_FILE = "knowledge_lab_sessions.json"
REFLECTIONS_DIR = "docs"
REFLECTIONS_FILE = os.path.join(REFLECTIONS_DIR, "learning-reflections.md")

QUESTIONS = [
    {
        "id": 1,
        "topic": "Critical SLA & Time Boundaries",
        "question": "Q1 | A critical ticket is created at 10:00 UTC. At 11:00 UTC, is it overdue?",
        "options": {
            "A": "Yes",
            "B": "No, only strictly after 11:00",
            "C": "Only if assigned",
            "D": "Only if reopened"
        },
        "answer": "B",
        "revision": "Review SLA boundary condition: a ticket is overdue only when current UTC time is STRICTLY LATER than due_at. At the exact due instant (11:00 UTC), it is not overdue."
    },
    {
        "id": 2,
        "topic": "Priority Order Rules",
        "question": "Q2 | Priority order: urgency=low and affected_users=10. What priority?",
        "options": {
            "A": "Critical",
            "B": "High",
            "C": "Medium",
            "D": "Low"
        },
        "answer": "C",
        "revision": "Review priority calculation hierarchy: affected_users > 3 or urgency == medium yields Medium priority when higher rules do not match."
    },
    {
        "id": 3,
        "topic": "Illegal State Transitions & Atomicity",
        "question": "Q3 | Illegal transition: an unassigned open ticket moves directly to in_progress. What should happen?",
        "options": {
            "A": "Transition succeeds",
            "B": "Status changes but history stays",
            "C": "Reject without changing ticket or events",
            "D": "Delete the ticket"
        },
        "answer": "C",
        "revision": "Review transaction invariants: rejected operations must leave both ticket data and audit event lists completely unchanged."
    },
    {
        "id": 4,
        "topic": "Reopening & SLA Cycles",
        "question": "Q4 | Reopening: a resolved high-priority ticket is reopened. Which SLA behavior is correct?",
        "options": {
            "A": "Keep old due_at always",
            "B": "Start a fresh SLA cycle while preserving created_at",
            "C": "Reset created_at to today's date",
            "D": "Delete previous events"
        },
        "answer": "B",
        "revision": "Review SLA lifecycle rules: reopening starts a new SLA cycle at the reopening timestamp, updates due_at, but preserves original created_at continuity."
    },
    {
        "id": 5,
        "topic": "Escalation Idempotency",
        "question": "Q5 | Escalation repeated: an overdue ticket is checked three times within one SLA cycle. How many new ESCALATE events?",
        "options": {
            "A": "Three",
            "B": "Two",
            "C": "One",
            "D": "Zero"
        },
        "answer": "C",
        "revision": "Review idempotency: each overdue ticket creates exactly ONE escalation event in a given SLA cycle using per-cycle escalation markers."
    },
    {
        "id": 6,
        "topic": "JSON Persistence & Fault Tolerance",
        "question": "Q6 | JSON corrupted: the saved file has invalid JSON. What is the safest action?",
        "options": {
            "A": "Replace data with empty list",
            "B": "Use eval()",
            "C": "Ignore and keep running with partial data",
            "D": "Reject load and preserve existing valid state"
        },
        "answer": "D",
        "revision": "Review storage safety: validation must reject malformed data before touching memory; never overwrite good state with empty defaults."
    },
    {
        "id": 7,
        "topic": "Code Review & Test Boundaries",
        "question": "Q7 | Code review: a PR changes SLA calculations but adds no boundary tests. What should a reviewer do?",
        "options": {
            "A": "Approve because it runs locally",
            "B": "Request focused tests and explanation",
            "C": "Merge and test next week",
            "D": "Ask AI to approve automatically"
        },
        "answer": "B",
        "revision": "Review engineering rigor: time and boundary logic changes require explicit unit tests verifying exact edge cases."
    },
    {
        "id": 8,
        "topic": "Security & Safe Parsing",
        "question": "Q8 | AI suggestion: an assistant says 'use eval() to parse stored JSON'. What should you do?",
        "options": {
            "A": "Copy it",
            "B": "Disable tests",
            "C": "Reject and use JSON parsing with validation",
            "D": "Share the whole file publicly"
        },
        "answer": "C",
        "revision": "Review security invariants: never execute arbitrary code (`eval`) on external or stored data; use built-in `json` parsing with strict schema validation."
    },
    {
        "id": 9,
        "topic": "Duplicate Detection & Normalization",
        "question": "Q9 | Duplicate warning: titles ' Wi-Fi   Down ' and 'wi-fi down' share category, both unresolved. What should the CLI do?",
        "options": {
            "A": "Silently delete original",
            "B": "Warn and require confirmation",
            "C": "Silently block forever",
            "D": "Ignore normalization"
        },
        "answer": "B",
        "revision": "Review duplicate policy: normalization catches whitespace/case variants, but requires explicit operator confirmation rather than hard blocking."
    },
    {
        "id": 10,
        "topic": "Audit Log Atomicity",
        "question": "Q10 | Audit log: an invalid return/status operation is rejected. What should happen to event count?",
        "options": {
            "A": "Increase by one",
            "B": "Increase twice",
            "C": "Reset to zero",
            "D": "Stay unchanged"
        },
        "answer": "D",
        "revision": "Review event atomicity: failed operations append zero events, keeping audit and ticket states completely unchanged."
    }
]

def run_knowledge_lab():
    print("\n===== ENGINEERING KNOWLEDGE LAB =====")
    participant = input("Select Participant Role [A (Engineer A) / B (Engineer B)]: ").strip().upper()
    if participant not in ("A", "B"):
        print("Invalid role selection. Defaulting to Engineer B.")
        participant = "B"

    print(f"\nWelcome Engineer {participant}! You are taking the official 10-question Knowledge Bank assessment.")
    print("Requirement: At least 3 detailed explanations must be provided during this session.\n")

    score = 0
    explanations_given = 0
    missed_questions = []
    session_details = []

    for q in QUESTIONS:
        print(f"\n--------------------------------------------------")
        print(f"Question {q['id']} / 10 [{q['topic']}]")
        print(q['question'])
        for opt, text in q['options'].items():
            print(f"  {opt}. {text}")

        ans = input("Your answer (A/B/C/D): ").strip().upper()
        is_correct = (ans == q['answer'])

        if is_correct:
            print("-> Correct!")
            score += 1
        else:
            print(f"-> Incorrect. The correct answer was {q['answer']}.")
            missed_questions.append(q)

        needed_more = max(0, 3 - explanations_given)
        prompt_msg = (
            f"Provide your reasoning/explanation (Optional): " 
            if needed_more == 0 
            else f"Provide your reasoning/explanation (MANDATORY - {needed_more} more required): "
        )
        
        explanation = input(prompt_msg).strip()
        if explanation:
            explanations_given += 1
        elif needed_more > 0:
            while not explanation:
                print("Error: You must provide an explanation to meet the minimum requirement of 3.")
                explanation = input("Provide your reasoning/explanation: ").strip()
            explanations_given += 1

        session_details.append({
            "question_id": q['id'],
            "topic": q['topic'],
            "selected": ans,
            "correct": q['answer'],
            "passed": is_correct,
            "explanation": explanation
        })

    print("\n========================================")
    print(f" ASSESSMENT COMPLETE - ENGINEER {participant}")
    print(f" Final Score: {score} / 10 ({(score/10)*100}%)")
    print(f" Explanations Logged: {explanations_given}")
    print("========================================")

    if missed_questions:
        print("\nTargeted Revision Topics for Missed Questions:")
        for mq in missed_questions:
            print(f"  * [Q{mq['id']}] {mq['topic']}: {mq['revision']}")
    else:
        print("\nFlawless execution! You achieved a perfect score across all domains.")

    session_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "participant": f"Engineer {participant}",
        "score": score,
        "total": 10,
        "explanations_count": explanations_given,
        "details": session_details
    }

    try:
        existing_data = []
        if os.path.exists(LAB_FILE) and os.path.getsize(LAB_FILE) > 0:
            with open(LAB_FILE, "r") as f:
                existing_data = json.load(f)
        existing_data.append(session_record)
        with open(LAB_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)
        print(f"\nLearning session saved successfully to {LAB_FILE}.")
    except Exception as e:
        print(f"Warning: Could not save lab session: {e}")

    print("\n--- Real Learning Reflection Reminder ---")
    print("Per system guidelines, choose one missed or difficult question and log your reflection in:")
    print(f"  -> '{REFLECTIONS_FILE}'")
    print("Format template:")
    print("  'I first believed..., I checked..., I changed my understanding because...'")
    
    create_ref = input("Would you like to draft a learning reflection now? (y/n): ").strip().lower()
    if create_ref == 'y':
        q_num = input("Enter Question ID reflected upon (e.g., 1): ").strip()
        reflection_text = input("Enter your reflection ('I first believed..., I checked..., I changed my understanding because...'): ").strip()
        
        os.makedirs(REFLECTIONS_DIR, exist_ok=True)
        reflection_entry = f"\n\n## Engineer {participant} - Reflection on Q{q_num}\n- **Date:** {datetime.now(timezone.utc).isoformat()}\n- **Reflection:** {reflection_text}\n"
        
        with open(REFLECTIONS_FILE, "a") as rf:
            rf.write(reflection_entry)
        print(f"Reflection successfully appended to {REFLECTIONS_FILE}!")

    input("\nPress Enter to return to the Main Menu...")