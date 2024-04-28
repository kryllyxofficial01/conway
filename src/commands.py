import utils, mcstatus, ipaddress

def get_playerlist(is_slash_command = True) -> str:
    prefix = "/" if is_slash_command else "!"

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
        print(f"{utils.get_current_time()} | \033[1;33m{prefix}playerlist\033[0;0m: Prior call \033[1;31mtimed out\033[0;0m")
        return "Connection timed out, likely due to an invalid server domain and/or port configuration"

def change_mcserver_config(config_name: str, config_value: str, is_slash_command=True) -> str:
    prefix = "/" if is_slash_command else "!"

    configs = utils.load_config()

    error = False
    output = ""
    if config_name == "domain":
        try: ipaddress.ip_address(config_value)

        except ValueError:
            error = True

            print(f"{utils.get_current_time()} | \033[1;33m{prefix}mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid domain ({config_value})\033[0;0m")
            output = "Must be a valid domain"

    elif config_name == "port":
        try: config_value = int(config_value)

        except ValueError:
            error = True

            print(f"{utils.get_current_time()} | \033[1;33m{prefix}mcserver_config\033[0;0m: Prior call contained a \033[1;31mnon-integer port ({config_value})\033[0;0m")
            output = "Port must be an integer"

        else:
            if config_value < 0 or config_value > 65535: # max port value
                error = True

                print(f"{utils.get_current_time()} | \033[1;33m{prefix}mcserver_config\033[0;0m: Prior call contained an \033[1;31minvalid port ({config_value})\033[0;0m")
                output = "Port must be greater than 0 and less than 65535"

    if not error:
        configs[config_name] = config_value
        utils.refresh_config(configs)

        print(f"{utils.get_current_time()} | \033[1;33m{prefix}mcserver_config\033[0;0m: Prior call changed \033[0;32m{config_name.capitalize()}\033[0;0m to \033[0;32m{config_value}\033[0;0m")
        output = f"Updated '{config_name.capitalize()}' to be '{config_value}'"

    return output