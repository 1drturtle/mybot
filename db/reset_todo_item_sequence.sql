DELETE FROM todo_items WHERE item_index = 'abc123';
-- In Python, go through each row in the user's list and change the index WHERE index >= deleted_index and index -= 1
SELECT SETVAL('todo_items_item_index_seq', MAX(item_index)) FROM todo_items WHERE list_id = :list_to_update;