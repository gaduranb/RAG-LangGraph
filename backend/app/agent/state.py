from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State for the banking support agent."""
    messages: Annotated[list, add_messages] # Garantizo que se agregan mensajes correctamente en lugar de reemplazarlos
    question: str
    answer: Optional[str]
    citations: Optional[List[dict]]
    tool_calls: Optional[List[str]]
    is_out_of_scope: bool
    needs_holidays: bool
    retrieved_docs: Optional[str]  # RAG: Documentos recuperados formateados
