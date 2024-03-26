import interactions, mcstatus, json, pathlib, dotenv, os
from interactions import Client, SlashContext, Intents, OptionType, SlashCommandChoice
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext

dotenv.load_dotenv()

config_path = str(pathlib.Path(__file__).parent.absolute()) + "/configs.json"

client = Client(
    token = os.getenv("TOKEN"),
    default_scope = 1167687057360027668,
    intents = Intents.GUILDS | Intents.MESSAGE_CONTENT | Intents.GUILD_MESSAGES
)
prefixed_commands.setup(client, default_prefix="!")

@interactions.slash_command(
    name = "ping",
    description = "Returns the latency of the bot"
)
async def ping(context: SlashContext):
    await context.send(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@interactions.slash_command(
    name = "playerlist",
    description = "Get the list of players currently online."
)
async def playerlist(context: SlashContext):
    await context.defer()

    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    mcserver = mcstatus.JavaServer(
        host = configs["domain"],
        port = int(configs["port"])
    )

    try:
        output = ", ".join([player.name for player in mcserver.status().players.sample])
    except TypeError:
        output = "No players are online."

    await context.send(output)

@interactions.slash_command(
    name = "mcserver_config",
    description = "Change server info for use in the MC API."
)
@interactions.slash_option(
    name = "config_name",
    description = "Name of the config being changed.",
    required = True,
    opt_type = OptionType.STRING,
    choices = [
        SlashCommandChoice(
            name = "Domain",
            value = "domain"
        ),
        SlashCommandChoice(
            name = "Port",
            value = "port"
        )
    ]
)
@interactions.slash_option(
    name = "config_value",
    description = "Value the config is being changed to.",
    required = True,
    opt_type = OptionType.STRING
)
async def mcserver_config(context: SlashContext, config_name: str, config_value: str):
    operator_role = context.guild.get_role(1167687375913234464)

    if context.author.has_role(operator_role):
        with open(config_path, "r") as config_file:
            configs = json.load(config_file)

        configs[config_name] = config_value

        with open(config_path, "w") as config_file:
            json.dump(configs, config_file, indent=4)

        await context.send(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

    else:
        await context.send("You do not have permission to use that command.")

@prefixed_command(name="ping")
async def ping_legacy(context: PrefixedContext):
    await context.reply(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@prefixed_command(name="playerlist")
async def playerlist_legacy(context: PrefixedContext):
    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    mcserver = mcstatus.JavaServer(
        host = configs["domain"],
        port = int(configs["port"])
    )

    try:
        output = ", ".join([player.name for player in mcserver.status().players.sample])
    except TypeError:
        output = "No players are online."

    await context.reply(output)

@prefixed_command(name="mcserver_config")
async def mcserver_config_legacy(context: PrefixedContext, config_name: str, config_value: str):
    operator_role = context.guild.get_role(1167687375913234464)

    if context.author.has_role(operator_role):
        with open(config_path, "r") as config_file:
            configs = json.load(config_file)

        if config_name in ("domain", "port"):
            configs[config_name] = config_value

            with open(config_path, "w") as config_file:
                json.dump(configs, config_file, indent=4)

            await context.reply(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

        else:
            await context.reply(f"No config name '{config_name}'")

    else:
        await context.send("You do not have permission to use that command.")

client.start()