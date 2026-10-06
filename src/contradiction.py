"""
Contradiction Detection module.

This combines three complementary layers:
1. RULE-BASED NUMERIC DIFFING (Layer 1a).
   Deterministic extraction of numbers and dates with trailing punctuation
   stripped. Catches fine-grained numeric substitutions that NLI models miss.
2. DOMAIN ENTITY / ROLE ALIGNMENT (Layer 1b).
   Detects when claim and evidence substitute different mutually-exclusive
   entities/roles (e.g. "finance director" vs "department head") for the same slot.
   Operates alongside NLI to prevent confident-Trusted false negatives.
3. NEURAL NLI MODEL (Layer 2, roberta-large-mnli).
   Evaluates full contextual semantics and predicate-level polarity.
"""

import re
from transformers import pipeline

from src.claim_extraction import split_sentences
from src.similarity import semantic_similarity

NUMBER_PATTERN = re.compile(r"\d[\d,]*\.?\d*")

# Domain Entity & Role Taxonomy
ENTITY_CATEGORIES = {
    "ROLES_AND_AUTHORITIES": [
        "finance director",
        "department head",
        "reporting manager",
        "hr director",
        "finance department",
        "reporting manager and the finance department",
        "customer-facing roles",
        "customer-facing",
    ],
    "CHANNELS_AND_PLATFORMS": [
        "hr portal",
        "email",
    ],
    "EQUIPMENT": [
        "laptop",
        "external monitor",
    ],
    "CURRENCIES": [
        "usd",
        "inr",
        "eur",
    ],
    "CABIN_CLASS": [
        "economy class",
        "business class",
    ],
}

# Cache NLI model at module load
_NLI_PIPELINE = pipeline(
    "text-classification",
    model="roberta-large-mnli",
    device=-1
)


def extract_numbers(text: str):
    """
    Extracts numbers from text, stripping trailing sentence punctuation
    (e.g., '1.' -> '1', '12,' -> '12') to prevent false mismatch.
    """
    raw = NUMBER_PATTERN.findall(text)
    cleaned = set()
    for r in raw:
        c = r.rstrip(".,;:!?'\"").replace(",", "")
        if c:
            cleaned.add(c)
    return cleaned


def extract_domain_entities(text: str):
    """
    Extracts recognized domain entities and roles grouped by semantic category.
    """
    text_lower = text.lower()
    found = {}
    for category, entities in ENTITY_CATEGORIES.items():
        matched = set()
        for ent in entities:
            if re.search(r"\b" + re.escape(ent) + r"\b", text_lower):
                matched.add(ent)
        if matched:
            found[category] = matched
    return found


def check_entity_mismatch(claim: str, evidence: str, similarity_score: float):
    """
    Flags when claim and evidence reference different named entities/roles
    for the same functional slot under strong semantic similarity.
    Incorporates sentence-level predicate binding: restricts checks to the
    most predicate-relevant sentence in a multi-sentence evidence passage,
    preventing co-occurring entities in adjacent sentences from masking role swaps.
    """
    if similarity_score < 0.35:
        return None

    claim_entities = extract_domain_entities(claim)
    if not claim_entities:
        return None

    ev_sentences = split_sentences(evidence)
    passage_entities = extract_domain_entities(evidence)

    # Restrict check to the evidence sentence most relevant to the claim's predicate
    if len(ev_sentences) > 1:
        scored_sents = [(s, semantic_similarity(claim, s)) for s in ev_sentences]
        scored_sents.sort(key=lambda x: x[1], reverse=True)
        best_sentence, best_sim = scored_sents[0]
    else:
        best_sentence = evidence
        best_sim = similarity_score

    best_sent_entities = extract_domain_entities(best_sentence)

    for cat, c_ents in claim_entities.items():
        if cat in best_sent_entities:
            best_ents = best_sent_entities[cat]
            unmatched = c_ents - best_ents
            if unmatched and not (c_ents & best_ents):
                # If the claimed entity exists elsewhere in the passage, it's a binding mismatch
                if cat in passage_entities and (c_ents & passage_entities[cat]):
                    return (
                        "CONTRADICTION",
                        f"Role/entity binding mismatch detected in category '{cat}': claim binds {sorted(c_ents)} "
                        f"to predicate/rule where evidence sentence specifies {sorted(best_ents)} "
                        f"(entity {sorted(c_ents & passage_entities[cat])} exists in passage but is bound to a different rule) [ENTITY_PRESENT_WRONG_BINDING]."
                    )
                else:
                    return (
                        "CONTRADICTION",
                        f"Entity/role substitution detected in category '{cat}': claim references {sorted(unmatched)} "
                        f"where evidence specifies {sorted(best_ents)}."
                    )
        elif cat in passage_entities:
            # Entity exists in passage, but best sentence has NO entity of this category
            pass_ents = passage_entities[cat]
            if c_ents.issubset(pass_ents) and best_sim >= 0.40:
                return (
                    "CONTRADICTION",
                    f"Role/entity binding mismatch detected in category '{cat}': claim binds {sorted(c_ents)} "
                    f"to predicate/rule where evidence sentence does not support this entity "
                    f"(entity {sorted(c_ents)} exists in passage but is bound to a different rule) [ENTITY_PRESENT_WRONG_BINDING]."
                )
            elif not (c_ents & pass_ents):
                return (
                    "CONTRADICTION",
                    f"Entity/role substitution detected in category '{cat}': claim references {sorted(c_ents - pass_ents)} "
                    f"where evidence specifies {sorted(pass_ents)}."
                )

    return None


def _nli_fallback(claim: str, evidence: str, similarity_score: float):
    """
    Real NLI model (roberta-large-mnli) for claims that pass the rule-based numeric/entity layers.
    Premise is evidence, hypothesis is claim.
    """
    result = _NLI_PIPELINE({"text": evidence, "text_pair": claim})
    if isinstance(result, list):
        result = result[0]

    label = result["label"].upper()
    score = round(float(result["score"]), 3)

    if label == "CONTRADICTION":
        return "CONTRADICTION", f"NLI model detected contradiction with evidence (confidence: {score})."
    elif label == "ENTAILMENT":
        return "ENTAILMENT", f"NLI model confirmed entailment from evidence (confidence: {score})."
    else:
        return "NEUTRAL", f"Evidence neither entails nor directly contradicts claim (confidence: {score})."


def check_contradiction(claim: str, evidence: str, similarity_score: float):
    """
    Returns (label, reason) where label in
    {"ENTAILMENT", "CONTRADICTION", "NEUTRAL"}.
    """
    claim_numbers = extract_numbers(claim)
    evidence_numbers = extract_numbers(evidence)

    # Layer 1a: Deterministic numeric mismatch
    if claim_numbers and evidence_numbers:
        if not claim_numbers.issubset(evidence_numbers):
            unmatched = claim_numbers - evidence_numbers
            if unmatched and similarity_score >= 0.35:
                return (
                    "CONTRADICTION",
                    f"Claim contains number(s) {sorted(unmatched)} not present in evidence "
                    f"(evidence contains {sorted(evidence_numbers)}); likely numeric substitution."
                )

    # Layer 1b: Domain Entity / Role mismatch
    entity_check = check_entity_mismatch(claim, evidence, similarity_score)
    if entity_check is not None:
        return entity_check

    # Layer 2: Defer semantic and negation contradictions to RoBERTa-large-MNLI
    return _nli_fallback(claim, evidence, similarity_score)


if __name__ == "__main__":
    # Test case 1: numeric extraction with trailing punctuation ("age of 1.")
    test_text = "Adoption leave of 12 weeks is available to employees who legally adopt a child under the age of 1."
    extracted = extract_numbers(test_text)
    assert extracted == {"12", "1"}, f"Expected {{'12', '1'}}, got {extracted}"
    print("Test 1 passed: extract_numbers correctly strips trailing punctuation ->", extracted)

    # Test case 2: numeric substitution contradiction
    res1 = check_contradiction(
        "Employees are entitled to 30 annual paid leaves per calendar year.",
        "Employees are entitled to 20 annual paid leaves per calendar year.",
        0.9
    )
    print("Test 2 passed: numeric substitution caught ->", res1)
    assert res1[0] == "CONTRADICTION"

    # Test case 3: entity swap detection (reimb_013)
    res2 = check_contradiction(
        "A late claim requires written approval from the department head.",
        "Claims submitted after 30 days will not be processed except with written approval from the finance director.",
        0.65
    )
    print("Test 3 passed: entity swap caught ->", res2)
    assert res2[0] == "CONTRADICTION"
