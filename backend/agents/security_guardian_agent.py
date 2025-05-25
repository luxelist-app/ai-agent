from __future__ import annotations

import asyncio
import json
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Dict, List

from backend.agents.base_agent import AgentResponse, BaseAgent

SECRET_PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret": re.compile(r"(?i)aws.*[=:\"']([0-9a-zA-Z/+]{40})"),
    "GCP Service Key": re.compile(r"\"type\":\\s*\"service_account\""),
    "JWT": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}"),
    "Generic 32-char hex": re.compile(r"[a-f0-9]{32}"),
}

BANDIT_CMD = "bandit -q -r {path} -f json"

class Agent(BaseAgent):
    """Security Guardian – static scanner & secret-detector."""

    async def handle(self, message: str, context: Dict) -> AgentResponse:
        msg_lower = message.lower().strip()

        # -------- Path scan mode --------
        if msg_lower.startswith("scan path="):
            target = msg_lower.split("=", 1)[1].strip()
            return await self._scan_path(Path(target))

        # -------- Snippet scan mode --------
        snippets = self._extract_snippets(message)
        if snippets:
            return self._scan_snippets(snippets)

        # Fallback: guidance
        help_text = dedent(
            """
            🛡 **Security Guardian** – How to use  
            • *Snippet scan*: paste code inside ```triple back-ticks``` and ask “scan this”.  
            • *Path scan*: `scan path=backend/` (runs Bandit recursively).  
            """
        )
        return AgentResponse(content=help_text)

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #

    async def _scan_path(self, path: Path) -> AgentResponse:
        if not path.exists():
            return AgentResponse(content=f"❌ Path `{path}` does not exist.")

        cmd = shlex.split(BANDIT_CMD.format(path=str(path)))
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = await proc.communicate(timeout=120)
            if err:
                return AgentResponse(content=f"Bandit error:\n```\n{err.decode()}```")

            findings = json.loads(out or b"{}").get("results", [])
            if not findings:
                return AgentResponse(content=f"✅ No Bandit issues found in `{path}`.")

            report_lines = [
                f"*{f['filename']}* L{f['line_number']} – **{f['issue_text']}** "
                f"({f['test_id']})"
                for f in findings
            ][:20]  # show top 20
            report = "\n".join(report_lines)
            return AgentResponse(
                content=f"⚠️ Bandit found {len(findings)} issue(s):\n" + report
            )
        except Exception as e:
            return AgentResponse(content=f"Bandit run failed: {e}")

    def _scan_snippets(self, snippets: List[str]) -> AgentResponse:
        hits: List[str] = []
        for snip in snippets:
            for name, pat in SECRET_PATTERNS.items():
                if pat.search(snip):
                    hits.append(f"• **{name}** detected")

        if hits:
            return AgentResponse(
                content="⚠️ Potential secrets found:\n" + "\n".join(sorted(set(hits)))
            )
        return AgentResponse(content="✅ No obvious secrets or keys detected.")

    @staticmethod
    def _extract_snippets(text: str) -> List[str]:
        """Return list of code blocks delimited by back-ticks."""
        fence = re.compile(r"```(?:[\w+]+\n)?(.*?)```", re.S)
        return [m.group(1) for m in fence.finditer(text)]
