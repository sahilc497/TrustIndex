"""
Claim Extraction module.

MVP implementation: splits a generated answer into atomic-ish claims using
simple heuristics (sentence boundaries + coordinating conjunctions).

PRODUCTION UPGRADE PATH:
Replace `extract_claims()` with an LLM-based extractor. Prompt template:

    "Break the following answer into a JSON list of independent, atomic
    factual claims. Resolve any pronouns. Each claim must state exactly
    one fact and be understandable on its own.\n\nAnswer: {answer}"

This keeps the same function signature (str -> List[str]) so the rest of
the pipeline doesn't need to change when you swap in the LLM version.
"""

import re


COORDINATORS = re.compile(r"\s*,\s*(?:and|but)\s+|\s+(?:and|but)\s+", re.IGNORECASE)

VERB_PATTERN = re.compile(
    r"\b(?:is|are|was|were|be|been|being|have|has|had|do|does|did|can|could|shall|should|will|would|may|might|must|require|requires|required|receive|receives|received|provide|provides|provided|apply|applies|applied|confirm|confirms|confirmed|submit|submits|submitted|pay|pays|paid|entitle|entitles|entitled)\b",
    re.IGNORECASE
)


def split_sentences(text: str):
    # simple sentence splitter; good enough for policy-style short answers
    text = text.strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def extract_claims(answer: str):
    """
    Returns a list of atomic claim strings extracted from the answer.
    Splits compound claims at coordinating conjunctions only when both
    conjoined segments express complete propositions (contain verbal predicates)
    or are explicitly delineated by punctuation, avoiding splitting compound noun phrases.
    """
    claims = []
    for sentence in split_sentences(answer):
        matches = list(COORDINATORS.finditer(sentence))
        if not matches:
            claims.append(sentence.strip().rstrip("."))
            continue

        split_points = []
        current_part_start = 0

        for m in matches:
            left_part = sentence[current_part_start:m.start()].strip()
            right_part = sentence[m.end():].strip()
            has_comma = "," in sentence[m.start()-1:m.start()+1]
            left_has_verb = bool(VERB_PATTERN.search(left_part))
            right_has_verb = bool(VERB_PATTERN.search(right_part))

            if (has_comma and right_has_verb) or (left_has_verb and right_has_verb):
                split_points.append((m.start(), m.end()))
                current_part_start = m.end()

        if not split_points:
            claims.append(sentence.strip().rstrip("."))
        else:
            prev = 0
            for start, end in split_points:
                part = sentence[prev:start].strip().rstrip(".,")
                if len(part) > 3:
                    claims.append(part)
                prev = end
            tail = sentence[prev:].strip().rstrip(".,")
            if len(tail) > 3:
                claims.append(tail)

    return claims if claims else [answer.strip()]


if __name__ == "__main__":
    tests = [
        "Employees are entitled to 20 annual paid leaves per calendar year.",
        "Yes, unused annual leave can be carried forward for a maximum of 1 year.",
        "Claims above 5,000 INR require approval from both the reporting manager and the finance department.",
    ]
    for t in tests:
        print(t, "->", extract_claims(t))
