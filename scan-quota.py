import os


HOMEDIR = os.path.expanduser('~')
SAVEDIR = HOMEDIR + "/.quota-scanner/"
SCANFILE = SAVEDIR + "scan.dat"
FILTERDIR = SAVEDIR + "filter/"


def humanReadable(size):
    if size > 1_000_000_000:
        return f"{size/1024**3:.2f}Go"
    if size > 1_000_000:
        return f"{size/1024**2:.2f}Mo"
    if size > 1_000:
        return f"{size/1024:.2f}Ko"
    return f"{size}o"

def incorectUsageMsg(command):
    print(f"Incorect usage: {COMMANDS_REG[command]["usage"]}")



def scan(*args):
    explored = 0
    folders = {}
    for root, _, files in os.walk(HOMEDIR):
        for filename in files:
            file = os.path.join(root, filename)
            if os.path.isfile(file):
                path = ""
                for folder in file.split("/")[4:-1]:
                    folders[path + folder] = folders.get(path + folder, 0) + os.path.getsize(file)
                    path += folder + "/"
            explored += 1
            if not explored & 0b0001_1111_1111:
                print(f" {explored} files scanned\r", end='')

    print("\n\n--- 10 biggest folders ---")

    flist = list(folders.items())
    flist = sorted(flist, key=lambda x: x[1])[::-1]
    stdo = ""
    for folder, size in flist[:10]:
        stdo += f"\033[94m{folder}\033[0m {humanReadable(size)}\n"
    print(stdo)


    fout = []
    for fo, si in flist:
        fout.append(fo)
        fout.append(" ")
        fout.append(str(si))
        fout.append("\n")

    with open(SCANFILE, "w") as f:
        f.write("".join(fout))


def topSearch(*args):
    if not args:
        incorectUsageMsg("top")
        return
    try:
        amount = int(args[0])
    except:
        print("Incorect usage: top <amount>; <amount> must be a number")
        return
    if not os.path.exists(SCANFILE):
        print("No scan found; Use the 'scan' command first.")
        return
    with open(SCANFILE, "r") as file:
        lines = []
        for i in range(amount):
            line = file.readline()
            if not line:
                continue
            line = line.split()
            folder = "".join(line[:-1])
            size = int(line[-1])
            lines.append((folder, size))
    
    print(f"\n--- {amount} biggest folders ---")
    stdo = ""
    for folder, size in lines:
        stdo += f"\033[94m{folder}\033[0m {humanReadable(size)}\n"
    print(stdo)


def strSearch(*args):
    if not args:
        incorectUsageMsg("search")
        return
    if not os.path.exists(SCANFILE):
        print("No scan found; Use the 'scan' command first.")
        return
    string = args[0]
    with open(SCANFILE, "r") as file:
        lines = []
        for line in file:
            if not line:
                continue
            line = line.split()
            folder = "".join(line[:-1])
            if string in folder:
                size = int(line[-1])
                lines.append((folder, size))

    print(f"\n--- Folders containing {string} ---")
    index = 0
    while index < len(lines):
        stdo = ""
        for folder, size in lines[index:index+50]:
            start = folder.find(string)
            end = start + len(string)
            stdo += f"\033[94m{folder[:start]}\033[91m{folder[start:end]}\033[94m{folder[end:]}\033[0m {humanReadable(size)}\n"
        print(stdo)

        index += 50
        if index >= len(lines):
            print(f"{len(lines)}/{len(lines)} matches")
            break

        print(f"{index}/{len(lines)} matches")
        userInput = input("Press 'ENTER' to continue\nOr 'q' to exit\n")
        if userInput.lower() == 'q':
            return


def filter(*args):
    if not args:
        incorectUsageMsg("filter")
        return

    filterHeader = """# Filters can be used to make a selection of folders
# that can be used for visualization or deletion
#
# If your filter doesn't work, you can debug it using 'filter debug %n' (feature not implemented yet)
#
# In order to configure this filter
# you can write a script using the folowing commands:
#
#
"""

    match args[0]:
        case "create":
            if not args[1]:
                print("Incorect usage: filter create <name>")
                return
            with open(FILTERDIR + args[1], "w") as file:
                file.write(filterHeader % args[1])
            print(f"Created filter {args[1]}\n'filter edit {args[1]}' to edit")
        case "list":
            if os.path.exists(FILTERDIR):
                filters = []
                for elem in os.listdir(FILTERDIR):
                    if os.path.isfile():
                        filters.append(elem)
                print("\n".join(filters))
            else:
                print("No filters found")
        case "edit":
            if os.path.exists(FILTERDIR):
                if not args[1]:
                    print("Incorect usage: filter edit <name>")
                    return
                if not os.path.exists(FILTERDIR + args[1]):
                    print(f"This filter does not exists. You can create it using 'filter create {args[1]}'")
                    return
                os.system(f"nano {FILTERDIR + args[1]}")
            else:
                print("No filters found")
        case "delete":
            if not args[1]:
                print("Incorect usage: filter delete <name>")
                return
            if not os.path.exists(FILTERDIR + args[1]):
                print(f"This filter does not exists.")
                return
            os.remove(FILTERDIR + args[1])
        case "explorer":
            if not os.path.exists(FILTERDIR):
                if not os.path.exists(SAVEDIR):
                    os.mkdir(SAVEDIR)
                os.mkdir(FILTERDIR)
            os.system("exo-open --launch FileManager " + FILTERDIR)
        case "debug":
            if not args[1]:
                print("Incorect usage: filter debug <name>")
                return
            if not os.path.exists(FILTERDIR + args[1]):
                print(f"This filter does not exists.")
                return
            #TODO
            print("Feature not implemented yet.")
        case _ as option:
            print(f"Unknown option '{option}'")



def quitApp(*args):
    global appRunning
    appRunning = False

def displayHelp(*args):
    b, r = '\033[1m', '\033[0m'
    if args and args[0] in COMMANDS_REG:
        cmd = COMMANDS_REG[args[0]]
        menu = f"\n{b}Command{r}: {cmd["name"]}\
            \n{b}Usage{r}: {cmd["usage"]}\
            \n{b}Aliases{r}: {" | ".join(cmd["aliases"])}\
            \n{b}Description{r}: {cmd["description"]}\
            \n{b}Details{r}:\n{cmd["help"]}\n"

    else:
        menu = "--- All commands ---\n"
        for command in COMMANDS:
            menu += f"    {command["usage"]:<20}"
            if len(command["usage"]) > 20:
                menu += f"\n    {"":<20}"
            menu += " - "
            if command["aliases"]:
                menu += f"({"|".join(command["aliases"])}) "
            menu += f"{command["description"]}\n"
    print(menu)








COMMANDS = [
    #? "run" key will later be used to directly call the command's code
    {
        "name": "help",
        "usage": "help [<command>]",
        "aliases": ["h", "hp"],
        "description": "display the help menu",
        "run": displayHelp,
        "help": "This command gives extended informations abount a given command or lists all existing commands if no argument is given."
            "\nex:\n'help scan' gives details about the 'scan' command."
            "\n'help' gives a list of all existing commands."
            "\n\nBut if you read this you already know that."
    },
    {
        "name": "scan",
        "usage": "scan",
        "aliases": ["sc"],
        "description": "deep scan your home directory",
        "run": scan,
        "help": "This command run a deep scan of your home directory."
            "\nThis mean all the folders in your home directory will be analysed and then strored with their size for later use."
            "\nRunning the 'scan' command is required befor using data processing commands such as 'search' or 'top'."
            "\nIf the 'scan' command is not run befor using data processing commands, then said command will not be able to run."
    },
    {
        "name": "top",
        "usage": "top <amount>",
        "aliases": ["tp"],
        "description": "show the <amount> biggest folders",
        "run": topSearch,
        "help": "This command will display a given number of the biggest folders registered by the latest scan."
            "nex:\n'top 10' displays the 10 folders with the highest size."
            "n'top 35' displays the 35 folders with the highest size."
    },
    {
        "name": "search",
        "usage": "search <word>",
        "aliases": ["sr"],
        "description": "show all the folders containing <word> in their path",
        "run": strSearch,
        "help": "This command will give you back all the folders containing a given word in their path among all the saved folders from the latest scan."
            "\nex:\n'search .vscode' will give you all the sub-folders of the .vscode folder."
    },
    {
        "name": "filter",
        "usage": "filter <option> [<name>]",
        "aliases": ["ft"],
        "description": f"manage filters; type 'help filter' for more informations",
        "run": filter,
        "help": "This command is used to create and manage filters."
            "\nFilters can be used to order or delete certain folders."
            "\nAvalaible options are:"
            f"\n{"create":<10} - Create a new filter with a given name. ex: 'filter create COOLFILTER'"
            f"\n{"list":<10} - List all existing filters."
            f"\n{"edit":<10} - Edit a given filter. ex: 'filter edit COOLFILTER'"
            f"\n{"delete":<10} - Delete a given filter. ex: 'filter delete COOLFILTER'"
            f"\n{"explorer":<10} - Open the filters folder in the file explorer."
            f"\n{"debug":<10} - Debug a given filter. ex: 'filter debug COOLFILTER'"
    },
    {
        "name": "quit",
        "usage": "quit",
        "aliases": ["q", "exit"],
        "description": "quit the app",
        "run": quitApp,
        "help": "Do exactly what is advertised: Close the application."
    }
]

def buildCommands():
    global COMMANDS_LIB
    global COMMANDS_REG
    COMMANDS_LIB = {}
    COMMANDS_REG = {}
    for cmd in COMMANDS:
        COMMANDS_LIB[cmd["name"]] = cmd["run"]
        COMMANDS_REG[cmd["name"]] = cmd
        for als in cmd["aliases"]:
            COMMANDS_LIB[als] = cmd["run"]


#* Menu
if __name__ == "__main__":
    buildCommands()
    if not os.path.exists(SAVEDIR):
        os.mkdir(SAVEDIR)
    if not os.path.exists(FILTERDIR):
        os.mkdir(FILTERDIR)

    appRunning = True
    displayHelp()
    while appRunning:
        userInput = input("\033[95m~>\033[0m ")
        userInput = userInput.strip().split()
        if not userInput:
            continue
        command, args = userInput[0], userInput[1:]
        COMMANDS_LIB.get(command, lambda *args: print(f"Unknown command '{command}'"))(*args)
