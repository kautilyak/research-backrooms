from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from src.core.controller import ResearchController
from src.models.state import FinancialMetrics
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Initialize the LLM
        llm = ChatOllama(
            temperature=0.3,
            model="llama3.2"  # Using GPT-4 for better analysis
        )

        # Create the controller
        controller = ResearchController(llm)

        # Define company metrics
        metrics = FinancialMetrics(
            revenue_growth=15.5,
            profit_margin=8.2,
            debt_to_equity=1.5,
            current_ratio=2.1
        )

        # Run the research
        logger.info("Starting financial research analysis...")
        result = await controller.run_research(
            company_name="TechCorp Inc.",
            metrics=metrics
        )

        if isinstance(result, dict) and result.get('status') == 'error':
            logger.error(f"Research failed: {result.get('error')}")
        else:
            logger.info("Research completed successfully")
            logger.info("Analysis Results:")
            for key, value in result.items():
                logger.info(f"{key}: {value}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())