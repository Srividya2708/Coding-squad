"""Learning-curve demo: same alert class, before vs after memory."""
from agent import init_bank, triage, log_outcome, briefing

def show(title, text):
    print(f"\n{'='*70}\n{title}\n{'='*70}\n{text}")

A1 = ("orders-api p99 latency 8.5s, 502s from gateway, logs show 'timeout acquiring "
      "connection from pool'. Started 6 minutes after the v3.4 deploy.")
A2 = ("billing-api latency 10s and 5xx, 'connection pool exhausted' errors, "
      "started right after the v5.1 deploy.")

if __name__ == "__main__":
    init_bank()
    show("ROUND 1 - NO MEMORY (generic LLM)", triage(A1, use_memory=False)[0])

    ans, mems = triage(A1)
    show(f"ROUND 2 - WITH HINDSIGHT MEMORY ({len(mems)} memories recalled)", ans)

    # The on-call engineer confirms what actually happened -> agent learns.
    log_outcome(A1, "retry loop in v3.4 held DB connections open",
                "rollback to v3.3, then patched retry backoff", worked=True)

    ans, mems = triage(A2)
    show("ROUND 3 - NEW SERVICE, LEARNED PATTERN APPLIES", ans)

    show("REFLECT - what recurring failure patterns do we have?",
         briefing("What recurring incident patterns and failed fixes should on-call know about?"))
