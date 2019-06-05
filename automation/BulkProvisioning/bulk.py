import os
import subprocess
import fire
import uuid

class BulkProvision(object):
    def __init__(self, number):
        self.IP_ADDRESSES = []
        self.NUMBER_OF_GROUPS = number
        if len(self.IP_ADDRESSES) < int(self.NUMBER_OF_GROUPS):
            print("Please add more IP addresses to continue!")
            sys.exit(1)

    def generate(self):
        for count in range(0, self.NUMBER_OF_GROUPS):
            group_name = "Group-" + str(uuid.uuid1())

            with open('template.yaml', 'r') as file:
                data = file.read().format(group_name, group_name, group_name)

            config_file_name = group_name + ".yaml"

            f = open(config_file_name, "w+")
            f.write(data)
            f.close()

            subprocess.run(["./automateCreation.sh", self.IP_ADDRESSES[count], config_file_name, "True", group_name])

    def exists(self):
        path = os.getcwd()
        CONFIG_FILES = [f for f in os.listdir(path) if f.endswith('.yaml')]
        count = 0
        for config_file in CONFIG_FILES:
            subprocess.run(["./automateCreation.sh", self.IP_ADDRESSES[count], config_file_name, "True", config_file_name.split(".", 1)[0]])
            count+=1

def main():
    fire.Fire(BulkProvision)

if __name__ == '__main__':
    print("Sample Usage: `python3 bulk.py --number 1 generate`")
    print("where `1` represents the number of groups to create")
    print()
    print("Using the keyword `generate` will")
    print("automatically generate .YAML config files")
    print()
    print("If you have already made these .YAML configuration files, ")
    print("you should use the following: `python3 bulk.py --number 1 exists`")
    print("This will use all of the .YAML files that are in the current directory")
    print()
    print("Make sure that you have updated the IP Addresses available to you")
    main()
