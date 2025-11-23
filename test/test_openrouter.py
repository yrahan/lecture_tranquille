import streamlit as st
from openai import OpenAI

def main():
    # Charger la clé API depuis secrets.toml
    api_key = st.secrets["OPENROUTER_API_KEY"]

    # Configuration du client OpenAI pour OpenRouter
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    print("➡️ Envoi d'une requête test à OpenRouter...")

    # Requête simple pour vérifier si la clé fonctionne
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",   # modèle gratuit
        messages=[
            {"role": "system", "content": "Tu es un assistant simple et amical."},
            {"role": "user", "content": "Dis-moi bonjour !"}
        ]
    )

    print("\nRéponse OpenRouter :")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
