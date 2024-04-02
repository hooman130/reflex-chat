import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import faiss

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def generate_query_prompt(client, chat_history, user_question):
    """
    Generate a query prompt based on the chat history and user question using the OpenAI completion API.

    Parameters:
    - client: An instance of the OpenAI API client.
    - chat_history: A string containing the conversation history.
    - user_question: The latest question from the user.

    Returns:
    - A string containing the generated search query.
    """
    prompt = (
        "Given the following conversation history and the latest question, "
        "generate a search query for faiss flat index to find relevant documents"
        "required to answer the user's question you don't know about, usually techincal:\n\n"
        "Conversation History:\n"
        f"{chat_history}\n\n"
        "Latest Question:\n"
        f"{user_question}\n\n"
        "Search Query:"
    )
    prompt = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=prompt,
            max_tokens=1000,
            temperature=0.3,
        )

        print(response.choices[0])

        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return ""


def retrieve_relevant_content(
    user_query, embedding_path, doc_name, k=5, model_name="All-MiniLM-L6-v2"
):
    model = SentenceTransformer(model_name)
    related_docs = search_index(user_query, model, embedding_path, doc_name, k)
    related_docs = ". ".join(related_docs)
    return related_docs


def search_index(query, model, embedding_path, doc_name, k=5):
    # Load the index and documents
    index = faiss.read_index(f"{doc_name}_index.index")
    with open(os.path.join(embedding_path, f"{doc_name}.json"), "r") as f:
        documents = json.load(f)

    # Convert query to embedding
    query_embedding = model.encode([query])[0].reshape(1, -1)

    # Perform the search
    _, indices = index.search(query_embedding, k)
    return [documents[i] for i in indices[0]]


def create_faiss_index(embeddings_path, doc_name):
    embeddings = np.load(embeddings_path)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)
    faiss.write_index(index, f"{doc_name}_index.index")


def preprocess_text(text):
    # Tokenize
    tokens = word_tokenize(text)
    # Lowercase and remove punctuation
    tokens = [word.lower() for word in tokens if word.isalpha()]
    # Remove stopwords
    tokens = [word for word in tokens if not word in stop_words]
    # Lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)


def read_and_preprocess(folder_path):
    documents = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if (
                file.endswith(".md")
                or file.endswith(".mdx")
                or file.endswith(".txt")
                or file.endswith(".json")
            ):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    preprocessed_text = preprocess_text(text)
                    documents.append(preprocessed_text)
    return documents


def embed_documents(folder_path, model):
    documents = read_and_preprocess(folder_path)
    document_embeddings = model.encode(documents, batch_size=8, show_progress_bar=True)
    return documents, document_embeddings


# Embed documents and save embeddings along with their corresponding texts for later retrieval
def save_embeddings_and_texts(folder_path, save_path, doc_name, model):
    documents, embeddings = embed_documents(folder_path, model)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    np.save(os.path.join(save_path, f"{doc_name}.npy"), embeddings)
    with open(os.path.join(save_path, f"{doc_name}.json"), "w") as f:
        json.dump(documents, f)
