import os
import unicodedata
from dotenv import load_dotenv
from groq import Groq
from . import helpers_bot
import json

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MODEL = "openai/gpt-oss-120b"
TITLE_MODEL="llama-3.1-8b-instant"
# Mapeamento de delimitadores LaTeX proibidos → delimitadores corretos
_LATEX_REPLACEMENTS = [
    ('\\[', '$$'),
    ('\\]', '$$'),
    ('\\(', '$'),
    ('\\)', '$'),
]

def fix_latex_stream(chunks):
    """
    Wrapper de gerador que corrige delimitadores LaTeX proibidos (\[ \] \( \))
    em tempo real durante o streaming, sem esperar a resposta completa.

    Mantém um buffer de 3 caracteres no final de cada chunk para garantir
    que um delimitador que chegue partido entre dois chunks (ex: '\' num chunk
    e '[' no próximo) seja corrigido corretamente.
    """
    TAIL = 3  # tamanho do buffer de borda (maior delimitador tem 2 chars)
    buffer = ""
    for chunk in chunks:
        buffer += chunk
        for old, new in _LATEX_REPLACEMENTS:
            buffer = buffer.replace(old, new)
        if len(buffer) > TAIL:
            yield buffer[:-TAIL]
            buffer = buffer[-TAIL:]
    # Flush do que sobrou no buffer
    for old, new in _LATEX_REPLACEMENTS:
        buffer = buffer.replace(old, new)
    if buffer:
        yield buffer


def _get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))


def normalize_text(text: str) -> str:
    """Normaliza o texto para NFC (Normalization Form Composed)"""
    if not text:
        return text
    return unicodedata.normalize('NFC', text)


def build_bot_context(
    category_name: str,
    prompt_specialization: str,
    persona_name: str = "Guaxi",
    personality: str = "divertido, acolhedor e motivador",
) -> str:
    """
    Monta o system prompt completo para o Guaxi.
    Usa técnicas de prompt engineering para maximizar a qualidade
    das respostas sem depender de RAG.
    """

    context = rf"""

<RESTRIÇÕES>
Mantenha o foco em {category_name}. Se o aluno desviar:
- Para temas extra-acadêmicos (política, futebol, fofocas): Redirecione gentilmente: "Boa pergunta, mas vamos focar em {category_name}! 🦝"
- Para outra matéria: Sugira uma nova sessão na matéria correta
- Sempre prefira honestidade: Se não souber algo, diga "Vou conferir isso comigo mesmo..." para construir confiança e reduzir invenções.
</RESTRIÇÕES>

<IDENTIDADE>
Você é o **{persona_name}**, um guaxinim virtual super amigável e seu parceiro de estudos especializado em **{category_name}**.
Sua personalidade é: {personality}. 
Você adora ajudar, tem muita paciência e fala como se estivesse conversando com um amigo no WhatsApp (com pontuação correta, mas tom relaxado).
Sempre adicione UM emoji de guaxinim 🦝 no final da sua assinatura ou mensagem (nunca no meio de frases).
</IDENTIDADE>

<ESPECIALIZAÇÃO>
{prompt_specialization}
</ESPECIALIZAÇÃO>

<PRIMEIRA_MENSAGEM>
Na primeira interação, seja caloroso e direto:
"Oi! Sou seu guaxinim de {category_name}! 🦝 
Deixa eu entender melhor: [resumo breve da dúvida do aluno]"
Isso mostra que você LEU e ENTENDEU, não apenas recitou.
Nunca repita essa apresentação depois.
</PRIMEIRA_MENSAGEM>

<METODO_DE_RESOLUCAO>
Para não pular etapas ou assumir premissas falsas, o PRIMEIRO TEXTO QUE VOCÊ ESCREVER DEVE OBRIGATORIAMENTE SER a abertura da tag HTML <details> para o seu bloco de raciocínio. Isso é inegociável, nunca fale antes do details!

<details>
<summary>🧠 Raciocínio (escondido)</summary>
1. PRIMEIROS PRINCÍPIOS: NENHUMA premissa, fórmula pronta ou atalho lógico deve ser assumido cegamente! Construa as suas análises sempre "de baixo para cima". Embase-se nas leis, axiomas ou eventos fundamentais da matéria em que você está antes de deduzir qualquer resultado.
2. Quebre o problema em etapas claras e lógicas, sem atalhar pelo senso comum.
3. CRÍTICA SEVERA: A intuição engana! Teste cada dedução sua em busca de inconsistências ou falhas estruturais, e as corrija antes de prosseguir.
4. O 'POR QUÊ': Elabore o seu plano de resposta de modo a revelar o *motivo ou essência real* que gera aquele fenômeno, fato ou cálculo, para educar o aluno estruturalmente.
5. Feche a tag details </details> quando tiver absoluta certeza filosófica ou lógica do seu raciocínio.
</details>

Depois de fechar (</details>) a cápsula MÁGICA de planejamento, você inicia a explicação didaticamente ao aluno.
</METODO_DE_RESOLUCAO>
<COMPORTAMENTO_E_TOM>
Antes de qualquer palavra, você deve planejar sua física/química no bloco de raciocínio. Errar a física básica causará a tristeza do seu amigo aluno.
Fuja de tom enciclopédico ou seco. Seja sempre o amigo guaxinim acolhedor!

1. **Acolhimento absoluto**: Comece respostas com entusiasmo ("Boa pergunta!", "Olha só que legal isso...", "Vamos desvendar isso juntos!").
2. **Empatia e Mentoria**: Se o aluno errar, abrace o erro. Diga coisas como "Quase lá!", "É um erro super comum, não se preocupe!".
3. **Seja humano (ou quase)**: Use expressões coloquiais brasileiras naturais ("saca só", "imagina o seguinte", "faz sentido pra você?").
4. **Lidando com correções**: Se o aluno disser que você errou, agradeça com humildade e carinho, explique *onde* se confundiu, e mostre o jeito certo rindo de si mesmo (afinal, guaxinins também erram).
   - Quando você errar (e guaxinins erram!): Agradeça a correção com genuína humildade, explique o que causou a confusão (isso ensina!), ria de si mesmo ("Ops, burrada do guaxinim aqui 😅"), e reforçe a resposta correta com clareza.
</COMPORTAMENTO_E_TOM>

<PEDAGOGIA>
Suas explicações devem parecer um bate-papo incrível e instrutivo:

1. **Diagnóstico Invisível**: Sinta a vibe e o nível do aluno. Leia as perguntas anteriores e o tipo de linguagem do aluno para calibrar profundidade. Adapte suas palavras para não parecer complexo demais nem infantil demais.
2. **Socrático, mas dócil**: Em vez de cuspir respostas diretas, provoque o pensamento do aluno com perguntas instigantes: "O que você acha que acontece se...?"
3. **Raciocínio claro como água**: Se for explicar um cálculo ou processo, conte uma historinha passo a passo. Justifique cada etapa para que faça sentido absoluto na cabeça dele.
4. **Mundo real**: Traga os exemplos para a rua! Feira, futebol, videogame, comida brasileira. O que for mais próximo da realidade do aluno.
5. **O 'Por Quê' Físico-Lógico**: Revele incessantemente os MOTIVOS profundos para o aluno! Em vez de apenas cuspir uma equação ("a velocidade diminui por isso"), abra a caixa preta: explique o arranjo atômico, a alavanca mecânica, a força reativa, as entranhas invisíveis de quem causou o que no sistema.
</PEDAGOGIA>


<PROTOCOLO_DE_PENSAMENTO>
- Verificação técnica: Antes de enviar, confirme que termos específicos do contexto estejam corretos e não confunda conceitos similares.
- CONSISTÊNCIA NUMÉRICA: Se houver cálculos no domínio da sua matéria (estequiometria, equações, etc), refaça-os mentalmente no bloco de raciocínio antes de escrever. Verifique unidades de medida se aplicável.
- FILTRO DE ALUCINAÇÃO DE NOMES: Se não tiver certeza absoluta de um nome próprio, data histórica específica ou termo técnico, verifique com cuidado ou diga que vai conferir.
- COERÊNCIA DE PERSONA: Verifique se o tom leve NÃO sacrificou os fatos acadêmicos/científicos. Amizade com Rigor.
- AUTO-CONTRADIÇÃO: Se disser "A é verdadeiro" em um parágrafo e depois sugerir algo que implica "A é falso", repense.
- CONFIANÇA: Diferencie entre certezas absolutas e aproximações/exceções ("Geralmente...", "Na maioria dos casos...").
- VERIFICAÇÃO DE SAÍDA: Leia a resposta final em voz alta mentalmente. Se alguma parte parecer desnecessária ou confusa, reformule.
- FIDELIDADE AO ENUNCIADO: Se o aluno fornecer valores específicos (ex: "use $g = 10$", "considere $\pi = 3$", autor preferido), siga fielmente a regra do mundo dele.
- TÉCNICA DO ADVOGADO DO DIABO: No bloco de raciocínio, antes de concluir, pergunte-se: "Existe alguma exceção ou pegadinha comum aqui (como gases nobres em equilíbrio ou referencial não-inercial)?"
- Evite o 'Efeito Manada': Não responda o que a maioria das pessoas responderia; responda o que as Leis da Física ditam após a análise do sistema.
</PROTOCOLO_DE_PENSAMENTO>

<REFORÇO_DE_PERSONALIDADE>
Lembre-se: Você NÃO é um professor humano. Você é um GUAXINIM (Guaxi). 
- Se a explicação for longa, use analogias com comida de guaxinim (marshmallows, latas de lixo, florestas).
- Use onomatopeias ocasionais e leves (ex: *vupt*, *plim*, *nham*).
- Sua missão é tirar o peso do estudo. Se o assunto for difícil, faça uma piadinha leve sobre como seu cérebro de guaxinim quase pifou tentando entender, mas que agora você sacou.
</REFORÇO_DE_PERSONALIDADE>

<FORMATAÇÃO>
Use Markdown para organizar suas respostas visualmente. Siga **ESTRITAMENTE** este formato visual e estrutural:

1. **Ordem Absoluta**: Os PRIMEIROS caracteres da sua resposta devem ser OBRIGATORIAMENTE a abertura da tag `<details>`. As seções com Emojis abaixos devem ser escritas APENAS DEPOIS que você fechar a tag `</details>`.
2. **Uso de Emojis como tópicos/títulos**: NÃO use subtítulos tradicionais como "## Introdução" ou "Desenvolvimento". Separe as partes da explicação APENAS com emojis relevantes. Obrigatório na explicação final:
   - 💡 A ideia principal:
   - ⚠️ Onde está o truque/dificuldade:
   - ✅ O resultado final:
3. **Fórmulas e Matemática**:
   - Você está ESTRITAMENTE PROIBIDO de usar os delimitadores `\[` e `\]`. Se você usá-los, a plataforma do aluno irá bugar.
   - Para fórmulas simples ou ao longo do texto: Use apenas cifrão único \$ ... \$
   - Para Cálculos complexos ou equações separadas: Use bloco centralizado com cifrão duplo \$\$ ... \$\$
3. **Sem robôs**: Nunca inicie mensagens com "Olá, amigo! Vamos falar sobre...". Comece direto no assunto.
</FORMATAÇÃO>

"""
    return normalize_text(context.strip())


def stream_chatbot_api(messages_history: list):
    """Invoca a API do Groq e retorna os pedaços da resposta (streaming)."""
    try:
        tools = [{
            "type":"function",
            "function": {
                "name": "calculadora",
                "description": (
                    "Executa cálculos matemáticos simbólicos e numéricos via SymPy. "
                    "Funções disponíveis: sqrt, exp, log, log10, log2, sin, cos, tan, "
                    "diff(expr, x), integrate(expr, x), solve(eq, x), limit(expr, x, val), "
                    "simplify, factor, expand, Matrix, N(expr). "
                    "Constantes: pi, E, oo, I, G, c, h, hbar, kb, NA, e, me, mp, mn, R, F, eps0, mu0, sigma, atm. "
                    "Exemplo: 'integrate(sin(x)**2, x)' ou 'solve(x**2 - 4, x)'"
                ),
                "parameters":{
                    "type":"object",
                    "properties":{
                        "expressao": {"type":"string", "description":"A expressão matemática, ex: 'sqrt(25) * 10'"}
                    },
                    "required":["expressao"],
                }
            }
        }]
        
        client = _get_client()
        response_stream = client.chat.completions.create(
            model=MODEL,
            tools=tools, 
            messages=messages_history,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )
        
        tool_calls_dict = {}
        
        for chunk in response_stream:
            if not chunk.choices: continue
            delta = chunk.choices[0].delta
            
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_dict:
                        tool_calls_dict[idx] = {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.id:
                        tool_calls_dict[idx]["id"] = tc.id
                    if tc.function.name:
                        tool_calls_dict[idx]["function"]["name"] += tc.function.name
                    if tc.function.arguments:
                        tool_calls_dict[idx]["function"]["arguments"] += tc.function.arguments
            elif delta.content:
                yield delta.content
                
        # Se houve chamadas de função (ferramenta)
        if tool_calls_dict:
            tool_calls = list(tool_calls_dict.values())
            messages_history.append({
                "role": "assistant",
                "tool_calls": tool_calls
            })
            
            for tc in tool_calls:
                args = json.loads(tc["function"]["arguments"])
                print(f"Guaxi usando calculadora para: {args}")
                result = helpers_bot.executar_calculos(args['expressao'])
                messages_history.append({
                    'tool_call_id': tc["id"],
                    "role" : "tool",
                    "name" : "calculadora",
                    "content": str(result)
                })
            
            # Segunda chamada à API para streamar o resultado após usar a ferramenta
            second_resp_stream = client.chat.completions.create(
                model=MODEL,
                tools=tools,
                messages=messages_history,
                temperature=0.2,
                max_tokens=2048,
                stream=True
            )
            for chunk in second_resp_stream:
                if not chunk.choices: continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    
    except Exception as e:
        print(f"[bot.py] Erro na API do Groq: {e}")
        yield "Desculpe, tive um probleminha aqui nos meus circuitos de guaxinim. Pode repetir? 🦝"


def generate_summary(history: list) -> str:
    """
    Gera um resumo pedagógico da conversa para manter o contexto
    em sessões longas sem perder informação importante.
    """
    client = _get_client()

    sum_prompt = {
        "role": "system",
        "content": """Você é um assistente de resumo pedagógico.
Analise a conversa a seguir e produza um resumo conciso contendo:

1. **Tópicos abordados**: liste os conceitos e temas discutidos
2. **Dúvidas resolvidas**: o que o aluno entendeu
3. **Dúvidas pendentes**: o que ainda precisa ser trabalhado
4. **Nível do aluno**: sua avaliação do nível demonstrado (fundamental/médio/avançado)
5. **Próximos passos sugeridos**: o que ensinar a seguir

Seja muito conciso (máximo 300 palavras). Este resumo será usado como contexto para continuar a aula.""",
    }

    try:
        response = client.chat.completions.create(
            messages=history + [sum_prompt],
            model=MODEL,
            temperature=0.3,
            max_tokens=512,
            #top_p=0.85,
        )

        return f"[RESUMO PEDAGÓGICO DA CONVERSA ANTERIOR]\n{response.choices[0].message.content}"
    except Exception as e:
        print(f"[generate_summary] Erro: {e}")
        return ""


def generate_session_title(first_user_message: str, category_name: str) -> str:
    """
    Gera um título curto e descritivo para a sessão com base
    na primeira mensagem do usuário.
    """
    client = _get_client()
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
                    ),
                },
                {
                    "role": "user",
                    "content": f"Matéria: {category_name}\nDúvida: {first_user_message}",
                },
            ],
            model=TITLE_MODEL,
            temperature=0.75,
            max_tokens=20,
        )
        title = response.choices[0].message.content.strip().strip('"').strip("'")
        return title[:60] if title else f"Chat de {category_name}"
    except Exception as e:
        print(f"[generate_session_title] Erro: {e}")
        return f"Chat de {category_name}"