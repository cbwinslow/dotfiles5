# Gemini Error Log – TEMPLATE

> Central log of runtime errors encountered by Gemini.

---

## Error 0001 – {{TIMESTAMP}}

- **Component:** memory
- **Context:** attempt to write memory entry after deployment.
- **Error Message:** `database is locked`
- **Stack Trace (optional):**
  - See external log file or debug dump.

- **User Impact:** deployment summary was not stored in memory.
- **Mitigation / Fix Attempted:** retry with backoff, then fall back to journal-only logging.
- **Status:** workaround
- **Related Journal Entry:** `JOURNAL_{{SESSION_ID}}` entry #4

---

## Error 0002 – {{TIMESTAMP}}

- **Component:** secrets
- **Context:** reading `.env` file for CI/CD credentials.
- **Error Message:** `.env file missing or unreadable`
- **User Impact:** cannot proceed with deployment.
- **Mitigation / Fix Attempted:** prompt user to configure secrets.
- **Status:** unresolved
- **Related Journal Entry:** entry #7
