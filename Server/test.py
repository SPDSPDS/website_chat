from langchain.document_loaders import UnstructuredURLLoader
from langchain.docstore.document import Document
from unstructured.cleaners.core import remove_punctuation,clean,clean_extra_whitespace
from langchain.chains.summarize import load_summarize_chain

def generate_document(url):
    "Given an URL, return a langchain Document to futher processing"
    loader = UnstructuredURLLoader(urls=[url],
        mode="elements",
        post_processors=[clean,remove_punctuation,clean_extra_whitespace])
    elements = loader.load()
    selected_elements = [e for e in elements if e.metadata['category']=="NarrativeText"]
    full_clean = " ".join([e.page_content for e in selected_elements])
    return Document(page_content=full_clean, metadata={"source":url})

print(generate_document('https://en.wikipedia.org/wiki/Israeli_bombing_of_the_Iranian_embassy_in_Damascus'))