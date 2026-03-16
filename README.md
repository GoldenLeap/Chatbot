# Guaxi - O Assistente Acadêmico 🦝✨

Guaxi é um chatbot educacional inteligente projetado para ser o parceiro de estudos ideal. Diferente de assistentes genéricos, o Guaxi utiliza uma persona de guaxinim empática, divertida e motivadora, focada em tornar o aprendizado leve e engajador.

Este projeto foi desenvolvido como uma ferramenta de apoio escolar, integrando tecnologias de IA com uma interface moderna e intuitiva.

## 🚀 Funcionalidades Principais

- **Personas Especializadas**: O bot adapta seu tom e conhecimento para 16 categorias diferentes (Matemática, Biologia, Redação, História, etc.).
- **Explicações Estruturadas**: Uso obrigatório de tópicos visuais (💡 Dica, ⚠️ Atenção, ✅ Conclusão) para facilitar a leitura.
- **Renderização Científica**: Suporte completo para fórmulas matemáticas e químicas via **KaTeX** ($LaTeX$).
- **Interface Moderna**: Layout responsivo com design "Glassmorphism", modo escuro e fontes otimizadas (Inter & Outfit).
- **Histórico Completo**: Sessões de estudo organizadas por data e categoria, com títulos gerados dinamicamente pela IA.
- **Correção Empática**: O bot é treinado para acolher erros e guiar o aluno passo a passo através do método socrático.

## 🚀 Funcionalidades Futuras

- **Sistema de Quizzes**: Uma funcionalidade para testar o conhecimento do usuário de forma interativa.
- **Feedback de Performance**: Um sistema de avaliação e análise do progresso do aluno ao longo do tempo.
- **Sistema de Conquistas**: Um sistema gamificado que recompensa os alunos pelos seus progressos acadêmicos e interações com o Guaxi, tornando o aprendizado mais divertido e motivador. Através de conquistas como badges e troféus, os alunos são incentivados a continuar estudando, alcançando novas metas e superando desafios.
- **Sistema de Login**: Para personalização do histórico e sessões de estudo.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python + [Flask](https://flask.palletsprojects.com/)
- **IA/LLM**: [Groq API](https://groq.com/) (Modelo Llama 3.3 70B)
- **Banco de Dados**: PostgreSQL (via psycopg2)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (AJAX/Fetch API)
- **Bibliotecas**:
  - `KaTeX` (Renderização de fórmulas)
  - `marked.js` (Markdown parsing)
  - `unicodedata` (Normalização de caracteres)

## 📋 Pré-requisitos

- Python 3.10+
- PostgreSQL
- Chave de API da Groq

## ⚙️ Configuração

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd Chatbot
   ```

2. **Crie e ative um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Variáveis de Ambiente**:
   Crie um arquivo `.env` na raiz do projeto com sua chave:
   ```env
   GROQ_API_KEY=sua_chave_aqui
   DATABASE_URL=postgresql://usuario:senha@localhost/nome_do_banco
   ```

5. **Inicialize o Banco de Dados**:
   ```bash
   flask --app flaskr init-db
   ```

6. **Execute o projeto**:
   ```bash
   flask --app flaskr run
   ```

## 🎨 Design System

O projeto utiliza uma paleta de cores inspirada em tons de roxo profundo e neon, focando em legibilidade e conforto visual durante longas sessões de estudo:
- **Primary**: #9d4edd (Roxo)
- **Background**: Gradiente escuro (Deep Space)
- **Tipografia**: Inter (Corpo do texto) e Outfit (Títulos)

---
*Desenvolvido com ❤️ para transformar a educação.* 🦝