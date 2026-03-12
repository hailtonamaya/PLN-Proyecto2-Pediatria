from langchain_ollama import ChatOllama
from pipeline.RAG2 import retrieve_evidence
from pipeline.auditor_promps_builts import build_applicability_prompt, build_nli_prompt, generate_llm_justification
import re
import json

LLM_MODEL = "llama3:8b"

def extract_field(patterns, text):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def parse_llm_audit(text: str):
    try:
        return json.loads(text)
    except:
        return {
            "result": "ERROR",
            "article": "NONE",
            "evidence": "",
            "reason": "Model returned invalid format"
        }


def analyze_claim(claim, evidence_blocks, llm):

    applicable_articles = []

    # ---------- STEP 1: FIND GOVERNING ARTICLE ----------
    for art in evidence_blocks:
        print(f"[DEBUG] Checking applicability Article {art['article']}")

        prompt = build_applicability_prompt(claim, art["text"])
        decision = llm.invoke(prompt).content.strip().upper()

        if decision == "APPLIES":
            applicable_articles.append(art)

    if not applicable_articles:
        return {
            "result": "NO_APPLIES",
            "article": "NONE",
            "evidence": "",
            "reason": "No governing article found"
        }

    # ---------- STEP 2: NOW DO NLI ----------
    best_match = None
    best_priority = -1

    priority_map = {
        "CONTRADICTION": 3,
        "ENTAILMENT": 2,
        "IRRELEVANT": 1
    }

    for art in applicable_articles:
        print(f"[DEBUG] NLI against governing Article {art['article']}")

        prompt = build_nli_prompt(claim, art["text"])
        label = llm.invoke(prompt).content.strip().upper()

        if label not in priority_map:
            continue

        if priority_map[label] > best_priority:
            best_priority = priority_map[label]
            best_match = (label, art)

    if best_match is None:
        return {
            "result": "NO_APPLIES",
            "article": applicable_articles[0]["article"],
            "evidence": applicable_articles[0]["text"][:300],
            "reason": "Article applies but no logical relation detected"
        }

    label, art = best_match

    if label == "CONTRADICTION":
        result = "NON_COMPLIANT"
    elif label == "ENTAILMENT":
        result = "COMPLIES"
    else:
        result = "NO_APPLIES"

    return {
        "result": result,
        "article": art["article"],
        "evidence": art["text"][:300],
        "reason": f"NLI classification: {label}"
    }

def audit_company_text(company_text: str):
    print("Claims detected in company text:")
    claims = company_text.split("\n")
    claims = [c.strip() for c in claims if c.strip()]
    llm = ChatOllama(model=LLM_MODEL)

    report = []

    for claim in claims:
        print(f"\n[DEBUG] Processing claim: \"{claim}\"")
        evidence = retrieve_evidence(claim, top_k=5)
        parsed = analyze_claim(claim, evidence, llm)

        report.append({
            "claim": claim,
            **parsed
        })

    generate_report(report)

def generate_report(results):

    print("\n==============================")
    print("REPORTE DE AUDITORÍA GDPR")
    print("==============================\n")

    llm = ChatOllama(model=LLM_MODEL)

    critical = False

    for i, r in enumerate(results, 1):

        result = r.get("result", "ERROR").upper()
        article = r.get("article", "NONE")
        evidence = r.get("evidence", "No evidence returned")
        justification = generate_llm_justification(
            llm,
            r["claim"],
            article,
            evidence,
            result
        )
        if result == "NON_COMPLIANT":
            icon = "❌"
            critical = True
            verdict = "NO CUMPLE"
        elif result == "COMPLIES":
            icon = "✔"
            verdict = "CUMPLE"
        else:
            icon = "➖"
            verdict = "NO APLICA"

        print(f"AFIRMACION {i}:")
        print(f"\"{r['claim']}\"\n")

        print(f"VEREDICTO: {icon} {verdict}")
        print(f"ARTÍCULO: {article}")

        #print("\nEVIDENCIA LEGAL:")
        #print(f"\"{evidence}\"")

        print("\nJUSTIFICACIÓN:")
        print(justification)

        print("\n--------------------------------\n")

    print("CONCLUSIÓN GENERAL:")
    if critical:
        print("La organización presenta incumplimientos normativos.")
    else:
        print("La organización cumple con la normativa evaluada.")