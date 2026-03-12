def build_audit_prompt(claim: str, evidence_blocks: list) -> str:

    if not evidence_blocks:
        evidence_text = "NO LEGAL TEXT FOUND"
    else:
        evidence_text = "\n\n".join(
            f"ARTICLE {e['article']}:\n{e['text'][:1200]}"
            for e in evidence_blocks
        )

    return f"""
You are a GDPR legal validator.

You MUST decide if the claim violates the law.

Rules:
- ONLY use the articles provided
- If article sets a requirement and claim contradicts → NON_COMPLIANT
- If claim follows requirement → COMPLIES
- If unrelated → NO_APPLIES
- Always choose an article number from the evidence

Return ONLY JSON:

{{
"result": "COMPLIES | NON_COMPLIANT | NO_APPLIES",
"article": "<number>",
"evidence": "<exact quote from article>",
"reason": "<one short sentence>"
}}

CLAIM:
{claim}

LEGAL ARTICLES:
{evidence_text}
"""


def build_nli_prompt(claim, article_text):
    return f"""
You are a strict legal validator.

Your task is to detect violation.

Important:
- If the law imposes a maximum or minimum deadline and the claim does not meet it → CONTRADICTION
- If the law requires a security measure and the claim omits it → CONTRADICTION
- If the claim satisfies the requirement → ENTAILMENT
- If unrelated → IRRELEVANT

Return only one word:
CONTRADICTION
ENTAILMENT
IRRELEVANT

CLAIM:
{claim}

LAW:
{article_text}
""".strip()

def build_applicability_prompt(claim, article_text):
    return f"""
You are a legal rule applicability classifier.

A legal article APPLIES only if it creates a concrete obligation,
prohibition, requirement, deadline, or security measure
that can be checked against the claim.

Definitions, principles, objectives, or general rights DO NOT APPLY.

Answer ONLY:
APPLIES
NOT_APPLIES

CLAIM:
{claim}

ARTICLE:
{article_text[:1200]}
"""


def generate_llm_justification(llm, claim, article, sentence, verdict):
    prompt = f"""
You are drafting a short legal justification.

Based strictly on the legal sentence and the claim,
write a concise justification (max 2 sentences).

Do NOT reinterpret the law.
Do NOT add new legal analysis.
Do NOT change the verdict.

VERDICT: {verdict}
ARTICLE: {article}
LEGAL SENTENCE:
"{sentence}"

CLAIM:
"{claim}"

Return only the justification paragraph.
"""

    return llm.invoke(prompt).content.strip()