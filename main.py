import os
import sys
import json

from colorama import Fore, init
from discord.ext.commands import AutoShardedBot

from commands import Commands
from listeners import Listeners


init(convert=True)


class ProjectMonolithBot(AutoShardedBot):
    def __init__(self):
        super(ProjectMonolithBot, self).__init__(
            command_prefix=".",
            help_command=None
        )

        print(f"{Fore.YELLOW}Checking config...", end="\r")

        if os.path.exists("config.json"):
            self.config = json.loads(open("config.json", encoding="utf-8").read())
        else:
            print(f"{Fore.RED}Creating new config...")
            open("config.json", "w", encoding="utf-8").write(json.dumps({
                "token": ""
            }))
            sys.exit(0)

        self.add_cog(Commands(self))
        self.add_cog(Listeners(self))


if __name__ == "__main__":
    bot = ProjectMonolithBot()
    bot.run(bot.config["token"], reconnect=True)
