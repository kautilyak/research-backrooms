from .base import FinancialAnalysisAgent


class BullAgent(FinancialAnalysisAgent):
    """Agent that analyzes positive aspects and growth opportunities"""

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Bull",
            role_description="financial analyst focusing on growth opportunities and positive indicators"
        )

