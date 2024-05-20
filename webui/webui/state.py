import os
from pydoc import doc
import reflex as rx
from openai import OpenAI
from dotenv import load_dotenv
import pyperclip
from webui.components import embedding_v2

load_dotenv()
_client = None


def get_models():
    """Get the list of models."""
    models = get_openai_client().models.list()
    models = [model.id for model in models if model.id.startswith("gpt")]
    models = sorted(models, reverse=True)
    return models


def get_openai_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


def get_files_list():
    """Get the list of files in the folder."""
    files = os.listdir("./uploaded_files")
    files = [file for file in files]
    return files


# Checking if the API key is set properly
if not os.getenv("OPENAI_API_KEY"):
    raise Exception("Please set OPENAI_API_KEY environment variable.")


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str
    model: str


DEFAULT_CHATS = {
    "Intros": [],
}


class State(rx.State):
    """The app state."""

    models_list: list[str] = get_models()
    model: str = "gpt-4-turbo-preview"
    model_params = {
        "temperature": 0.2,
        "max_tokens": 3000,
    }

    embedding_model: str = "all-MiniLM-L6-v2"
    doc_name: str = "reflex"
    use_embedding: bool = True
    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    streaming = False
    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    knowledge_bases: list[str] = get_files_list()
    uploading: bool = False
    progress: int = 0

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Trigger the folder upload."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.filename

            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            self.knowledge_bases.append(file.filename)

        print("Trigger folder upload")

    async def handle_upload_progress(self, progress: dict):
        self.uploading = True
        self.progress = round(progress["progress"] * 100)
        if self.progress >= 100:
            self.uploading = False

    def enable_embedding(self, doc_name: str):
        self.use_embedding = True
        folder_path = f"../{doc_name}-docs"
        save_path = f"../{doc_name}-embeddings"

        embedding.save_embeddings_and_texts(
            folder_path,
            save_path,
            doc_name,
            model=SentenceTransformer(self.embedding_model),
        )

        embedding.create_faiss_index(os.path.join(save_path, "dspy.npy"), doc_name)

    def stop_streaming(self):
        self.streaming = False
        print("Streaming stopped")

    def delete_message(self, chat_name: str, index: int):
        """Delete a message from the specified chat by index."""
        if chat_name in self.chats and 0 <= index < len(self.chats[chat_name]):
            del self.chats[chat_name][index]

    def handle_model_change(self, new_model):
        # Update the model in the state
        self.model = new_model

    def update_model_params(self, name: str, value: list[float]):
        """Update the model parameters."""
        # print(name, value[0])
        self.model_params[name] = value[0]
        # self.close_drawer()  # Close the drawer

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []
        # self.enable_embedding()

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    def add_system_message(self, content):
        self.chats[self.current_chat].append({"role": "system", "content": content})

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        model = self.openai_process_question

        async for value in model(question):
            yield value

    async def openai_process_question(self, question: str):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """
        # Add the question to the list of questions.
        qa = QA(question=question, answer="", model=self.model)
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        # Build the messages.
        messages = [
            {
                "role": "system",
                "content": "You are a friendly chatbot named Reflex. Respond in markdown.",
            }
        ]

        if self.use_embedding:
            query_prompt = embedding_v2.generate_query_prompt(
                get_openai_client(), self.chats[self.current_chat], question
            )
            print("query_prompt", query_prompt)
            related_docs = embedding_v2.retrieve_relevant_content(
                query_prompt,
                doc_name=self.doc_name,
                k=5,
                model_name=self.embedding_model,
                embedding_path=f"../{self.doc_name}-embeddings",
            )
            # print("related_docs", related_docs)
            messages.append(
                {
                    "role": "system",
                    "content": "use the following docs as context information"
                    + related_docs,
                }
            )

        for qa in self.chats[self.current_chat]:
            messages.append({"role": "user", "content": qa.question})
            messages.append({"role": "assistant", "content": qa.answer})

        # Remove the last mock answer.
        messages = messages[:-1]

        # Start a new session to answer the question.
        session = get_openai_client().chat.completions.create(
            model=self.model, messages=messages, stream=True, **self.model_params
        )

        print("model ", self.model, "was used")

        # Stream the results, yielding after every word.
        for item in session:
            if hasattr(item.choices[0].delta, "content"):
                answer_text = item.choices[0].delta.content
                # Ensure answer_text is not None before concatenation
                if answer_text is not None:
                    self.chats[self.current_chat][-1].answer += answer_text
                else:
                    # Handle the case where answer_text is None, perhaps log it or assign a default value
                    # For example, assigning an empty string if answer_text is None
                    answer_text = ""
                    self.chats[self.current_chat][-1].answer += answer_text
                self.chats = self.chats
                yield

        # Toggle the processing flag.
        self.processing = False

    def set_clipboard(self, message: str):
        """Set the clipboard text."""
        pyperclip.copy(message)
