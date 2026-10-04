"""Run trifecta-check exactly as its CLI does (all three scanners), and print JSON.
Its CLI prints only a Rich table, so the same calls are made here."""
import json
import sys
from pathlib import Path

from trifecta_check.analyzer import TrifectaAnalyzer
from trifecta_check.scanners.auto_gpt import AutoGPTScanner
from trifecta_check.scanners.langchain import LangChainScanner
from trifecta_check.scanners.mcp import MCPScanner

result = TrifectaAnalyzer([AutoGPTScanner(), MCPScanner(), LangChainScanner()]).analyze(Path(sys.argv[1]))
print(json.dumps({"has_trifecta": result.has_trifecta(), "capabilities": sorted({f.capability.name for f in result.findings}),
                  "findings": [f.description for f in result.findings], "errors": result.errors}))
