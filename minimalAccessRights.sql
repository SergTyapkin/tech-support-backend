REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "tech-support-backend";
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM "tech-support-backend";
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM "tech-support-backend";

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "tech-support-backend";
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO "tech-support-backend";
GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO "tech-support-backend";

-- Now "tech-support-backend" can only SELECT, UPDATE, INSERT, DELETE in all tables
-- And use trigger functions
