import traceback
import os
import uuid
if os.environ.get("ENV", "LOCAL") == "LOCAL":
    from dotenv import load_dotenv
    load_dotenv()

import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from assistant import build_memory, build_agent, openai_callback
from callback import FinalStreamingStdOutCallbackHandler
from tracking import track_event
from utils import strip_final_answer

st.set_page_config(page_title="Financial Assistant", page_icon="🍻")
st.title("🍻 Financial Assistant")
st.write("The current user by auth token feature is not implemented yet. So, please add the prefix: `I'm Maureen Lee.` to questions related to user's data if didn't ask.\n\
         The database is just quite simple with 2 tables only, you can see fully [here](https://drive.google.com/drive/folders/11MHq8C_rAwlikRyFu4DW4Hc0F0ZUebHz?usp=sharing)")

session_id = uuid.uuid4().hex

# Set up memory
msgs = StreamlitChatMessageHistory()
memory = build_memory(msgs=msgs)

if len(msgs.messages) == 0:
    msgs.add_ai_message("Hi, I'm a delightful assistant. How is it going?")
    st.session_state.steps = {}

# For reset chat history
def on_reset():
    msgs.clear()
    msgs.add_ai_message("Hi, I'm a delightful assistant. How is it going?")
    st.session_state.steps = {}

col1, col2 = st.columns([3, 1])
with col1:
    view_messages = st.expander("View the message contents in session state")

with col2:
    st.button("Reset chat history", on_click=on_reset)

# Render current messages from StreamlitChatMessageHistory
# for msg in msgs.messages:
#     st.chat_message(msg.type).write(msg.content)

# Remove these below lines (49-61) and turn on the above lines (45-46) if just want to display the final answer
avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if not hasattr(step[0], "tool"):
                continue
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

agent_executor = build_agent(memory=memory)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input(placeholder="Hi, I'm Maureen Lee. How is my financial health currently?"):
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # Replace FinalStreamingStdOutCallbackHandler to StreamlitCallbackHandler if just want to display the final answer only
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False) # FinalStreamingStdOutCallbackHandler()
        cfg = RunnableConfig(callbacks=st_cb)
        cfg["callbacks"] = [st_cb]
        cfg["session_id"] = session_id
        try:
            response = agent_executor.invoke({'input': prompt}, cfg)
            st.write(strip_final_answer(response["output"]))
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

            # Track the number of tokens used
            track_event(
                "Token usage",
                session_id,
                {
                    "user_prompt": prompt,
                    "prompt_tokens": openai_callback.prompt_tokens,
                    "completion_tokens": openai_callback.completion_tokens,
                    "total_tokens": openai_callback.total_tokens,
                    "total_cost": openai_callback.total_cost
                }
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            st.write("Something went wrong. Please ask me again.")

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Message History initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
