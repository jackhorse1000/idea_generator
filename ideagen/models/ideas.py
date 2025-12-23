from typing import List, Dict, Any
from pydantic import BaseModel


def clean_dict(data: Any) -> Any:
    """Recursively remove None values and empty strings from dicts."""
    if isinstance(data, dict):
        return {
            k: clean_dict(v)
            for k, v in data.items()
            if v is not None and v != ""
        }
    elif isinstance(data, list):
        return [clean_dict(item) for item in data]
    return data


class IdeaResponse(BaseModel):
    """Response containing generated ideas. Each idea is a dict with name -> details."""
    ideas: List[Dict[str, Dict[str, Any]]]

    def to_clean_dict(self) -> dict:
        """Export ideas with None/empty values removed."""
        return {"ideas": clean_dict(self.ideas)}
