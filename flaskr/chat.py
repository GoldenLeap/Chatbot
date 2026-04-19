from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort 
from werkzeug.security import generate_password_hash

from flaskr.db import get_db
from flaskr.db import *
from flaskr.bot import *
bp = Blueprint('chat', __name__)

@bp.route('/')
def index():
    """Renderiza a página inicial (dashboard) mostrando categorias e histórico recente."""
    db = get_db()
    
    categorias = db.execute(
        'SELECT id, name, description FROM categories ORDER BY name ASC'
    ).fetchall()
    
    # Pega o primeiro usuário (sistema monousuário para fins de demonstração)
    user = db.execute('SELECT id FROM users LIMIT 1').fetchone()
    sessions = []
    if user:
        sessions = get_user_sessions(user['id'])
    
    return render_template('index.html', categories=categorias, sessions=sessions)

@bp.route('/historico')
def history():
    db = get_db()
    user = db.execute('SELECT id FROM users LIMIT 1').fetchone()
    grouped = []
    if user:
        grouped = get_sessions_by_category(user['id'])
    return render_template('history.html', grouped=grouped)

@bp.route('/create/<int:category_id>', methods=('POST',) )
def create_session(category_id):
    """Cria uma nova sessão de chat vinculada a uma categoria específica."""
    db = get_db()
    
    # Garantia de usuário existente (Mock de autenticação)
    user = db.execute('SELECT id FROM users LIMIT 1').fetchone()
    if not user:
        db.execute('INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
                   ('estudante1', 'estudante@teste.com', generate_password_hash('senha123')))
        db.commit()
        user = db.execute('SELECT id FROM users LIMIT 1').fetchone()
        
    category = db.execute('SELECT name, prompt_specialization FROM categories WHERE id = %s', (category_id, )).fetchone()
    if not category:
        abort(404,  f'Categoria {category_id} não existe')
        
    title = f"Chat de {category['name']}"
    
    cursor = db.execute(
        'INSERT INTO chat_sessions (user_id, category_id, title) VALUES (%s, %s, %s) RETURNING id',
        (user['id'], category_id, title)
    )
    new_session_id = cursor.fetchone()['id']
    
    system_context = build_bot_context(category['name'], category['prompt_specialization'])
    db.execute(
        'INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)',
        (new_session_id, 'system', system_context)
    )
    db.commit()
    
    return redirect(url_for('chat.session_view', session_id=new_session_id))

@bp.route('/chat/<int:session_id>', methods=('GET',))
def session_view(session_id):    
    session_info = get_session_info(session_id)
    
    if session_info is None:
        abort(404, f'ID de sessão {session_id} não existe')

    messages = get_session_messages(session_id)
    
    return render_template('chat.html', session=session_info, messages=messages)

@bp.route('/chat/<int:session_id>/send', methods=('POST',))
def send_message(session_id):
    """Endpoint via POST que responde formatado em Server-Sent Events (SSE) rodando o Llama em stream."""
    from flask import jsonify, Response, stream_with_context
    import json
    
    session_info = get_session_info(session_id)
    if session_info is None:
        return jsonify({'error': 'Sessão não encontrada'}), 404

    data = request.get_json()
    content = data.get('content', '').strip() if data else ''

    if not content:
        return jsonify({'error': 'Mensagem vazia'}), 400

    create_message(session_id, 'user', content)

    total_msgs = count_messages(session_id)

    new_title = None
    if total_msgs == 1:
        new_title = generate_session_title(content, session_info['category_name'])
        update_session_title(session_id, new_title)

    if total_msgs > 15 and total_msgs % 10 == 0:
        full_history = get_ai_context(session_id, limit=30)
        summary = generate_summary(full_history)
        create_message(session_id, 'system', summary)

    history = get_ai_context(session_id)
    
    def generate():
        if new_title:
            yield f"data: {json.dumps({'new_title': new_title})}\n\n"
            
        full_bot_reply = ""
        for chunk in fix_latex_stream(stream_chatbot_api(history)):
            if chunk:
                full_bot_reply += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        create_message(session_id, 'assistant', full_bot_reply)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')