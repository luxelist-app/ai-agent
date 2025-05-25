
import yaml
import re
import importlib.util
import pathlib
from typing import Dict, Any
from backend.agents.base_agent import AgentResponse

class AgentRouter:
    def __init__(self, manifest_path: str):
        self.manifest_path = pathlib.Path(manifest_path).resolve()
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = yaml.safe_load(f)

        self._load_agents()

    def _load_agents(self):
        self.routes = []
        manifest_dir = self.manifest_path.parent
        self.agents = {}
        for name, spec in self.manifest['agents'].items():
            file_path = manifest_dir / spec['file']
            module_name = f"_agent_{name}"
            spec_loader = importlib.util.spec_from_file_location(module_name, file_path)
            mod = importlib.util.module_from_spec(spec_loader)
            spec_loader.loader.exec_module(mod)
            agent_cls_name = spec.get('class', 'Agent')
            agent_cls = getattr(mod, agent_cls_name)
            self.agents[name] = agent_cls(llm=None)  # or pass your actual LLM instance later
        for route in self.manifest['routes']:
            pattern = re.compile(route['pattern'], re.I)
            self.routes.append((pattern, route['agent']))

    async def chat(self, message: str, context: Dict[str, Any] | None = None):
        context = context or {}
        target_name = 'general'
        for pattern, agent_name in self.routes:
            if pattern.search(message):
                target_name = agent_name
                break
        agent = self.agents[target_name]
        result = await agent.handle(message, context)
        if isinstance(result, AgentResponse):
            return result
        return AgentResponse(content=str(result))
