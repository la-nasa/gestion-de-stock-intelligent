-- Exécuter ce script dans le SQL Editor de Supabase
-- après avoir créé un projet gratuit

-- Créer les extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Créer les tables principales
CREATE TABLE IF NOT EXISTS accounts_user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    matricule VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'VIEWER',
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    password VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Créer un utilisateur admin par défaut
-- Mot de passe: IUC@2026! (hashé)
INSERT INTO accounts_user (email, first_name, last_name, matricule, role, is_active, is_staff, is_superuser, password)
VALUES ('admin@iuc.cm', 'Admin', 'IUC', 'ADM001', 'ADMIN', TRUE, TRUE, TRUE,
        'pbkdf2_sha256$720000$salt$hash...'); -- Remplacer par le vrai hash