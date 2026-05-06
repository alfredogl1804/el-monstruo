-- El Monstruo — Tabla users canónica para Manus-Oauth
-- Compatible con TiDB / MySQL 8 / Postgres 14+ (con ajustes JSONB).
-- Generado por skill manus-oauth-pattern v0.1.0
--
-- Naming inviolable per DSC-G-004:
--   La tabla se llama `users` (estándar). NO `monstruo_users`, NO `app_users`.
--   Las columnas con identidad usan prefijo `manus_` cuando refieren a Manus
--   (manus_token, manus_user_id) para distinguir de campos del proyecto.

CREATE TABLE IF NOT EXISTS users (
  id              VARCHAR(64)  PRIMARY KEY,             -- = manus user_id (sub claim)
  email           VARCHAR(255) UNIQUE NOT NULL,
  email_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
  name            VARCHAR(255),
  avatar_url      TEXT,

  -- Token de Manus encrypted at rest (ver MONSTRUO_TOKEN_ENCRYPTION_KEY)
  manus_token_encrypted   TEXT,
  manus_token_expires_at  TIMESTAMP NULL,
  manus_refresh_token_encrypted TEXT,

  -- Auditoría
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login_at   TIMESTAMP NULL,
  last_login_ip   VARCHAR(64),
  last_login_user_agent TEXT,

  -- Estado del usuario
  status          VARCHAR(32) NOT NULL DEFAULT 'active',  -- active | suspended | deleted
  suspended_reason TEXT,
  suspended_at    TIMESTAMP NULL,

  -- Metadata flexible específica del proyecto
  metadata_json   JSON
);

CREATE INDEX idx_users_email          ON users(email);
CREATE INDEX idx_users_status         ON users(status);
CREATE INDEX idx_users_last_login_at  ON users(last_login_at);

-- Tabla auxiliar de sesiones (HTTP-only cookies firmadas)
CREATE TABLE IF NOT EXISTS user_sessions (
  id              VARCHAR(64)  PRIMARY KEY,             -- session_id firmado
  user_id         VARCHAR(64)  NOT NULL,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at      TIMESTAMP    NOT NULL,
  revoked_at      TIMESTAMP    NULL,
  ip_address      VARCHAR(64),
  user_agent      TEXT,

  CONSTRAINT fk_user_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_sessions_user_id    ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
