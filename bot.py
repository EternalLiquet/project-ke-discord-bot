import hikari
import crescent
import os
import miru
import requests
from miru.ext import nav
import json
from bs4 import BeautifulSoup

bot = hikari.GatewayBot(os.getenv('BOT_TOKEN'))
client = crescent.Client(bot)
miru.install(bot)

@client.include
@crescent.command(name="rank", description="Shows a range of entries from the project ke exchange points ranking site")
class Rank:
    minimum = crescent.option(int, description="The top rank to show", min_value=1, default=1)
    maximum = crescent.option(int, description="The bottom rank to show", min_value=1, default=10)

    async def callback(self, ctx: crescent.Context) -> None:
        if self.minimum > self.maximum:
            await ctx.respond("The top rank cannot be greater than the bottom rank")
            return
        await ctx.respond(f"Showing ranks from {self.minimum} to {self.maximum}")
        URL = "https://projectke.com/exchange-points/"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        table_rows = soup.find_all("tr")

        if(self.maximum > len(table_rows)):
            await ctx.respond("The bottom rank is too high, the maximum value is " + str(len(table_rows) - 1))
            return

        message_to_send = "Exchange Points Ranking\n"

        count = self.minimum

        for i in range(self.minimum, self.maximum + 1):
            td = table_rows[i].find_all("td")
            row = [i.text for i in td]
            message_to_send += f"{count}. {row[0]} - {row[1]}\n"
            count += 1
        await ctx.respond(message_to_send)

@client.include
@crescent.command(name="search", description="Searches the Project Ke shop for a specific search term")
class Search:
    search_term = crescent.option(str, description="The search term to search for")

    async def callback(self, ctx: crescent.Context) -> None:
        response = requests.get(os.getenv('PROJECT_KE_API_BASE_URL') + 'app/goods/list?goodsName=' + self.search_term)
        print(response.json())
        pages = []
        for x in range(len(response.json()['data'])):
            pages.append(hikari.Embed(title="Search Result for \"" + self.search_term + "\"", description=response.json()['data'][x]['goodsName']).set_image(response.json()['data'][x]['goodsImage']))
        
        navigator = nav.NavigatorView(pages=pages)

        print(dir(navigator))

        await navigator.send(ctx.interaction, ephemeral=True)

bot.run()