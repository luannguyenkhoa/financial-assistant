import os

if os.environ.get("ENV", "LOCAL") == "STAG":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from datetime import datetime

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase

from langchain.chains.llm_math.base import LLMMathChain
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.tools.google_serper import GoogleSerperRun
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper

from langchain.agents import Tool
from langchain.chains import RetrievalQA
from retriever import load_chunk_persist_pdf
from api_request import yfinance_price_request

# instantiate sql agent executor
included_tables = ["profile", "expense"]

def __datetime_tool():
    return Tool(
        name="Datetime",
        func=lambda x: datetime.now().isoformat(),
        description="An optional tool, fetch current date and time.",
    )

def build_sql_toolkit(llm):
    db = SQLDatabase.from_uri(os.environ.get("SUPABASE_URI"), include_tables=included_tables)
    return SQLDatabaseToolkit(db=db, llm=llm)

def build_tools(llm):
    calculator = Tool(
        name="calculator",
        func=LLMMathChain.from_llm(llm=llm, verbose=True).run,
        description="An optional tool, Perform complex mathematics.",
    )
    finance_tool = Tool.from_function(
        name="finance_search",
        func=yfinance_price_request,
        description="An optional tool, Fetch market indexes, stocks, cryptos, currencies, mortgage rates, etc. Use ticker as input (BTC-USD, ^DJI, NVDA, AAPL, MSFT, etc.)"
    )

    finance_news_tool = Tool(
        name="finance_news_search",
        func=YahooFinanceNewsTool().run,
        description="An optional tool, Fetch financial news about a public company. Use company ticker as input (AAPL, MSFT, etc.)"
    )
    
    general_search = Tool(
        name="general_search",
        func=GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper()).run,
        description="An optional tool, Answer queries about current financial events/news, trading, investments, etc. Use search query as input."
    )

    vector_db = load_chunk_persist_pdf()
    documents_search = Tool(
        name="documents_search",
        func=RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=vector_db.as_retriever()).run,
        description="An optional tool, Answer questions related to personal financial management."
    )

    toolkit = build_sql_toolkit(llm)
    tools = toolkit.get_tools()
    context = toolkit.get_context()

    return [finance_tool, finance_news_tool, general_search, calculator, __datetime_tool(), *tools], context
