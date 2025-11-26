"""
Simple wrapper for the LLM model.
Handles model loading and inference.
"""
import logging
from typing import Optional
from langchain_community.llms import CTransformers
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class JenkinsBot:
    """Simple chatbot for Jenkins questions."""

    def __init__(self, model_name: str, model_file: str, max_new_tokens: int = 512, temperature: float = 0.7):
        self.model_name = model_name
        self.model_file = model_file
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.llm = None
        self.chain = None

    def load(self):
        """Load the model."""
        logger.info(f"Loading model: {self.model_name}")
        try:
            self.llm = CTransformers(
                model=self.model_name,
                model_file=self.model_file,
                config={
                    'max_new_tokens': self.max_new_tokens,
                    'temperature': self.temperature,
                }
            )

            # Create the prompt template
            template = """[INST] <<SYS>>
You are a helpful Jenkins expert. Answer questions about Jenkins clearly and concisely.
{persona}

Previous conversation:
{history}
<</SYS>>

{question} [/INST]"""

            prompt = PromptTemplate(
                template=template,
                input_variables=["question", "persona", "history"]
            )

            # Create the chain
            self.chain = prompt | self.llm

            logger.info("Model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate_response(self, question: str, history: str = "", persona: str = "") -> str:
        """Generate a response to a question."""
        if not self.chain:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            response = self.chain.invoke({
                "question": question,
                "history": history,
                "persona": persona
            })
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.llm is not None and self.chain is not None


# Global bot instance
bot: Optional[JenkinsBot] = None


def init_bot(config):
    """Initialize the global bot instance."""
    global bot
    bot = JenkinsBot(
        model_name=config.MODEL_NAME,
        model_file=config.MODEL_FILE,
        max_new_tokens=config.MAX_NEW_TOKENS,
        temperature=config.TEMPERATURE
    )
    bot.load()


def get_bot() -> JenkinsBot:
    """Get the bot instance."""
    if bot is None:
        raise RuntimeError("Bot not initialized")
    return bot