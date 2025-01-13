import aiohttp
import os
import logging
import requests


# Define company metrics
# Get financial data from Alpha Vantage
class AlphaVantageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    async def get_company_financials(self, ticker: str) -> dict:
        """Fetch financial data for a company from Alpha Vantage API"""
        
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"Alpha Vantage API error: {response.status_code}")
        data = response.json()
        if "Error Message" in data:
            raise Exception(f"Alpha Vantage API error: {data['Error Message']}")
        return data
            
    # Example response fields from Alpha Vantage OVERVIEW endpoint:
    # 'Symbol': 'MSFT'
    # 'AssetType': 'Common Stock'
    # 'Name': 'Microsoft Corporation'
    # 'Description': 'Microsoft Corporation is an American multinational technology company...'
    # 'CIK': '789019'
    # 'Exchange': 'NASDAQ'
    # 'Currency': 'USD'
    # 'Country': 'USA'
    # 'Sector': 'TECHNOLOGY'
    # 'Industry': 'SERVICES-PREPACKAGED SOFTWARE'
    # 'Address': 'ONE MICROSOFT WAY, REDMOND, WA, US'
    # 'OfficialSite': 'https://www.microsoft.com'
    # 'FiscalYearEnd': 'June'
    # 'LatestQuarter': '2024-09-30'
    # 'MarketCapitalization': '3114842980000'
    # 'EBITDA': '136551997000'
    # 'PERatio': '34.6'
    # 'PEGRatio': '2.199'
    # 'BookValue': '38.69'
    # 'DividendPerShare': '3.08'
    # 'DividendYield': '0.0079'
    # 'EPS': '12.11'
    # 'RevenuePerShareTTM': '34.2'
    # 'ProfitMargin': '0.356'
    # 'OperatingMarginTTM': '0.466'
    # 'ReturnOnAssetsTTM': '0.146'
    # 'ReturnOnEquityTTM': '0.356'
    # 'RevenueTTM': '254189994000'
    # 'GrossProfitTTM': '176278995000'
    # 'DilutedEPSTTM': '12.11'
    # 'QuarterlyEarningsGrowthYOY': '0.104'
    # 'QuarterlyRevenueGrowthYOY': '0.16'
    # 'SharesOutstanding': '7434880000'

    def calculate_all_metrics(self, financial_data: dict) -> dict:
        """Calculate all financial metrics from Alpha Vantage data"""
        return {
            "revenue_growth": float(financial_data.get('QuarterlyRevenueGrowthYOY', 0)),
            "profit_margin": float(financial_data.get('ProfitMargin', 0)),
            "return_on_assets": float(financial_data.get('ReturnOnAssetsTTM', 0)),
            "return_on_equity": float(financial_data.get('ReturnOnEquityTTM', 0)),
            "earnings_per_share": float(financial_data.get('EPS', 0)),
            "pe_ratio": float(financial_data.get('PERatio', 0)),
            "peg_ratio": float(financial_data.get('PEGRatio', 0)),
            "book_value": float(financial_data.get('BookValue', 0)),
            "dividend_per_share": float(financial_data.get('DividendPerShare', 0)),
            "dividend_yield": float(financial_data.get('DividendYield', 0)),
            "revenue_per_share": float(financial_data.get('RevenuePerShareTTM', 0)),
            "operating_margin": float(financial_data.get('OperatingMarginTTM', 0)),
            "gross_profit": float(financial_data.get('GrossProfitTTM', 0)),
            "quarterly_earnings_growth": float(financial_data.get('QuarterlyEarningsGrowthYOY', 0)),
            "market_cap": float(financial_data.get('MarketCapitalization', 0)),
            "ebitda": float(financial_data.get('EBITDA', 0))
        }


