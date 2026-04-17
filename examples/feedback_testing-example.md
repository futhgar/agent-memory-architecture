---
name: Testing preferences
description: How I want the agent to approach tests for the TodoList API. Based on past incidents and personal workflow.
type: feedback
---

# Testing preferences

The following is how I want the agent to handle tests in this project. Not general advice — specific to this codebase.

## Rules

**Integration tests hit a real database.** Do not mock SQLAlchemy sessions or the Postgres driver. The test fixtures spin up an ephemeral Postgres in a Docker container; use that.

**Why:** Q4 2025 we had a production data-migration failure that passed all mocked tests. The mock didn't model a constraint interaction that real Postgres enforces. Lost half a day. Never again.

**How to apply:** If you see a mocked DB session in a test, flag it for removal. Rewrite to use the real fixture.

---

**Test files match source files 1:1.** `src/todolist/auth.py` → `tests/auth/test_auth.py`. Don't create sprawling "test_all_the_things.py" files.

**Why:** Debuggability. When a test fails in CI, I want to know which module is broken from the file path alone, without opening the file.

**How to apply:** New test files follow this pattern. If there's existing drift, leave it unless you're already editing nearby code.

---

**Pytest, not unittest.** I'm not converting existing unittest files unless they break — but any new tests are pytest.

**Why:** Cleaner fixtures, better parametrize, fewer lines. Conversion is tech debt I'm paying off opportunistically.

**How to apply:** If you need to add a test next to an existing unittest file, the new one can still be pytest. They coexist fine.

---

**Coverage target is 80%, not 100%.** I don't care about covering glue code (view routing, framework internals). Aim for 80% on business logic, ignore the rest.

**Why:** 100% coverage chases bad incentives. Forces silly tests. I'd rather have 80% with good assertions than 100% with 20% theater.

**How to apply:** Don't suggest adding tests for pure routing / DI / framework boilerplate. Focus test suggestions on business logic.
