import utils, mcstatus, ipaddress, interactions

def get_playerlist(is_slash_command = True) -> str:
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

        return output

    except:
        print(utils.log_message("playerlist", "Prior call \033[1;31mtimed out\033[0;0m", is_slash_command))
        return "Connection timed out, likely due to an invalid server domain and/or port configuration"

def change_mcserver_config(config_name: str, config_value: str, is_slash_command = True) -> str:
    configs = utils.load_config()

    error = False
    output = ""
    if config_name == "domain":
        try: ipaddress.ip_address(config_value)

        except ValueError:
            error = True

            print(utils.log_message(
                "mcserver_config",
                f"Prior call contained an \033[1;31minvalid domain ('{config_value}')\033[0;0m",
                is_slash_command
            ))

            output = "Must be a valid domain"

    elif config_name == "port":
        try: config_value = int(config_value)

        except ValueError:
            error = True

            print(utils.log_message(
                "mcserver_config",
                f"Prior call contained a \033[1;31mnon-integer port ('{config_value}')\033[0;0m",
                is_slash_command
            ))

            output = "Port must be an integer"

        else:
            if config_value < 0 or config_value > 65535:
                error = True

                print(utils.log_message(
                    "mcserver_config",
                    f"Prior call contained an \033[1;31minvalid port ('{config_value}')\033[0;0m",
                    is_slash_command
                ))

                output = "Port must be greater than 0 and less than 65535"

    if not error:
        configs[config_name] = config_value
        utils.refresh_config(configs)

        print(utils.log_message(
            "mcserver_config",
            f"Prior call changed \033[0;32m'{config_name.capitalize()}'\033[0;0m to \033[0;32m'{config_value}'\033[0;0m",
            is_slash_command
        ))

        output = f"Updated '{config_name.capitalize()}' to be '{config_value}'"

    return output

def get_strikes(guild: interactions.Guild) -> str:
    strikes = utils.get_strikes()

    output = []
    for user_id in strikes:
        member = guild.get_member(int(user_id))
        strike_count = strikes[user_id]

        output.append(f"{member.username} ({member.display_name}): {strike_count}")

    return "\n".join(output)

def add_strikes(user_id: int, strikes: int, guild: interactions.Guild, is_slash_command = True) -> str:
    user_strikes = utils.get_strikes()

    new_strikes = user_strikes[str(user_id)] + strikes
    user_strikes[str(user_id)] = new_strikes

    utils.update_strikes(user_strikes)

    print(utils.log_message(
        "strikes add",
        f"Prior call gave \033[0;32m'{guild.get_member(user_id).username}'\033[0;0m \033[0;32m{strikes} strike{'s' if strikes != 1 else ''}\033[0;0m",
        is_slash_command
    ))

    return f"Gave '{guild.get_member(user_id).display_name}' {strikes} strike{'s' if abs(strikes) != 1 else ''}\nThey are now at {new_strikes} total"

def refresh_strikes(guild: interactions.Guild, is_slash_command = True) -> str:
    strikes = utils.get_strikes()

    strikes = dict.fromkeys(strikes, 0)

    print(utils.log_message("strikes clear", "Prior call \033[0;32mcleared all user strikes\033[0;0m", is_slash_command))

    members = guild.members

    for member in members:
        if not member.bot and not member.has_role(utils.ALT_ROLE_ID):
            if str(member.id) not in strikes.keys():
                strikes[str(member.id)] = 0

    to_be_removed = []
    for user_id in strikes.keys():
        if user_id not in [str(member.id) for member in members]:
            to_be_removed.append(user_id)

    for user_id in to_be_removed:
        strikes.pop(user_id)

    utils.update_strikes(strikes)

    return "All strikes cleared\nUser list refreshed"