-- Atlas Memory System Schema
-- Hybrid markdown + SQLite architecture

-- Facts extracted from conversations (long-term memory)
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    source TEXT,  -- 'conversation', 'manual', 'migration'
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Fact embeddings for semantic search
CREATE TABLE IF NOT EXISTS fact_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_id INTEGER NOT NULL UNIQUE,
    embedding BLOB NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (fact_id) REFERENCES facts(id) ON DELETE CASCADE
);

-- Soul aspects (agent's evolving identity)
CREATE TABLE IF NOT EXISTS soul (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aspect TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Conversation messages (for semantic search of past conversations)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    session_id TEXT DEFAULT 'main',
    token_count INTEGER,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Message embeddings for semantic search
CREATE TABLE IF NOT EXISTS message_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL UNIQUE,
    embedding BLOB NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Rolling summaries for context efficiency
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT DEFAULT 'main',
    start_message_id INTEGER NOT NULL,
    end_message_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Daily logs index (synced from markdown files)
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_summaries_session ON summaries(session_id, end_message_id);
CREATE INDEX IF NOT EXISTS idx_soul_aspect ON soul(aspect);
CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date);

-- FTS5 for keyword search on facts
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    category,
    subject, 
    content,
    content='facts',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, category, subject, content)
    VALUES (new.id, new.category, new.subject, new.content);
END;

CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, category, subject, content)
    VALUES ('delete', old.id, old.category, old.subject, old.content);
END;

CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, category, subject, content)
    VALUES ('delete', old.id, old.category, old.subject, old.content);
    INSERT INTO facts_fts(rowid, category, subject, content)
    VALUES (new.id, new.category, new.subject, new.content);
END;
