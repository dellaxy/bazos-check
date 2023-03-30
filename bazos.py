import requests
import asyncio
from bs4 import BeautifulSoup
from discord.ext import commands

kategoria = "https://mobil.bazos.sk"

cat = kategoria + \
    "/{0}?hledat={1}&hlokalita=&humkreis=&cenaod=100&cenado={2}&order="

search = ["Playstation 5"]
price_filter = [550]

stock = []
stocknew = []

guild = None
channel = None
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('READY')
    global channel, guild, stock
    guild = client.get_guild(834750687770443847)
    channel = guild.get_channel(846015183000436767)
    p = nacitanie()
    pocetinzeratov = p[0]
    stock.extend(stocknew)

    while True:
        hodnoty = nacitanie()
        aktualne = hodnoty[0]
        print(pocetinzeratov)
        print(aktualne)
# ___________________________________________
        if aktualne > pocetinzeratov:
            print('pridany')
            novyinzerat = list(set(stocknew) - set(stock))
            new = ' '.join([str(n) for n in novyinzerat])
            stock += novyinzerat
            pocetinzeratov = aktualne
            print(novyinzerat)
            await channel.send("**Nový inzerát**" + new)
        elif aktualne < pocetinzeratov:
            print('odobraty')
            staryinzerat = list(set(stock) - set(stocknew))
            stock = list(set(stock) - set(staryinzerat))
            print(staryinzerat)
            pocetinzeratov = aktualne
# ___________________________________________
        await asyncio.sleep(900)

# ________________________________________________________________________________________________________________________________________________________________


@client.command()
async def quit(ctx):
    if ctx.channel.id is not channel.id:
        return
    await clear(10)
    await ctx.bot.logout()

# ________________________________________________________________________________________________________________________________________________________________


def nacitanie():
    stocknew.clear()
    x = 0
    y = 0
    pocet = 0
    # _________________________________________________________________ Listovanie medzi stránkami
    while (y != len(search)):
        link = str(cat)
        if x == 0:
            url = link.format("", str(search[y]), price_filter[y])

        else:
            url = link.format(str(x)+"/", str(search[y]), price_filter[y])

        x += 20
        r = requests.get(url)
    # _________________________________________________________________ Načítanie produktov zo stránky
        if r:
            soup = BeautifulSoup(r.content, features="html.parser")
            itms = soup.find_all(
                'div', attrs={'class': 'inzeraty inzeratyflex'})
            if len(itms) == 0:
                y += 1
                x = 0
            # ---------------------------------------------------- Porovnávanie produktov zo stránky s kľúčovými slovami
            for i in itms:
                name = i.find('span', attrs={'class': 'nadpis'})
                price = i.find('div', attrs={'class': 'inzeratycena'})
                link = name.find("a").get("href")
                price = price.text.strip("€").replace(" ", "")
                success = name.text.strip().lower()
                if str(search[y]) in success:
                    if (price.isnumeric()):
                        stocknew.append('\n'+name.text.strip() +
                                        ' - **'+price+' €** \n'+kategoria+link)
                    elif not price.isnumeric():
                        stocknew.append('\n'+name.text.strip() +
                                        ' - **'+price+'** \n'+kategoria+link)
                    pocet += 1

            # ----------------------------------------------------
        else:
            break
    return [pocet, stocknew]
    print(stock)
# _______________________________________________________________________________________________________________________________________________________________


async def clear(l):
    await channel.purge(limit=l, check=lambda msg: not msg.pinned)

client.run(BOT_TOKEN)
