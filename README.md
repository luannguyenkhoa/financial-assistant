# 🍺🔗 LangChain + ReAct Agent + RAG + OpenAI model 🤝 Streamlit

An financial assistant for helping user in personal financial management. Basically, user can ask for his current finance health to get the summary and the advice from the bot to improve the finance health by reducing some unneeded expense or improving the spend. By the way, the user can question to get newest information like stock, ctypto prices,... from the internet, or any question related to finance domain to get the answer.

## Requirements
- OpenAI account tier 1 at least
- .env
- venv
- python 3.11

## TechStack
- LangChain
- OpenAI GPT-4 model
- ReAct prompt
- RAG with pdf
- Tools:
  - Datetime
  - Math
  - Yahoo Financial News
  - Yahoo Financial API
  - Google Serper search
  - SQL Database toolkit - Supabase connect
- GPTCache
- Amplitude - Token usage tracking tool
- Streamlit - App UI

## Technical notes
- Assume ENV=STAG is placing the app on Streamlit
- Only one table of the database with name: `expense` supported for now.

## Local Development Setup
- Install streamlit package
- pip

## Warning:
- If you run the app on macos locally, you should disable `pysqlite3-binary` from requirements.txt file before running pip install.

## Running
```shell
streamlit run app.py
```

## Cost:
- GPT-4 tokens consume
- OpenAI Embedding
- Additional services quota: SERPER, Amplitude, LangChain Smith