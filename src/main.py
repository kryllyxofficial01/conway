import dotenv, os, typing, utils, commands
from interactions import slash_command, slash_option, Client, SlashCommand, SlashContext, SlashCommandChoice, OptionType
from interactions import Intents, Member
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from utils import CONFIG_PATH, STRIKES_PATH, OPERATOR_ROLE_ID

dotenv.load_dotenv()

if not os.path.exists(CONFIG_PATH):
   utils.refresh_config({})

client = Client(
    token = os.getenv("TOKEN"),
    intents = Intents.ALL,
    send_command_tracebacks = False # go go gadget remove stacktrace dumps
)
prefixed_commands.setup(client, default_prefix="!")

strikes_base = SlashCommand(
    name = "strikes",
    description = "Handle strikes"
)

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

    operator_role = context.guild.get_role(OPERATOR_ROLE_ID)

    if context.author.has_role(operator_role):
        await context.send(commands.change_mcserver_config(config_name, config_value))
    else:
        print(utils.log_message("mcserver_config", "Prior call \033[1;31mnot permitted\033[0;0m", True))
        await context.send("You do not have permission to use that command.")

@strikes_base.subcommand(
    sub_cmd_name = "view",
    sub_cmd_description = "Get the strike counts of every player"
)
@slash_option(
    name = "user",
    description = "User to view the strikes of",
    required = False,
    opt_type = OptionType.MENTIONABLE
)
async def strikes_view(context: SlashContext, user: Member = None):
    print(utils.log_command_call("strikes view", context.author.username))

    operator_role = context.guild.get_role(OPERATOR_ROLE_ID)

    if context.author.has_role(operator_role):
        if user == None: await context.send(commands.get_strikes(context.guild))
        else:
            strikes = utils.get_strikes()

            print(utils.log_message(
                "strikes view",
                f"Prior call \033[0;32mrequested strikes for '{user.username}'\033[0;0m",
                True
            ))

            await context.send(f"{user.username} ({user.display_name}): {strikes[str(user.id)]}")

    else:
        print(utils.log_message("strikes view", "Prior call \033[1;31mnot permitted\033[0;0m", True))
        await context.send("You do not have permission to use that command.")

@strikes_base.subcommand(
    sub_cmd_name = "add",
    sub_cmd_description = "Add strikes to a player"
)
@slash_option(
    name = "user",
    description = "User to add strikes to",
    required = True,
    opt_type = OptionType.MENTIONABLE
)
@slash_option(
    name = "strikes",
    description = "Number of strikes to add",
    required = True,
    opt_type = OptionType.INTEGER
)
async def strikes_add(context: SlashContext, user: Member, strikes: int):
    print(utils.log_command_call("strikes add", context.author.username))

    operator_role = context.guild.get_role(OPERATOR_ROLE_ID)

    if context.author.has_role(operator_role):
        await context.send(commands.add_strikes(user.id, strikes, context.guild))
    else:
        print(utils.log_message("strikes add", "Prior call \033[1;31mnot permitted\033[0;0m", True))
        await context.send("You do not have permission to use that command.")

@strikes_base.subcommand(
    sub_cmd_name = "clear",
    sub_cmd_description = "Clear all strikes"
)
async def strikes_clear(context: SlashContext):
    print(utils.log_command_call("strikes clear", context.author.username))

    operator_role = context.guild.get_role(OPERATOR_ROLE_ID)

    if context.author.has_role(operator_role):
        await context.send(commands.clear_strikes())
    else:
        print(utils.log_message("strikes clear", "Prior call \033[1;31mnot permitted\033[0;0m", True))
        await context.send("You do not have permission to use that command.")

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
        print(utils.log_message(
            "mcserver_config",
            "Prior call \033[1;31mmissing configuration name\033[0;0m",
            False
        ))

        await context.send("You must provide a configuration")

    elif config_value == None:
        print(utils.log_message(
            "mcserver_config",
            "Prior call \033[1;31mmissing configuration value\033[0;0m",
            False
        ))

        await context.send("You must provide a value to set the configuration to")

    else:
        if context.author.has_role(operator_role):
            if config_name in valid_configs:
                await context.send(commands.change_mcserver_config(config_name, config_value, is_slash_command=False))
            else:
                print(utils.log_message(
                    "mcserver_config",
                    f"Prior call contained \033[1;31minvalid config name ('{config_name}')\033[0;0m",
                    False
                ))

                await context.send("Invalid config name")

        else:
            print(utils.log_message("mcserver_config", "Prior call \033[1;31mnot permitted\033[0;0m", False))
            await context.send("You do not have permission to use that command.")

client.start()