from discord.ext import commands
from asyncpg.exceptions import UniqueViolationError
from fuzzywuzzy import process
import logging

log = logging.getLogger(__name__)


def check_tag_name(name: str, illegals: list):
    if len(name) > 50:
        raise ValueError('Tag Name must be less than 50 characters.')
    if name in illegals:
        raise ValueError('Tag name must not be a built-in command or tag.')
    if name[0] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        raise ValueError('Tag name must start with a letter.')
    return True


class Tags(commands.Cog):
    """
    Tag commands for display of custom text.
    Inspired by RoboDanny's tag system.
    """

    def __init__(self, bot):
        self.bot = bot
        self.illegals = ['tag', 'create', 'add', 'new', 'search', 'info']

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('Tag commands cannot be used in private messages.')
        return True

    async def create_tag(self, ctx, name: str, content: str):
        """
        Creates a tag in the database. Perform name checking before running this function.
        :param ctx: The context to grab the author id and guild id from.
        :param str name: The name of the Tag
        :param str content: The tag's contents.
        """
        try:
            await self.bot.db.execute(
                f'INSERT INTO tags(name, content, author_id, guild_id)'
                f'VALUES ($1, $2, $3, $4)',
                name,
                content,
                ctx.author.id,
                ctx.guild.id
            )
        except UniqueViolationError:
            return False
        else:
            log.debug(f'Tag created in {ctx.guild} ({ctx.guild.id})'
                      f' by {ctx.author.name + ctx.author.discriminator} ({ctx.author.id})')
            return True

    async def fetch_tag(self, ctx, tag_name, owner=True):
        if owner:
            return await self.bot.db.fetchrow(f'SELECT * FROM tags WHERE name=$1 and author_id=$2 and guild_id=$3',
                                              tag_name,
                                              ctx.author.id,
                                              ctx.guild.id)
        else:
            return await self.bot.db.fetchrow(f'SELECT * FROM tags WHERE name=$1 and guild_id=$2',
                                              tag_name,
                                              ctx.guild.id)

    async def increment_tag(self, tag_id):
        """
        Increments the use count on a tag.
        """
        log.debug(f'Tag {tag_id} executed.')
        await self.bot.db.execute(
            f'UPDATE tags'
            '    SET uses = uses + 1\n'
            'WHERE tag_id = $1',
            tag_id
        )

    async def find_similar(self, tag_name, guild_id, limit=10):
        db_result = await self.bot.db.fetch('SELECT * from tags WHERE guild_id = $1', guild_id)
        names = [x.get('name') for x in db_result]
        results = process.extract(tag_name, names, limit=limit)
        out = []
        for result in results:
            for x in db_result:
                # at least 20% match.
                if x.get('name') == result[0] and result[1] > 20:
                    out.append(x)
        return out

    @commands.group(name='tag', invoke_without_command=True)
    async def tag(self, ctx, tag_name):
        """
        Tag commands for display of custom text.
        Inspired by RoboDanny's tag system.

        `tag_name` - The tag to look up.
        """
        query = f'SELECT * from tags WHERE name = $1'
        result = await self.bot.db.fetchrow(query, tag_name)
        if not result:
            similars = await self.find_similar(tag_name, ctx.guild.id)
            similar_tags = '\n'.join([f'- {x.get("name")}' for x in similars])
            if similar_tags:
                return await ctx.send(f'No tags found with that name.\nSimilar Tags:\n{similar_tags}')
            else:
                return await ctx.send('No tags found with that name or a similar name.')
        await self.increment_tag(result.get('tag_id'))
        return await ctx.send(result.get('content'))

    @tag.command(name='create', aliases=['new'])
    async def tag_create(self, ctx, tag_name, *, tag_content):
        """
        Creates a new tag.
        `tag_name` - The name of the tag. Must start with a letter and cannot be longer than 50 characters.
        `tag_content` - Content of the tag. Does not require quotes around whole thing. 1800 characters or less.
        """
        try:
            check_tag_name(tag_name, self.illegals)
        except ValueError:
            return await ctx.send(f'An invalid tag name was provided. Check {ctx.prefix}help '
                                  f'{ctx.command.qualified_name} for more information')

        if len(tag_content) > 1800:
            return await ctx.send('The content provided was larger than 1800 characters and has been rejected.')
        if len(tag_content) < 3:
            return await ctx.send('Tag content must be at least three characters.')
        result = await self.create_tag(ctx, tag_name, tag_content)
        if not result:
            return await ctx.send('A tag with that name already exists in this server.')
        return await ctx.send(f'Tag `{tag_name}` has been successfully created.')

    @tag.command(name='edit')
    async def tag_edit(self, ctx, tag_name, *, new_content):
        """
        Creates a new tag.
        `tag_name` - The name of the tag. Must start with a letter and cannot be longer than 50 characters.
        `tag_content` - Content of the tag. Does not require quotes around whole thing. 1800 characters or less.
        """

        if len(new_content) > 1800:
            return await ctx.send('The content provided was larger than 1800 characters and has been rejected.')
        if len(new_content) < 4:
            return await ctx.send('Tag content must be at least four characters.')
        if not await self.fetch_tag(ctx, tag_name):
            return await ctx.send(f'Could not find a tag in this server owned by you with name `{tag_name}`.')
        await self.bot.db.execute(
            f'UPDATE tags'
            '    SET content = $4\n'
            'WHERE name = $1 and author_id = $2 and guild_id = $3',
            tag_name,
            ctx.author.id,
            ctx.guild.id,
            new_content
        )
        log.debug(f'Tag {tag_name} edited in {ctx.guild} ({ctx.guild.id})'
                  f' by {ctx.author.name + ctx.author.discriminator} ({ctx.author.id})')
        return await ctx.send(f'Tag `{tag_name}` has been successfully edited.')

    @tag.command(name='delete')
    async def tag_delete(self, ctx, tag_name):
        """
        Deletes an existing tag.
        `tag_name` - The tag to delete.
        """
        if not await self.fetch_tag(ctx, tag_name):
            return await ctx.send(f'Could not find a tag in this server owned by you with name `{tag_name}`.')

        prompt = await ctx.prompt('Tag Deletion Confirmation', f'Please enter the tag you are trying to delete '
                                                               f'exactly to confirm this action.\n'
                                                               f'You are attempting to delete `{tag_name}`.')
        if prompt != tag_name:
            return await ctx.send('Action cancelled!', delete_after=10)

        await self.bot.db.execute(
            'DELETE FROM tags WHERE name = $1 and author_id = $2 and guild_id = $3',
            tag_name,
            ctx.author.id,
            ctx.guild.id
        )
        log.debug(f'Tag {tag_name} deleted in {ctx.guild} ({ctx.guild.id})'
                  f' by {ctx.author.name + ctx.author.discriminator} ({ctx.author.id})')
        return await ctx.send(f'Tag `{tag_name}` has been deleted.')

    @tag.command(name='info')
    async def tag_info(self, ctx, tag_name):
        """
        Gets meta information about a tag.
        `tag_name` - Name of tag to look up.
        """
        tag = await self.fetch_tag(ctx, tag_name, False)
        if not tag:
            return await ctx.send(f'Could not find a tag in this server with name `{tag_name}`.')
        embed = ctx.embed
        embed.title = 'Tag Info - ' + tag_name
        embed.add_field(name='Owner', value=f'<@{tag.get("author_id")}>')
        embed.add_field(name='Uses', value=tag.get('uses'))
        return await ctx.send(embed=embed)

    @tag.command(name='list')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tag_list(self, ctx):
        """
        Lists your most common 25 tags
        """
        tags = await self.bot.db.fetch(
            'SELECT * from tags WHERE guild_id = $1 and author_id = $2\n'
            'ORDER BY uses DESC\n'
            'LIMIT 25',
            ctx.guild.id,
            ctx.author.id
        )
        embed = ctx.embed
        embed.title = f'{ctx.author.display_name}\'s Tags.'
        embed.description = '\n'.join([f'- {x.get("name")}' for x in tags]) if tags else 'You do not have any tags.'
        return await ctx.send(embed=embed)

    @tag.command(name='search')
    async def tag_search(self, ctx, tag_name):
        """Searches for a tag in this server."""
        similar = await self.find_similar(tag_name, ctx.guild.id)
        embed = ctx.embed
        embed.title = f'Search result for {tag_name}'
        embed.description = '\n'.join([f'- {x.get("name")}' for x in similar]) if similar else 'No tag found.'
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
