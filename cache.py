import hashlib
from langchain.globals import set_llm_cache
from gptcache import Cache
from langchain.cache import GPTCache
from gptcache.adapter.api import init_similar_cache
from gptcache.processor.context.summarization_context import SummarizationContextProcess

def get_hashed_name(name):
   return hashlib.sha256(name.encode()).hexdigest()

def init_gptcache(cache_obj: Cache, llm: str):
   hashed_llm = get_hashed_name(llm)
   context_process = SummarizationContextProcess()
   init_similar_cache(
      pre_func=context_process.pre_process,
      cache_obj=cache_obj,
      data_dir=f"cache/similar_cache_{hashed_llm}"
   )

set_llm_cache(GPTCache(init_gptcache))