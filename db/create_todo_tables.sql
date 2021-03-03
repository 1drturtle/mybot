-- Uncomment lines below to reset database. Otherwise it will create the TODO tables and not overwrite tables with the same name.
-- DROP TABLE IF EXISTS todo_items;
-- DROP TABLE IF EXISTS todo_lists;

CREATE TABLE IF NOT EXISTS todo_lists(
	list_id INT GENERATED ALWAYS AS IDENTITY,
	user_id BIGINT NOT NULL,
	name TEXT DEFAULT 'default',
	PRIMARY KEY (list_id)
);

CREATE TABLE IF NOT EXISTS todo_items(
	item_id INT GENERATED ALWAYS AS IDENTITY,
	list_id INT NOT NULL,
	item TEXT NOT NULL,
	item_index SERIAL,
	PRIMARY KEY (item_id),
	CONSTRAINT fk_todo_item_to_list
		FOREIGN KEY (list_id)
			REFERENCES todo_lists(list_id)
			ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_todo_items_in_same_list_index ON todo_items(list_id, item_index);