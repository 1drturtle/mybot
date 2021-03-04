from discord.ext import commands
import typing
from asyncpg.exceptions import UniqueViolationError



# Each User has one To-do list

class ToDoItem:
    def __init__(self, item_id: int, list_id: int, item: str, item_index: int):
        self.item_id = item_id
        self.list_id = list_id
        self.item = item
        self.item_index = item_index


class ToDoList:
    def __init__(self, list_id, author_id, items: typing.List[ToDoItem]):
        self.list_id = list_id
        self.author_id = author_id
        self.items = items

    @classmethod
    async def from_db(cls, db, author_id: int):
        """
        Gets an instance from the database
        """
        db_result = await db.fetchrow('SELECT * FROM todo_lists WHERE user_id = $1', author_id)
        if db_result is None:
            raise LookupError(f'Could not find a to-do list owned by user with id {author_id}')
        todo_items = []
        for todo_item in await db.fetch('SELECT * FROM todo_items WHERE list_id = $1', db_result.get('list_id')):
            x = todo_item.get
            todo_items.append(ToDoItem(x('item_id'), x('list_id'), x('item'), x('item_index')))
        return cls(db_result.get('list_id'), author_id, todo_items)

    @classmethod
    async def new(cls, db, author_id):
        """
        Creates a new To-Do list for a user.
        """
        query = 'INSERT INTO todo_lists(user_id, name) VALUES($1, default)'
        try:
            await db.execute(query, author_id)
        except UniqueViolationError:
            return None
        return cls.from_db(db, author_id)


class Todo(commands.Cog):
    """Commands for the To-Do list."""

    def __int__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    async def get_todo_list(self, author_id):
        """
        Gets a user's to-do list, and creates one if it doesn't exist.

        :param int author_id: id of user
        :return:
        """
        try:
            todo = ToDoList.from_db(self.db, author_id)
        except LookupError:
            todo = ToDoList.new(self.db, author_id)
        finally:
            return todo


def setup(bot):
    bot.add_cog(Todo(bot))
