import dotenv, os, typing, utils, commands
from interactions import slash_command, slash_option, Client, SlashContext, Intents, OptionType, SlashCommandChoice
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from utils import CONFIG_PATH, OPERATOR_ROLE_ID

dotenv.load_dotenv()

if not os.path.exists(CONFIG_PATH):
   utils.refresh_config({})

client = Client(
    token = os.getenv("TOKEN"),
    intents = Intents.GUILDS | Intents.MESSAGE_CONTENT | Intents.GUILD_MESSAGES,
    send_command_tracebacks = False # go go gadget stacktrace dump
)
prefixed_commands.setup(client, default_prefix="!")

@slash_command(
    name = "ping",
    description = "Returns the latency of the bot"
)
async def ping(context: SlashContext):
    print(utils.log_command_call("ping", context.author.username))

    await context.send(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@slash_command(
    name = "playerlist",
    description = "Get the list of players currently online."
)
async def playerlist(context: SlashContext):
    await context.defer()

    print(utils.log_command_call("playerlist", context.author.username))

    await context.send(commands.get_playerlist())

@slash_command(
    name = "mcserver_config",
    description = "Change server info for use in the MC API."
)
@slash_option(
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
@slash_option(
    name = "config_value",
    description = "Value the config is being changed to.",
    required = True,
    opt_type = OptionType.STRING
)
async def mcserver_config(context: SlashContext, config_name: str, config_value: str):
    print(utils.log_command_call("mcserver_config", context.author.username))

    operator_role = context.guild.get_role(OPERATOR_ROLE_ID) # hard coded role ID because I'm lazy, shut up

    output = ""
    if context.author.has_role(operator_role):
        output = commands.change_mcserver_config(config_name, config_value)
    else:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")
        output = "You do not have permission to use that command."

    await context.send(output)

@prefixed_command(name="ping")
async def ping_legacy(context: PrefixedContext):
    print(utils.log_command_call("ping", context.author.username, is_slash_command=False))

    await context.reply(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@prefixed_command(name="playerlist")
async def playerlist_legacy(context: PrefixedContext):
    print(utils.log_command_call("playerlist", context.author.username, is_slash_command=False))

    await context.reply(commands.get_playerlist(is_slash_command=False))

@prefixed_command(name="mcserver_config")
async def mcserver_config_legacy(context: PrefixedContext, config_name: typing.Optional[str], config_value = None):
    print(utils.log_command_call("mcserver_config", context.author.username, is_slash_command=False))

    valid_configs = ["domain", "port"]
    operator_role = context.guild.get_role(OPERATOR_ROLE_ID)

    if config_name == None:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration name\033[0;0m")
        output = "You must provide a configuration"

    elif config_value == None:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration value\033[0;0m")
        output = "You must provide a value to set the configuration to"

    else:
        if context.author.has_role(operator_role):
            output = commands.change_mcserver_config(config_name, config_value, is_slash_command=False)
        else:
            print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")
            output = "You do not have permission to use that command."

    await context.reply(output)

client.start()