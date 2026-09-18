-- Track whether the operator was notified after a successful lead insert.
ALTER TABLE leads ADD COLUMN notified_at TEXT;
ALTER TABLE leads ADD COLUMN notify_status TEXT;
