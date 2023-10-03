import discord
from .helpers import get_enchant_data_string, get_villager_data_string, check_villager


def pluralize(s, n):
    return s if n == 1 else s + 's'


class Pages:
    def __init__(self, dictionary, keys_per_page=10):
        self.dictionary = dictionary
        self.keys = list(dictionary)
        self.total_keys = len(dictionary)
        self.page = 1
        self.keys_per_page = keys_per_page
        self.total_pages = self.key_index_to_page(self.total_keys - 1)

    def get_current_page(self):
        res = [f'Page {self.page}/{self.total_pages:,} '
               f'({self.total_keys:,} {pluralize("item", self.total_keys)} total):\n\n']

        index_offset = (self.page - 1) * self.keys_per_page  # Skip past prior pages
        keys_left = self.total_keys - (self.page - 1) * self.keys_per_page
        # Get min between keys_per_page and # of keys left (so last page doesn't index error)
        for n in range(min(self.keys_per_page, keys_left)):  # Print items on page
            index = index_offset + n
            res.append(self.get_item_text(index) + '\n')
        return ''.join(res)

    def key_index_to_page(self, key_index):  # key_index starts counting from 0
        # Ex with keys_per_page = 10:
        # 0-9 = page 1, 10-19 = page 2
        return 1 + key_index // self.keys_per_page

    def next_page(self):  # Positive integer
        if self.page < self.total_pages:
            self.page += 1

    def prev_page(self):  # Positive integer
        if self.page > 1:
            self.page -= 1

    def get_item_text(self, index):  # index from the list of keys
        raise NotImplementedError


class EnchantPages(Pages):
    def get_item_text(self, index):
        return get_enchant_data_string(self.keys[index])


class VillagerPages(Pages):
    def __init__(self, dictionary, unused_villagers):
        super().__init__(dictionary, keys_per_page=5)
        self.unused_villagers = unused_villagers

    def get_current_page(self):
        res = [f'Page {self.page}/{self.total_pages:,} '
               f'({self.total_keys:,} {pluralize("item", self.total_keys)} total):\n']

        if self.unused_villagers:
            res.append(f"Villagers with no bests: {', '.join(self.unused_villagers)}\n\n")
        else:
            res.append('\n')

        index_offset = (self.page - 1) * self.keys_per_page  # Skip past prior pages
        keys_left = self.total_keys - (self.page - 1) * self.keys_per_page
        # Get min between keys_per_page and # of keys left (so last page doesn't index error)
        for n in range(min(self.keys_per_page, keys_left)):  # Print items on page
            index = index_offset + n
            res.append(self.get_item_text(index) + '\n')
        return ''.join(res)

    def get_item_text(self, index):
        return get_villager_data_string(self.keys[index])


class PageView(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=30)
        self.author = None
        self.message = None
        self.pages = pages

    async def interaction_check(self, interaction):
        if self.author == interaction.user:
            return True
        else:
            await interaction.response.send_message('Only the command sender can use this!', ephemeral=True,
                                                    delete_after=5)
            return False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label='<', style=discord.ButtonStyle.gray, disabled=True)
    async def left(self, interaction, button):
        self.pages.prev_page()
        button.disabled = self.pages.page == 1
        self.children[1].disabled = False
        await interaction.response.edit_message(content=self.pages.get_current_page(), view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.gray)
    async def right(self, interaction, button):
        self.pages.next_page()
        button.disabled = self.pages.page == self.pages.page == self.pages.total_pages
        self.children[0].disabled = False
        await interaction.response.edit_message(content=self.pages.get_current_page(), view=self)
