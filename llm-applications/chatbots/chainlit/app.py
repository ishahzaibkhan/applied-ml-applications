from langchain_groq import ChatGroq
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import chainlit as cl
from chainlit.types import ThreadDict

model_gpt = "openai/gpt-oss-20b"
model_qwen = "qwen/qwen3-32b"
model_groq = "groq/compound"


model = ChatGroq(model_name=model_groq, temperature=1, streaming=True)
db_conninfo = "postgresql+asyncpg://admin:admin@localhost/my_chainlit_db"

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Teaching Mode",
            markdown_description="The underlying LLM model is **GPT-3.5**.",
        ),
        cl.ChatProfile(
            name="Quiz Mode",
            markdown_description="The underlying LLM model is **GPT-4**.",
            icon="https://picsum.photos/250",
        ),
    ]

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(conninfo=db_conninfo)


@cl.on_chat_start
async def main():
    mode = cl.user_session.get("chat_profile")
    if mode == "Teaching Mode":
        intro = "In Teaching Mode, I will provide detailed explanations to help you understand various topics."
        template = "You are a helpful assistant that provides detailed explanations to users' questions."
    elif mode == "Quiz Mode":
        intro = "In Quiz Mode, I will challenge you with tricky questions to test your knowledge."
        template = "You are a quiz master that challenges users with tricky questions and no explanations or teaching is allowed, Only questions"
    await cl.Message(content=intro).send()

    cl.user_session.set(
        "chat_history",
        [
            {"role": "system", "content": template}
        ],
    )



@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    cl.user_session.set("chat_history", [])

    for message in thread["steps"]:
        if message["type"] == "user_message":
            cl.user_session.get("chat_history").append(
                {"role": "user", "content": message["output"]}
            )
        elif message["type"] == "assistant_message":
            cl.user_session.get("chat_history").append(
                {"role": "assistant", "content": message["output"]}
            )


@cl.on_message
async def on_message(message: cl.Message):
    chat_history = cl.user_session.get("chat_history")

    chat_history.append(
        {"role": "user", "content": message.content})

    response = model.invoke(chat_history)
    chat_history.append(
        {"role": "assistant", "content": response.content})

    cl.user_session.set("chat_history", chat_history)

    await cl.Message(response.content).send()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")
