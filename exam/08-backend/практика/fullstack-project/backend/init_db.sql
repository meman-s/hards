CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_title ON items (title);
CREATE TABLE IF NOT EXISTS log_items (
    history_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE
OR REPLACE FUNCTION log_items_add() RETURNS TRIGGER AS $$ BEGIN
    IF TG_OP = 'INSERT' THEN
    INSERT INTO
        log_items (item_id, added_at)
    VALUES
        (NEW .id, CURRENT_TIMESTAMP);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trigger_log_items AFTER
INSERT
    ON items FOR EACH ROW EXECUTE FUNCTION log_items_add();