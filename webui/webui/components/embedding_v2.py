# Refactored Python Code

import dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

# Load environment variables
dotenv.load_dotenv()

def initialize_components():
    # Initialize DirectoryLoader with the path to the directory containing markdown files
    loader = DirectoryLoader(
        "/home/hooman130/workspace/dspy-docs",
        glob="**/*.md*",
        recursive=True,
        show_progress=True,
        loader_kwargs={"autodetect_encoding": True},
    )

    # Load the documents and split them into smaller chunks
    docs = loader.load()
    md_splitter = MarkdownTextSplitter()
    all_splits = md_splitter.split_documents(docs)

    # Create vector representations of the text
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    )

    # Define the number of chunks to retrieve
    retriever = vectorstore.as_retriever(k=5)

    # Define the chat model
    chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

    return chat, retriever

def setup_prompt_templates():
    SYSTEM_TEMPLATE = """
    Answer the user's questions based on the below context. 
    If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

    <context>
    {context}
    </context>
    """

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_TEMPLATE),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return question_answering_prompt

def generate_answer(chat_history, question, chat, retriever, question_answering_prompt):
    # Create the document chain
    document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

    # Create the query transforming retriever chain
    query_transforming_retriever_chain = RunnableBranch(
        (
            lambda x: len(x.get("messages", [])) == 1,
            (lambda x: x["messages"][-1].content) | retriever,
        ),
        question_answering_prompt | chat | StrOutputParser() | retriever,
    ).with_config(run_name="chat_retriever_chain")

    # Create the conversational retrieval chain
    conversational_retrieval_chain = RunnablePassthrough.assign(
        context=query_transforming_retriever_chain,
    ).assign(
        answer=document_chain,
    )

    # Invoke the conversational retrieval chain with a list of messages
    output = conversational_retrieval_chain.invoke(
        {
            "messages": [
                HumanMessage(content=question),
                *[HumanMessage(content=msg) for msg in chat_history],
            ],
        }
    )

    return output

# Main execution
chat, retriever = initialize_components()
question_answering_prompt = setup_prompt_templates()
# Example usage
# response = generate_answer(["previous messages"], "What is Python?", chat, retriever, question_answering_prompt)