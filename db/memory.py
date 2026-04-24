from typing import Dict, Any, Optional


class SimpleInMemory:

    def __init__(self) -> None:
        self._memory: Dict[Any, Any] = {}

    def get(self, key: Any) -> Optional[Any]:
        if key not in self._memory:
            return
        
        return self._memory.get(key)

    def set(self, key: Any, value: Any) -> Optional[Any]:
        if key in self._memory:
            existing = self._memory[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                self._memory[key] = [existing, value]
        else:
            self._memory[key] = value

        return self._memory[key]

    def delete(self, key: Any) -> None:
        if key not in self._memory:
            return
        
        del self._memory[key]

    def exists(self, key: Any) -> bool:
        return bool(self._memory.get(key, None))
    
    def get_all(self):
        return self._memory