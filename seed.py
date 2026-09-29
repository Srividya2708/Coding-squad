"""Synthetic but realistic incident history (swap in your own post-mortems)."""
from agent import hs, BANK, init_bank

INCIDENTS = [
 "2026-03-04 payments-api p99 latency hit 9s with DB connection timeouts right after the 14:05 deploy of v2.31. Root cause: new ORM call opened a connection per request and exhausted the pool (max 50). Fix: rolled back v2.31 and raised pool to 120. Outcome: fix WORKED in 6 minutes. Restarting pods first FAILED, pool exhausted again in 2 minutes.",
 "2026-03-19 checkout-web 502 spike. Root cause: Redis maxmemory reached with allkeys-lru evicting session keys, users logged out mid-checkout. Fix: raised Redis memory to 8GB and added TTL to cart keys. Outcome: fix WORKED.",
 "2026-04-02 search-api slow queries, CPU 95% on primary Postgres. Root cause: missing index on orders(customer_id, created_at) after a schema migration. Fix: CREATE INDEX CONCURRENTLY. Outcome: WORKED. Scaling up the DB instance FAILED, cost doubled with no improvement.",
 "2026-04-21 payments-api 5xx after deploy v2.38. Root cause: same connection pool exhaustion pattern, a retry loop held connections open. Fix: rollback then patch retry backoff. Outcome: WORKED. Raising pool alone FAILED to stop it because the retries consumed the extra connections.",
 "2026-05-08 notifications-worker queue backlog of 2M messages. Root cause: downstream SMTP provider rate-limited us. Fix: enabled provider failover and throttled sends to 200/s. Outcome: WORKED.",
 "2026-05-30 inventory-api latency 6s after deploy v1.12. Root cause: N+1 queries in a new endpoint plus default pool size of 20. Fix: eager loading and rollback. Outcome: WORKED. Pod restart FAILED.",
 "Team runbook preference: on any latency alert within 30 minutes of a deploy, check deploy diff and DB pool metrics before scaling anything. Rollback is preferred over hotfix during business hours.",
]

if __name__ == "__main__":
    init_bank()
    hs.retain_batch(bank_id=BANK, retain_async=False,
                    items=[{"content": t, "context": "post-mortem"} for t in INCIDENTS],
                    document_id="postmortems-h1-2026")
    print(f"Seeded {len(INCIDENTS)} incidents into bank '{BANK}'.")
