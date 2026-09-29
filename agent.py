"""On-call SRE copilot whose value comes from Hindsight memory."""
import os, time
from hindsight_client import Hindsight
from openai import OpenAI

BANK = os.getenv("BANK_ID", "oncall-sre")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
MISSION = ("I am an on-call SRE copilot. I remember every incident: symptoms, root cause, "
           "fix attempted and whether it worked. I recommend fixes that worked before and "
           "explicitly warn about fixes that failed.")

hs = Hindsight(base_url=os.getenv("HINDSIGHT_URL", "http://localhost:8888"),
               api_key=os.getenv("HINDSIGHT_API_KEY"))
llm = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])


def init_bank():
    try:
        hs.create_bank(bank_id=BANK, name="On-call SRE", mission=MISSION,
                       disposition={"skepticism": 4, "literalism": 3, "empathy": 2})
    except Exception as e:  # bank may already exist
        print(f"[bank] {e}")


def ask_llm(system, user, retries=3):
    for i in range(retries):  # Groq models occasionally error; retry
        try:
            r = llm.chat.completions.create(
                model=MODEL, temperature=0.2,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            return r.choices[0].message.content
        except Exception as e:
            print(f"[llm retry {i+1}] {e}"); time.sleep(1.5)
    return "LLM unavailable."


def recall_context(alert):
    res = hs.recall(bank_id=BANK, query=alert, budget="mid", max_tokens=3000,
                    types=["world", "experience", "observation"])
    return [r.text for r in res.results]


def triage(alert, use_memory=True):
    """Return (answer, memories_used)."""
    mems = recall_context(alert) if use_memory else []
    ctx = "\n".join(f"- {m}" for m in mems) or "(no prior incident memory)"
    system = ("You are an on-call SRE copilot. Give: 1) most likely root cause, 2) first 3 actions, "
              "3) what NOT to try. Be concise. If memory shows a past fix worked or failed, cite that "
              "incident explicitly. Never invent past incidents.")
    answer = ask_llm(system, f"ALERT:\n{alert}\n\nTEAM INCIDENT MEMORY:\n{ctx}")
    return answer, mems


def log_outcome(alert, root_cause, fix, worked):
    """Close the loop: the agent learns from what actually happened."""
    hs.retain(bank_id=BANK, context="incident outcome",
              content=(f"Incident: {alert} Root cause: {root_cause} Fix applied: {fix} "
                       f"Outcome: fix {'WORKED' if worked else 'FAILED'}."))


def briefing(topic):
    """Reflect: memory-grounded synthesis across many incidents."""
    return hs.reflect(bank_id=BANK, query=topic, budget="mid").text
