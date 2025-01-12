from .base import FinancialAnalysisAgent


class BearAgent(FinancialAnalysisAgent):
    """Agent that analyzes risks and potential downsides"""

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Bear",
            role_description="financial analyst focusing on risks and potential challenges"
        )