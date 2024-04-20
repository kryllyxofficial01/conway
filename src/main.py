import interactions, mcstatus, json, pathlib, dotenv, os
from interactions import Client, SlashContext, Intents, OptionType, SlashCommandChoice
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
import typing, ipaddress

dotenv.load_dotenv()

config_path = str(pathlib.Path(__file__).parent.absolute()) + "/configs.json"

if not os.path.exists(config_path):
    with open(config_path, 'w') as file:
        json.dump({}, file, indent=4)

client = Client(
    token = os.getenv("TOKEN"),
    default_scope = 1167687057360027668,
    intents = Intents.GUILDS | Intents.MESSAGE_CONTENT | Intents.GUILD_MESSAGES,
    send_command_tracebacks = False # go go gadget stacktrace dump
)
prefixed_commands.setup(client, default_prefix="!")

@interactions.slash_command(
    name = "ping",
    description = "Returns the latency of the bot"
)
async def ping(context: SlashContext):
    print(f"\033[1;33m/ping\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")
    await context.send(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@interactions.slash_command(
    name = "playerlist",
    description = "Get the list of players currently online."
)
async def playerlist(context: SlashContext):
    await context.defer()

    print(f"\033[1;33m/playerlist\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")

    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    domain = configs["domain"]
    port = configs["port"]

    try:
        mcserver = mcstatus.JavaServer(
            host = domain,
            port = port,
        )

        try:
            output = ", ".join([player.name for player in mcserver.status().players.sample])
        except TypeError:
            output = "No players are online."

        await context.send(output)

    except:
        print("\033[1;33m/playerlist\033[0;0m: Prior call \033[1;31mtimed out\033[0;0m")
        await context.send("Connection timed out, likely due to an invalid server domain and/or port configuration")

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
    print(f"\033[1;33m/mcserver_config\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")

    operator_role = context.guild.get_role(1167687375913234464) # hard coded role ID because I'm lazy, shut up

    if context.author.has_role(operator_role):
        with open(config_path, "r") as config_file:
            configs = json.load(config_file)

        error = False
        if config_name == "domain":
            try: ipaddress.ip_address(config_value)
            except ValueError:
                print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid domain ({config_value})\033[0;0m")
                await context.send("Port must be a valid domain")
                error = True

        elif config_name == "port":
            try: config_value = int(config_value)

            except ValueError:
                print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained a \033[1;31mnon-integer port ({config_value})\033[0;0m")
                await context.send("Port must be an integer")
                error = True

            else:
               if config_value < 0 or config_value > 65535: # max port value
                    print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid port ({config_value})\033[0;0m")
                    await context.send("Port must be greater than 0 and less than 65535")
                    error = True

        if not error:
            configs[config_name] = config_value

            with open(config_path, "w") as config_file:
                json.dump(configs, config_file, indent=4)

            print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call changed \033[0;32m{config_name.capitalize()}\033[0;0m to \033[0;32m{config_value}\033[0;0m")
            await context.send(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

    else:
        print("\033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")
        await context.send("You do not have permission to use that command.")

@prefixed_command(name="ping")
async def ping_legacy(context: PrefixedContext):
    print(f"\033[1;33m!ping\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")
    await context.reply(f"Ping: {round(context.bot.latency * 1000, 2)} ms")

@prefixed_command(name="playerlist")
async def playerlist_legacy(context: PrefixedContext):
    print(f"\033[1;33m!playerlist\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")

    with open(config_path, "r") as config_file:
        configs = json.load(config_file)

    domain = configs["domain"]
    port = configs["port"]

    try:
        mcserver = mcstatus.JavaServer(
            host = domain,
            port = port,
        )

        try:
            output = ", ".join([player.name for player in mcserver.status().players.sample])
        except TypeError:
            output = "No players are online."

        await context.reply(output)

    except:
        print("\033[1;33m/playerlist\033[0;0m: Prior call \033[1;31mtimed out\033[0;0m")
        await context.reply("Connection timed out, likely due to an invalid server domain and/or port configuration")

@prefixed_command(name="mcserver_config")
async def mcserver_config_legacy(context: PrefixedContext, config_name: typing.Optional[str], config_value = None):
    print(f"\033[1;33m!mcserver_config\033[0;0m: Called by \033[0;32m{context.author.username}\033[0;0m")

    if config_name == None:
        print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration name\033[0;0m")
        await context.reply("You must provide a configuration")

    elif config_value == None:
        print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mmissing configuration value\033[0;0m")
        await context.reply("You must provide a value to set the configuration to")

    else:
        operator_role = context.guild.get_role(1167687375913234464) # hard coded role ID because I'm lazy, shut up

        valid_configs = ["domain", "port"]

        if context.author.has_role(operator_role):
            with open(config_path, "r") as config_file:
                configs = json.load(config_file)

            if config_name in valid_configs:
                error = False
                if config_name == "domain":
                    try: ipaddress.ip_address(config_value)
                    except ValueError:
                        print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid domain ({config_value})\033[0;0m")
                        await context.reply("Port must be a valid domain")
                        error = True

                elif config_name == "port":
                    try: config_value = int(config_value)

                    except ValueError:
                        print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained a \033[1;31mnon-integer port ({config_value})\033[0;0m")
                        await context.reply("Port must be an integer")
                        error = True

                    else:
                        if config_value < 0 or config_value > 65535: # min and max port value
                            print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid port ({config_value})\033[0;0m")
                            await context.reply("Port must be greater than 0 and less than 65535")
                            error = True

                if not error:
                    configs[config_name] = config_value

                    with open(config_path, "w") as config_file:
                        json.dump(configs, config_file, indent=4)

                    print(f"\033[1;33m/mcserver_config\033[0;0m: Prior call changed \033[0;32m{config_name.capitalize()}\033[0;0m to \033[0;32m{config_value}\033[0;0m")
                    await context.reply(f"Updated '{config_name.capitalize()}' to be '{config_value}'")

        else:
            print("\033[1;33m/mcserver_config\033[0;0m: Prior call \033[1;31mnot permitted\033[0;0m")
            await context.reply("You do not have permission to use that command.")

client.start()