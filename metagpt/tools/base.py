from abc import ABC, abstractmethod


class Tool(ABC):
    @abstractmethod
    async def build(self):
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    async def run(self, instruction: str) -> str:
        """Return the execution result."""
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    async def exit(self):
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    def reset(self):
        raise NotImplementedError("Please implement this method.")
