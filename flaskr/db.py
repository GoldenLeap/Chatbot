
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
import click
from flask import current_app, g

from .config import load_config

config = load_config()

def get_db():
    """Retorna a conexão com o banco de dados. Se não existir no contexto (g), cria uma nova."""
    if 'db' not in g:
        try:
            g.db = psycopg.connect(**config)
            g.db.row_factory = dict_row
        except (Exception) as e:
            print(e)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read())
        db.commit()
        
@click.command('init-db')
def init_db_cmd():
    init_db()
    click.echo("DB inicializado")

def init_app(app):
    """Registra comandos CLI e a função de limpeza de contexto na aplicação Flask."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cmd)


# --- Funções de Manipulação de Dados ---

def create_message(session_id, role, content):
    """
    Insere mensagem e retorna o registro
    """
    db = get_db()
    cursor = db.execute(
        'INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s) RETURNING *',
        (session_id, role, content)
    )
    db.commit()
    return cursor.fetchone()

def get_session_messages(session_id, include_system=False):
    db = get_db()
    query = 'SELECT role, content, created_at FROM messages WHERE session_id = %s'
    if not include_system:
        query += " AND role != 'system'"
    query += ' ORDER BY created_at ASC'
    
    return db.execute(query, (session_id,)).fetchall()

# Trata e recupera o contexto para a IA

def get_ai_context(session_id, limit=15):
    """
    Busca o prompt de sistema original, o resumo mais recente (se houver),
    e as últimas N mensagens da conversa.
    Formata no padrão que o modelo (llama/Groq) espera.
    """
    db = get_db()
    # Reconstruir o prompt de sistema DINAMICAMENTE na hora do envio
    # Isso garante que alterações nas regras do bot.py afetem sessões antigas imediatamente,
    # não dependendo mais da mensagem 'system' congelada no banco de dados.
    cat_info = db.execute(
        "SELECT c.name, c.prompt_specialization FROM chat_sessions s JOIN categories c ON s.category_id = c.id WHERE s.id = %s",
        (session_id,)
    ).fetchone()
    import flaskr.bot as bot
    system_origin = {"role": "system", "content": bot.build_bot_context(cat_info['name'], cat_info['prompt_specialization'])}
    
    last_sum = get_last_summary(session_id)
    
    # Busca apenas as mensagens mais recentes (limite de contexto), ordenadas crescentemente
    recent_msgs = db.execute(
        "SELECT role, content FROM (SELECT id, role, content FROM messages WHERE session_id = %s AND role NOT IN ('system') ORDER BY created_at DESC LIMIT 6) sub ORDER BY id ASC",    
        (session_id,)
    ).fetchall()
    final_context = [system_origin]
    if last_sum:
        final_context.append({"role": "system", "content": last_sum['content']})
    
    final_context.extend(recent_msgs)
    return final_context


def get_session_info(session_id):
    """Busca detalhes da sessão e da categoria vinculada."""
    db = get_db()
    return db.execute(
        '''SELECT s.id, s.title, c.name AS category_name, c.prompt_specialization
        FROM chat_sessions s
        JOIN categories c ON s.category_id = c.id
        WHERE s.id = %s''',
        (session_id,)
    ).fetchone()


def get_last_summary(session_id):
    """Busca o resumo mais recente salvo na sessão."""
    db = get_db()
    # Procuramos por uma mensagem de sistema que comece com 'Resumo da conversa'
    return db.execute(
        "SELECT content FROM messages WHERE session_id = %s AND role = 'system' AND content LIKE 'Resumo da conversa%%' ORDER BY created_at DESC LIMIT 1",
        (session_id,)
    ).fetchone()

def count_messages(session_id):
    """Conta quantas mensagens de usuário/assistente existem (exclui o system original)."""
    db = get_db()
    result = db.execute(
        "SELECT COUNT(*) as total FROM messages WHERE session_id = %s AND role != 'system'",
        (session_id,)
    ).fetchone()
    return result['total']

def update_session_title(session_id, new_title: str):
    """Atualiza o título de uma sessão de chat."""
    db = get_db()
    db.execute(
        'UPDATE chat_sessions SET title = %s WHERE id = %s',
        (new_title, session_id)
    )
    db.commit()


def get_user_sessions(user_id):
    """Retorna todas as sessões de um usuário, ordenadas por mais recentes."""
    db = get_db()
    
    return db.execute(
        '''SELECT s.id, s.title, c.name AS category_name, c.id AS category_id, s.updated_at
        FROM chat_sessions s
        JOIN categories c ON s.category_id = c.id
        WHERE s.user_id = %s
        ORDER BY s.updated_at DESC''',
        (user_id,)
    ).fetchall()

def get_sessions_by_category(user_id):
    """Retorna sessões do usuário agrupadas por categoria."""
    db = get_db()
    rows = db.execute(
        '''SELECT s.id, s.title, c.name AS category_name, c.id AS category_id, c.description, s.updated_at
        FROM chat_sessions s
        JOIN categories c ON s.category_id = c.id
        WHERE s.user_id = %s
        ORDER BY c.name ASC, s.updated_at DESC''',
        (user_id,)
    ).fetchall()

    grouped = {}
    for row in rows:
        cat_id = row['category_id']
        if cat_id not in grouped:
            grouped[cat_id] = {
                'category_name': row['category_name'],
                'category_id': cat_id,
                'sessions': []
            }
        grouped[cat_id]['sessions'].append(row)
    return list(grouped.values())