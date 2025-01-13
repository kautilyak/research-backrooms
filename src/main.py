from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from src.core.controller import ResearchController
from src.models.state import FinancialMetrics
import asyncio, os
import logging
from src.data_sources.vantage import AlphaVantageClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Initialize the LLM
        llm = ChatOllama(
            temperature=0.3,
            model="llama3.2",
            num_ctx=16384,
        )

        # Create the controller
        controller = ResearchController(llm)

        

        alpha_vantage_client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
        financial_data = await alpha_vantage_client.get_company_financials("MSFT")  # Assuming TechCorp ticker is TECH
        
        # Calculate metrics from the raw financial data from AlphaVantage
        metrics = FinancialMetrics(**alpha_vantage_client.calculate_all_metrics(financial_data))

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