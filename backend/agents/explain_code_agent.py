# backend/agents/explain_code_agent.py
from __future__ import annotations

import ast
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple

from backend.agents.base_agent import AgentResponse, BaseAgent

FENCE = re.compile(r"```(\w+)?\n(.*?)```", re.S)

class Agent(BaseAgent):
    """
    Explain-Code Agent

    Usage examples:
      explain:
      ```python
      def add(a, b): return a+b
      ```
    """

    async def handle(self, message: str, context: Dict) -> AgentResponse:
        blocks = self._extract_blocks(message)
        if not blocks:
            return AgentResponse(
                content=(
                    "ℹ️  Paste code inside triple back-ticks to get an explanation, e.g.\n\n"
                    "```js\nfunction add(a,b){return a+b;}\n```"
                )
            )

        reports = []
        for lang, code in blocks:
            lang = lang or self._guess_lang(code)
            if lang == "python":
                reports.append(self._explain_python(code))
            else:
                reports.append(self._explain_generic(lang, code))

        return AgentResponse(content="\n\n---\n\n".join(reports))

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_blocks(text: str) -> List[Tuple[str | None, str]]:
        return [(m.group(1), m.group(2)) for m in FENCE.finditer(text)]

    @staticmethod
    def _guess_lang(code: str) -> str:
        if "import " in code or "def " in code:
            return "python"
        if "#include" in code or "std::" in code:
            return "cpp"
        if "function " in code or "console.log" in code:
            return "javascript"
        if "class " in code and "public:" in code:
            return "cpp"
        return "plaintext"

    # ---------- Python special-case ----------------------------------- #
    def _explain_python(self, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"❌ Python parse error: {e}"

        funcs, classes, imports = [], [], []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None)
                names = [n.name for n in node.names]
                imports.append(f"{mod or ''}{' → ' if mod else ''}{', '.join(names)}")

        summary = [
            "### 🐍 Python snippet analysis",
            f"*Lines*: {len(code.splitlines())}",
        ]
        if imports:
            summary.append(f"*Imports*: {', '.join(imports)}")
        if classes:
            summary.append(f"*Classes*: {', '.join(classes)}")
        if funcs:
            summary.append(f"*Functions*: {', '.join(funcs)}")

        docstring = ast.get_docstring(tree)
        if docstring:
            summary.append("\n*Top-level docstring*: " + textwrap.shorten(docstring, 120))

        return "\n".join(summary)

    # ---------- Fallback for other languages -------------------------- #
    def _explain_generic(self, lang: str, code: str) -> str:
        lines = code.splitlines()
        total = len(lines)
        comment_lines = len([l for l in lines if l.strip().startswith(("//", "#", "/*"))])
        keywords = {
            "class ": "Classes",
            "def ": "Functions",
            "function ": "Functions",
            "import ": "Imports / Includes",
            "#include": "Imports / Includes",
        }
        found: Dict[str, List[str]] = {v: [] for v in keywords.values()}

        for ln in lines:
            for kw, group in keywords.items():
                if kw in ln:
                    found[group].append(ln.strip())

        report = [f"### 📄 {lang.capitalize()} snippet analysis", f"*Lines*: {total}"]
        if comment_lines:
            pct = (comment_lines / total) * 100
            report.append(f"*Comment lines*: {comment_lines} ({pct:.0f}%)")
        for group, arr in found.items():
            if arr:
                first_three = [textwrap.shorten(x, 60) for x in arr[:3]]
                report.append(f"*{group}*: {len(arr)} (e.g., {', '.join(first_three)})")

        return "\n".join(report)
