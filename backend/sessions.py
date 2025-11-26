"""
Simple session management for conversation history.
Each user gets a session ID that tracks their conversation.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


class ConversationSession:
    """A single conversation session."""

    def __init__(self, session_id: str, max_messages: int = 50):
        self.session_id = session_id
        self.messages: List[Dict[str, str]] = []
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.max_messages = max_messages

    def add_exchange(self, human_msg: str, ai_msg: str):
        """Add a question-answer exchange."""
        self.messages.append({
            'human': human_msg,
            'ai': ai_msg,
            'timestamp': datetime.now().isoformat()
        })
        self.last_used = datetime.now()

        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_history_text(self) -> str:
        """Get conversation history as text for LLM context."""
        history_lines = []
        for msg in self.messages:
            history_lines.append(f"Human: {msg['human']}")
            history_lines.append(f"AI: {msg['ai']}")
        return '\n'.join(history_lines)

    def clear(self):
        """Clear all messages."""
        self.messages = []
        self.last_used = datetime.now()


class SessionManager:
    """Manages all conversation sessions."""

    def __init__(self, session_lifetime_hours: int = 24, max_messages: int = 50):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_lifetime = timedelta(hours=session_lifetime_hours)
        self.max_messages = max_messages

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        """Get existing session or create a new one."""
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_used = datetime.now()
            return session

        # Create new session
        new_id = session_id if session_id else str(uuid.uuid4())
        session = ConversationSession(new_id, self.max_messages)
        self.sessions[new_id] = session
        return session

    def cleanup_old_sessions(self):
        """Remove sessions that haven't been used recently."""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.last_used > self.session_lifetime
        ]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)


# Global session manager
session_manager: Optional[SessionManager] = None


def init_session_manager(config):
    """Initialize the global session manager."""
    global session_manager
    session_manager = SessionManager(
        session_lifetime_hours=config.SESSION_LIFETIME_HOURS,
        max_messages=config.MAX_MESSAGES_PER_SESSION
    )


def get_session_manager() -> SessionManager:
    """Get the session manager instance."""
    if session_manager is None:
        raise RuntimeError("Session manager not initialized")
    return session_manager
