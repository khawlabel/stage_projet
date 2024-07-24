import argparse
import time  # Importer le module pour mesurer le temps
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from groq import Groq  # Importer le client Groq
from langchain_huggingface import HuggingFaceEmbeddings  # Importer les embeddings Hugging Face
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

CHROMA_PATH = "../data/chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def get_groq_response(prompt_text: str) -> str:
    """Generate a response using Groq API."""
    client = Groq(api_key='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')  # Remplacez par votre clé API réelle

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message

def normalize_scores(results):
    """Normalize relevance scores to be between 0 and 1."""
    normalized_results = []
    for doc, score in results:
        normalized_score = max(0, min(1, score))  # Assurer que le score est entre 0 et 1
        normalized_results.append((doc, normalized_score))
    return normalized_results

def get_embedding_function():
    """Get Hugging Face embeddings function."""
    return HuggingFaceInferenceAPIEmbeddings(api_key='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', model_name="intfloat/multilingual-e5-large")

def query_rag(query_text: str) -> str:
    try:
        start_time = time.time()  # Début du chronométrage
        
        # Préparer la fonction d'embedding
        embedding_function = get_embedding_function()
        print(f"Embedding function initialized: {embedding_function}")

        # Charger la base de données vectorielle
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        print("Chroma vector store loaded.")

        # Utiliser Chroma pour la recherche de similarité
        results = db.similarity_search(query_text, k=10)  # Note: `similarity_search` method
        print(f"Search completed. Number of results: {len(results)}")

        if not results:
            print("No documents found.")
            return "No documents found."

        # Les résultats contiennent des documents et des scores de similarité
        documents_with_scores = [(doc, doc.metadata.get("score", 0)) for doc in results]
        print(f"Extracted documents with similarity scores.")

        # Trier les documents par score de similarité (du plus élevé au plus bas)
        documents_with_scores.sort(key=lambda x: x[1], reverse=True)
        print(f"Documents sorted by similarity score.")

        # Préparer le texte du contexte à partir des documents top-k
        top_k_results = documents_with_scores[:10]
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in top_k_results])
        print(f"Context Text: {context_text[:500]}...")  # Afficher les premiers 500 caractères pour la brièveté

        # Préparer le prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        print(f"Prompt: {prompt}")

        # Générer la réponse en utilisant Groq
        response_text = get_groq_response(prompt)
        print(f"Response Text: {response_text}")

        # Obtenir les sources des documents
        sources = [doc.metadata.get("id", None) for doc, _ in top_k_results]
        print(f"Sources: {sources}")

        # Formater la réponse
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print(f"Formatted Response: {formatted_response}")

        end_time = time.time()  # Fin du chronométrage
        elapsed_time = end_time - start_time
        print(f"Time taken for query: {elapsed_time:.2f} seconds")  # Afficher le temps écoulé

        return formatted_response

    except Exception as e:
        import traceback
        print(f"An error occurred in query_rag: {e}")
        print(traceback.format_exc())

def main():
    # Créer le CLI14.93 seconds
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    response_text = query_rag(query_text)
    print(response_text)

if __name__ == "__main__":
    main()