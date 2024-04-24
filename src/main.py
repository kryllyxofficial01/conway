import mcstatus, dotenv, os, typing, ipaddress, utils
from interactions import slash_command, slash_option, Client, SlashContext, Intents, OptionType, SlashCommandChoice
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from utils import CONFIG_PATH

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

    configs = utils.load_config()

    domain = configs["domain"]
    port = configs["port"]

    try:
        mcserver = mcstatus.JavaServer(
            host = domain,
            port = port
        )

        try: output = ", ".join([player.name for player in mcserver.status().players.sample])
        except TypeError: output = "No players are online."
        else: await context.send(output)

    except:
        print(f"{utils.get_current_time()} | \033[1;33m/playerlist\033[0;0m: Prior call \033[1;31mtimed out\033[0;0m")

        await context.send("Connection timed out, likely due to an invalid server domain and/or port configuration")

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

    operator_role = context.guild.get_role(1167687375913234464) # hard coded role ID because I'm lazy, shut up

    if context.author.has_role(operator_role):
        configs = utils.load_config()

        error = False
        if config_name == "domain":
            try: ipaddress.ip_address(config_value)

            except ValueError:
                error = True

                print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid domain ({config_value})\033[0;0m")

                await context.send("Must be a valid domain")

        elif config_name == "port":
            try: config_value = int(config_value)

            except ValueError:
                error = True

                print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained a \033[1;31mnon-integer port ({config_value})\033[0;0m")

                await context.send("Port must be an integer")

            else:
               if config_value < 0 or config_value > 65535: # max port value
                    error = True

                    print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid port ({config_value})\033[0;0m")

                    await context.send("Port must be greater than 0 and less than 65535")

        if not error:
            configs[config_name] = config_value

            utils.refresh_config(configs)

            print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call changed \033[0;32m{config_name.capitalize()}\033[0;0m to \033[0;32m{config_value}\033[0;0m")

            await context.send(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

    else:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")

        await context.send("You do not have permission to use that command.")

@prefixed_command(name="ping")
async def ping_legacy(context: PrefixedContext):
    print(utils.log_command_call("ping", context.author.username, is_slash_command=False))

    await context.reply(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@prefixed_command(name="playerlist")
async def playerlist_legacy(context: PrefixedContext):
    print(utils.log_command_call("playerlist", context.author.username, is_slash_command=False))

    configs = utils.load_config()

    domain = configs["domain"]
    port = configs["port"]

    try:
        mcserver = mcstatus.JavaServer(
            host = domain,
            port = port,
        )

    except:
        print(f"{utils.get_current_time()} | \033[1;33m/playerlist\033[0;0m: Prior call \033[1;31mtimed out\033[0;0m")

        await context.reply("Connection timed out, likely due to an invalid server domain and/or port configuration")

    else:
        try: output = ", ".join([player.name for player in mcserver.status().players.sample])
        except TypeError: output = "No players are online."
        else: await context.reply(output)

@prefixed_command(name="mcserver_config")
async def mcserver_config_legacy(context: PrefixedContext, config_name: typing.Optional[str], config_value = None):
    print(utils.log_command_call("mcserver_config", context.author.username, is_slash_command=False))

    if config_name == None:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration name\033[0;0m")

        await context.reply("You must provide a configuration")

    elif config_value == None:
        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration value\033[0;0m")

        await context.reply("You must provide a value to set the configuration to")

    else:
        operator_role = context.guild.get_role(1167687375913234464)

        valid_configs = ["domain", "port"]

        if context.author.has_role(operator_role):
            configs = utils.load_config()

            if config_name in valid_configs:
                error = False
                if config_name == "domain":
                    try: ipaddress.ip_address(config_value)

                    except ValueError:
                        error = True

                        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid domain ({config_value})\033[0;0m")

                        await context.reply("Port must be a valid domain")

                elif config_name == "port":
                    try: config_value = int(config_value)

                    except ValueError:
                        error = True

                        print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained a \033[1;31mnon-integer port ({config_value})\033[0;0m")

                        await context.reply("Port must be an integer")

                    else:
                        if config_value < 0 or config_value > 65535:
                            error = True

                            print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid port ({config_value})\033[0;0m")

                            await context.reply("Port must be greater than 0 and less than 65535")

                if not error:
                    configs[config_name] = config_value

                    utils.refresh_config(configs)

                    print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call changed \033[0;32m{config_name.capitalize()}\033[0;0m to \033[0;32m{config_value}\033[0;0m")

                    await context.reply(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

        else:
            print(f"{utils.get_current_time()} | \033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")

            await context.reply("You do not have permission to use that command.")

client.start()