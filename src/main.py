import interactions, mcstatus, json, pathlib, dotenv, os

dotenv.load_dotenv()

config_path = str(pathlib.Path(__file__).parent.absolute()) + "/configs.json"

client = interactions.Client(token=os.getenv("TOKEN"), default_scope=976256461887897650)

@interactions.slash_command(
    name = "ping",
    description = "Get the current latency of the bot."
)
async def ping(context: interactions.SlashContext):
    await context.send(f"{round(client.latency * 1000, 2)} ms")

@interactions.slash_command(
    name = "playerlist",
    description = "Get the list of players currently online."
)
async def playerlist(context: interactions.SlashContext):
    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    mcserver = mcstatus.JavaServer(host=configs["domain"], port=int(configs["port"]))

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
    opt_type = interactions.OptionType.STRING,
    choices = [
        interactions.SlashCommandChoice(
            name = "Domain",
            value = "domain"
        ),
        interactions.SlashCommandChoice(
            name = "Port",
            value = "port"
        )
    ]
)
@interactions.slash_option(
    name = "config_value",
    description = "Value the config is being changed to.",
    required = True,
    opt_type = interactions.OptionType.STRING
)
async def mcserver_config(context: interactions.SlashContext, config_name: str, config_value: str):
    await context.defer()

    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    configs[config_name] = config_value

    with open(config_path, "w") as config_file:
        json.dump(configs, config_file, indent=4)

    await context.send(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

client.start()