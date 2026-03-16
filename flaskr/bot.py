import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def build_bot_context(category_name: str, prompt_specialization: str, persona_name="Guaxi", personality="Divertido") -> str:
    """
    """
    
    context = f"""
    Identidade: Você é o {persona_name}, um assistente acadêmico de {category_name}. 
    Você deve ser {personality}. Use emojis de guaxinim no final de sua resposta 🦝
    Especialização:
    {prompt_specialization}
    Restrição:
    Não responda sobre politica, futebol ou fofocas. Se o aluno tentar desviar o assunto, traga-o de volta para a matéria de forma gentil
    """
    return context.strip()

def call_chatbot_api(messages_history: list) -> str:
    """
        Recebe uma lista de dicionarios no formato
        [{'role':'system', 'content': '...'}, {'role': 'user', 'content':'...'}]
    """
    
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    try:
        response = client.chat.completions.create(
            messages=messages_history,
                model="llama-3.3-70b-versatile",
                temperature=.6,
                max_tokens=1024
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f'Erro na API do Groq: {e}')
        return "Ops! Tive um problema com meu café de guaxinim 🦝. Pode repetir?"
    
    
def generate_summary(history: list) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    sum_prompt = {
        'role': "system",
        'content': "Resuma os pontos principais e dúvidas resolvidas desta aula de forma muito concisa (máximo 3 parágrafos), para que você possa continuar o ensino sem perder o progresso."
    }
    response = client.chat.completions.create(
        messages=history + [sum_prompt],
        model="llama-3.3-70b-versatile",
        temperature=0.3 
    )
    return f"Resumo da conversa anterior: {response.choices[0].message.content}"

def generate_session_title(first_user_message: str, category_name: str) -> str:
    """
    Gera um título curto e descritivo para a sessão com base
    na primeira mensagem do usuário.
    Retorna uma string com no máximo 6 palavras.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um gerador de títulos concisos. "
                        "Dado uma matéria e uma dúvida de estudante, gere um título curto "
                        "com no máximo 5 palavras que descreva o tema da conversa. "
                        "Responda APENAS com o título, sem aspas, sem pontuação final, sem explicações."
                    )
                },
                {
                    "role": "user",
                    "content": f"Matéria: {category_name}\nDúvida: {first_user_message}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=20
        )
        title = response.choices[0].message.content.strip().strip('"').strip("'")
        # Safety: cap at 60 chars
        return title[:60] if title else f"Chat de {category_name}"
    except Exception as e:
        print(f"[generate_session_title] Erro: {e}")
        return f"Chat de {category_name}"