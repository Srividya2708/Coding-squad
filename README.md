# Incident Memory Agent (Hackathon: Hindsight)

An on-call SRE copilot that remembers every incident, root cause, and whether each fix worked or failed.
Without memory it gives generic advice ("restart pods, scale up"). With Hindsight it says
"this is the third connection-pool incident after a deploy; restarting FAILED twice, rollback WORKED."

## How Hindsight memory is used
| Op | Where | Purpose |
|---|---|---|
| `retain_batch` | `seed.py` | Load post-mortems as memories |
| `recall` | `agent.triage` | Pull similar past incidents (semantic + keyword + graph + temporal) |
| `retain` | `agent.log_outcome` | Close the loop: store what worked/failed so the agent improves |
| `reflect` | `agent.briefing` | Synthesize recurring patterns across incidents |
| bank mission/disposition | `agent.init_bank` | Skeptical SRE persona |

## Run
```bash
pip install -r requirements.txt
export GROQ_API_KEY=...            # groq.com free tier
export HINDSIGHT_URL=https://api.hindsight.vectorize.io   # confirm your Cloud URL in the console; or http://localhost:8888
export HINDSIGHT_API_KEY=...       # Cloud only (promo: MEMHACK99 in billing)
python seed.py
python demo.py
```
Demo shows: Round 1 generic -> Round 2 memory-grounded -> learns from outcome -> Round 3 a different service benefits.

## Ideas to extend
Slack/PagerDuty webhook input, Streamlit UI showing recalled memories, memory-defense on untrusted alert text.
