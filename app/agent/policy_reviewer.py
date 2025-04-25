import pandas as pd
import re

KEYWORDS = ["must", "should", "report", "ensure", "immediately", "required", "mandatory"]

def analyze_policies(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    flagged = []

    for line in lines:
        hits = [kw for kw in KEYWORDS if re.search(rf"\b{kw}\b", line, re.IGNORECASE)]
        if hits:
            flagged.append({
                "Sentence": line,
                "Keywords Found": ", ".join(hits),
                "Suggestion": "Clarify responsibility or action" if "should" in hits else "Check policy compliance"
            })

    return pd.DataFrame(flagged)
