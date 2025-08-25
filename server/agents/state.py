from typing import Dict, List, Optional, TypedDict, Any, Union

class GraphState(TypedDict, total=False):
    """State for the graph with typed dictionary."""
    user_input: str
    intent: str = "query"  # "query" | "results" | "analysis"
    generated_sql: Optional[str]
    validated_sql: Optional[str] = None
    validation_report: Dict[str, Any] = {}
    execution_result: Optional[List[Dict[str, Any]]] = None
    final_answer: Optional[str] = None
    error: Optional[str] = None
    
    @classmethod
    def create(cls, **kwargs) -> 'GraphState':
        """Create a new GraphState instance with default values."""
        state: GraphState = {
            'user_input': '',
            'generated_sql': None,
            'validated_sql': None,
            'validation_report': {},
            'execution_result': None,
            'final_answer': None,
            'error': None,
            **kwargs
        }
        return state
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GraphState':
        """Create a GraphState from a dictionary."""
        return cls.create(**data)
