from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseParser(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse the source file and return a dictionary of candidate fields.
        Values can be raw/unnormalized; the normalization step will clean them.
        """
        pass
