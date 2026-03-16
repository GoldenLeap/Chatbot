# Guaxi - O Assistente Acadêmico 🦝✨

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=flat-square&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square&logo=postgresql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-orange?style=flat-square)

Guaxi é um chatbot educacional inteligente projetado para ser o parceiro de estudos ideal. Diferente de assistentes genéricos, o Guaxi utiliza uma persona de guaxinim empática, divertida e motivadora, focada em tornar o aprendizado leve e engajador.

Este projeto foi desenvolvido como uma ferramenta de apoio escolar, integrando tecnologias de IA com uma interface moderna e intuitiva.

## 📸 Demonstração

**Funcionamento do chatbot**
> ![Demonstração do Guaxi](img/demo.gif)

## 🚀 Funcionalidades Principais

- **Personas Especializadas**: O bot adapta seu tom e conhecimento para 16 categorias diferentes, garantindo precisão científica, histórica e linguística.
  <details>
    <summary><b>📚 Ver todas as 16 categorias de estudo</b></summary>
    <ul>
      <li>Matemática</li>
      <li>Português</li>
      <li>Física</li>
      <li>Química</li>
      <li>História</li>
      <li>Geografia</li>
      <li>Filosofia</li>
      <li>Sociologia</li>
      <li>Biologia</li>
      <li>Ciências (Ensino Fundamental)</li>
      <li>Língua Inglesa</li>
      <li>Arte</li>
      <li>Educação Física</li>
      <li>Ensino Religioso</li>
      <li>Literatura Brasileira</li>
      <li>Redação e Produção Textual</li>
    </ul>
  </details>
- **Explicações Estruturadas**: Uso obrigatório de tópicos visuais (💡 Dica, ⚠️ Atenção, ✅ Conclusão) para facilitar a leitura.
- **Renderização Científica**: Suporte completo para fórmulas matemáticas e químicas via **KaTeX** (**LaTeX**).
- **Interface Moderna**: Layout responsivo com design "Glassmorphism", modo escuro e fontes otimizadas (Inter & Outfit).
- **Histórico Completo**: Sessões de estudo organizadas por data e categoria, com títulos gerados dinamicamente pela IA.
- **Correção Empática**: O bot é treinado para acolher erros e guiar o aluno passo a passo através do método socrático.

## 🔮 Funcionalidades Futuras

- **Sistema de Quizzes**: Uma funcionalidade para testar o conhecimento do usuário de forma interativa.
- **Feedback de Performance**: Um sistema de avaliação e análise do progresso do aluno ao longo do tempo.
- **Sistema de Conquistas**: Um sistema gamificado que recompensa os alunos pelos seus progressos acadêmicos e interações com o Guaxi, tornando o aprendizado mais divertido e motivador (badges, troféus, etc.).
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

4. **Variáveis de Ambiente e Banco de dados**:
    Copie os arquivos de exemplo para configurar seu ambiente local:
   ```bash
   cp .env.example .env
   cp database.ini.example database.ini
   ```
   Preencha o .env com sua GROQ_API_KEY e o database.ini com as credenciais do seu PostgreSQL.
  **Importante**: Não se esqueça de adicionar os arquivos `.env` e `database.ini` ao seu `.gitignore` para evitar que informações sensíveis, como suas chaves de API e dados de banco de dados, sejam versionadas no repositório.

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

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
---
*Desenvolvido com ❤️ para transformar a educação.* 🦝
