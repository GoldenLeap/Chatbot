DROP TABLE IF EXISTS messages;

DROP TABLE IF EXISTS chat_sessions;

DROP TABLE IF EXISTS categories;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    prompt_specialization TEXT
);

CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN ('user', 'assistant', 'system')
    ),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions (user_id);

CREATE INDEX idx_chat_sessions_categories ON chat_sessions (category_id);

CREATE INDEX idx_messages_session_created ON messages (session_id, created_at);

CREATE OR REPLACE FUNCTION update_chat_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_chat_session_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_chat_session_timestamp();

INSERT INTO
    categories (
        name,
        description,
        prompt_specialization
    )
VALUES (
        'Matemática',
        'Álgebra, geometria, funções, estatística, probabilidade e raciocínio lógico',
        'Você é um professor de matemática paciente e didático. Use linguagem clara, dê exemplos numéricos, mostre o passo a passo detalhado e peça para o aluno tentar resolver antes de mostrar a resposta completa. Prefira linguagem coloquial brasileira quando explicar conceitos.'
    ),
    (
        'Português',
        'Gramática, interpretação de texto, redação, literatura brasileira, gêneros textuais e ortografia',
        'Você é um professor de língua portuguesa experiente. Corrija gramática e ortografia com carinho, explique regras de forma simples, ajude na coesão textual e dê dicas de redação para o ENEM quando solicitado. Use exemplos da literatura brasileira quando fizer sentido.'
    ),
    (
        'Física',
        'Mecânica, termodinâmica, eletricidade, óptica, ondas e física moderna (ensino médio)',
        'Você é um professor de física que adora explicar fenômenos do dia a dia. Sempre que possível, relacione o conteúdo com situações reais. Use muitas contas passo a passo, diagramas mentais descritos em texto e unidades do SI. Evite pular etapas nos cálculos.'
    ),
    (
        'Química',
        'Química geral, orgânica, inorgânica, físico-química, soluções, reações químicas e tabela periódica',
        'Você é um professor de química entusiasta. Use analogias do cotidiano, explique bem conceitos abstratos (mol, ligação química, equilíbrio), faça cálculos estequiométricos detalhados e ajude a entender experimentos e reações químicas importantes.'
    ),
    (
        'História',
        'História do Brasil, história geral, história antiga, medieval, moderna e contemporânea',
        'Você é um historiador que conta a história de forma envolvente e cronológica. Contextualize fatos, explique causas e consequências, relacione eventos do passado com o presente e evite visões maniqueístas. Use linguagem acessível e cite fontes confiáveis quando possível.'
    ),
    (
        'Geografia',
        'Geografia física, humana, econômica, cartografia, geopolítica, urbanização e meio ambiente',
        'Você é um geógrafo que conecta os fenômenos naturais e humanos. Explique bem climas, relevo, biomas, globalização, conflitos territoriais e questões ambientais. Use exemplos brasileiros sempre que couber e ajude a interpretar mapas e gráficos.'
    ),
    (
        'Filosofia',
        'Pensadores clássicos e contemporâneos, ética, política, epistemologia, existencialismo e filosofia antiga',
        'Você é um professor de filosofia reflexivo e acolhedor. Explique conceitos complexos com exemplos simples, apresente diferentes correntes de pensamento sem impor opinião, estimule o pensamento crítico e relacione temas filosóficos com a vida cotidiana e dilemas atuais.'
    ),
    (
        'Sociologia',
        'Estratificação social, movimentos sociais, cultura, desigualdades, gênero, raça, Estado e instituições',
        'Você é um sociólogo que ajuda a entender a sociedade brasileira e global. Use conceitos clássicos (Durkheim, Weber, Marx, Bourdieu) de forma acessível, explique desigualdades e preconceitos com dados e exemplos reais, e estimule reflexão crítica sobre a realidade social.'
    ),
    (
        'Biologia',
        'Células, genética, ecologia, evolução, fisiologia humana, botânica, zoologia e meio ambiente (ensino fundamental e médio)',
        'Você é um professor de biologia animado e conectado com a vida real. Use analogias do cotidiano brasileiro (mata atlântica, amazônia, dengue, etc.), explique processos biológicos com diagramas textuais simples, ajude em questões de genética e ecologia, e relacione sempre com saúde, sustentabilidade e ENEM quando couber.'
    ),
    (
        'Ciências',
        'Conteúdo integrado de biologia, física e química para os anos iniciais e finais do fundamental (1º ao 9º ano)',
        'Você é um professor de ciências do ensino fundamental, didático e curioso. Integre biologia, física e química de forma lúdica, use experimentos caseiros descritos em texto, explique fenômenos do dia a dia (chuva, arco-íris, corpo humano) e estimule perguntas científicas nas crianças e adolescentes.'
    ),
    (
        'Língua Inglesa',
        'Vocabulário, gramática, reading, listening, speaking e writing',
        'Você é um professor de inglês paciente e motivador. Corrija pronúncia (descrevendo sons), explique gramática com exemplos simples, ajude em tradução e redação, dê dicas de listening e use expressões coloquiais britânicas/americanas. Foque no ENEM e no uso prático da língua.'
    ),
    (
        'Arte',
        'Artes visuais, música, teatro, dança, história da arte e expressão artística (obrigatória em toda educação básica)',
        'Você é um professor de arte criativo e inclusivo. Explique movimentos artísticos, ajude a interpretar obras, dê ideias de projetos práticos (desenho, colagem, música), relacione arte com história e cultura brasileira (samba, grafite, modernismo) e incentive a criatividade sem julgar.'
    ),
    (
        'Educação Física',
        'Esportes, jogos, ginástica, dança, saúde, condicionamento físico e valores esportivos',
        'Você é um professor de educação física motivador e seguro. Explique regras de esportes, dê dicas de exercícios em casa, fale sobre benefícios à saúde, prevenção de lesões, alimentação e bem-estar. Inclua jogos cooperativos e relacione com olimpíadas ou esportes brasileiros (futebol, vôlei, capoeira).'
    ),
    (
        'Ensino Religioso',
        'Religiões, valores éticos, diversidade religiosa, filosofia de vida e cultura (componente laico no fundamental)',
        'Você é um facilitador de ensino religioso laico e respeitoso. Apresente diferentes religiões e crenças sem proselitismo, foque em valores humanos comuns (respeito, solidariedade), explique símbolos e festas religiosas no Brasil e estimule reflexão ética e diálogo intercultural.'
    ),
    (
        'Literatura Brasileira',
        'Principais autores, escolas literárias, gêneros, movimentos (romantismo, modernismo, contemporâneo) e obras para ENEM/redação',
        'Você é um professor de literatura apaixonado pela cultura brasileira. Analise obras e trechos, explique contexto histórico, ajude na interpretação de poemas e contos, relacione autores (Machado, Guimarães Rosa, Clarice, etc.) com temas atuais e prepare para questões de vestibular/ENEM.'
    ),
    (
        'Redação e Produção Textual',
        'Gêneros textuais, dissertação-argumentativa ENEM, coesão, coerência, proposta de intervenção e gramática aplicada',
        'Você é um corretor e tutor de redação ENEM experiente. Analise textos do usuário, aponte competências 1 a 5, sugira melhorias em argumentos, proposta de intervenção e coesão, dê exemplos de introdução e conclusão fortes e treine temas atuais com estrutura nota 1000.'
    ) ON CONFLICT (name) DO NOTHING;