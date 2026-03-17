from mcp.server.fastmcp import FastMCP
from src.RAG.rag_pipeline import ask_rag

mcp = FastMCP("compliance-auditor")


@mcp.tool()
def audit_gdpr_compliance(company_text: str) -> str:
    """
    Analiza texto empresarial y verifica cumplimiento con GDPR.
    """

    from io import StringIO
    import sys

    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    try:
        response = ask_rag(company_text)
        buffer.write(response)
    finally:
        sys.stdout = sys_stdout

    return buffer.getvalue()


if __name__ == "__main__":
    mcp.run()