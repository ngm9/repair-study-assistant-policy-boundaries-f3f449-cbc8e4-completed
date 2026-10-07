## Task Overview
A clinical trial is a study that tests a medicine across several clinics, or sites. Site coordinators use an AI assistant to answer questions and draft messages, drawing on the study protocol, site procedures, and case records. Clinic staff can upload notes, but the study's own rules still set what the assistant may say.

After a quarter of live use, clinic staff, the privacy office, and the medical monitor have each reported behaviour they can't rely on. Their expectations are listed under Objectives. Investigate the supplied requests and make the assistant useful while staying inside the study's rules. Use your own provider key for a full run.

## Objectives
- Uploaded context should stay bounded by the study's rules, never override them.
- Participant privacy should hold everywhere the assistant responds or keeps a record.
- Refusals should be clear, and point people to the right next step.
- Every intervention should stay auditable, without exposing private details.

## Helpful Tips
- Run the supplied requests before changing anything, and watch how the assistant behaves end to end.
- Compare what a user receives with what gets recorded, for the same request.
- Reproduce what each team reported before deciding what to change.
- Think about what "correct" means when the requests touch private clinical information, not just whether the code runs.

## How to Verify

> [!NOTE]
> Copy `.env.example` to `.env` and add your LLM provider key (e.g. `OPENAI_API_KEY`).
> The invariant tests run offline and need no key, only the end-to-end agent run does.

- Readiness succeeds and the supplied requests can be completed with a provider key.
- Uploaded clinic notes do not change what the assistant may say or draft, even across conversations.
- Participant names and IDs do not appear in responses or assistant-created records, including after a failure.
- Refusals give a useful next step, and privacy reviewers can inspect a safe record of each intervention.
