"""
Simple Flask backend for Jenkins chatbot.
Clean, easy-to-understand implementation.
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import config
from models import init_bot, get_bot
from sessions import init_session_manager, get_session_manager

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    bot = get_bot()
    return jsonify({
        'status': 'healthy',
        'model_loaded': bot.is_loaded()
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint."""
    try:
        data = request.get_json()

        # Validate input
        question = data.get('text', '').strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400

        if len(question) > 2000:
            return jsonify({'error': 'Question too long (max 2000 characters)'}), 400

        # Get optional fields
        persona = data.get('persona', '').strip()
        session_id = data.get('session_id')

        # Get or create session
        session_mgr = get_session_manager()
        session = session_mgr.get_or_create_session(session_id)

        # Get conversation history
        history = session.get_history_text()

        # Generate response
        bot = get_bot()
        response = bot.generate_response(
            question=question,
            history=history,
            persona=persona
        )

        # Save to history
        session.add_exchange(question, response)

        return jsonify({
            'prediction': response,
            'session_id': session.session_id,
            'message_count': len(session.messages)
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/session/clear', methods=['POST'])
def clear_session():
    """Clear a session's conversation history."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({'error': 'session_id required'}), 400

        session_mgr = get_session_manager()
        session = session_mgr.get_or_create_session(session_id)
        session.clear()

        return jsonify({
            'success': True,
            'message': 'Session cleared',
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Error clearing session: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/session/cleanup', methods=['POST'])
def cleanup_sessions():
    """Cleanup old sessions (admin endpoint)."""
    try:
        session_mgr = get_session_manager()
        removed = session_mgr.cleanup_old_sessions()

        return jsonify({
            'success': True,
            'removed_sessions': removed
        })

    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def initialize_app():
    """Initialize the application components."""
    logger.info("Initializing application...")

    # Initialize session manager
    init_session_manager(config)
    logger.info("Session manager initialized")

    # Initialize bot (this loads the model)
    logger.info("Loading LLM model... (this may take a few minutes on first run)")
    init_bot(config)
    logger.info("Bot initialized successfully")


if __name__ == '__main__':
    initialize_app()
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
