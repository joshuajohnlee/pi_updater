from paramiko import SSHClient
import requests
import re

# try:
import credentials
# except:
#     print("Credentials were not found, please provide the following to set up this script")
#     new_host = input("Please provide the IP address of the target device (e.g. 192.168.0.1): ")
#     new_user = input("Please provide a username: ")
#     new_password = input("Please provide a password: ")

speedtest_flag = None

while speedtest_flag != "y" and speedtest_flag != "n":
    if speedtest_flag != None:
        print("Input not recognised")
    speedtest_flag = input("Run a speed test during this script? Y/N: ").lower()
    if speedtest_flag == "y":
        print("Will run a speed test")
    elif speedtest_flag == "n":
        print("Will not run a speed test")

print("Script running, will attempt to create SSH session")

client = SSHClient()
client.load_system_host_keys()
try:
    client.connect(credentials.host, username=credentials.ssh_username, password=credentials.ssh_password)
    print("SSH connection succesful")
except:
    print("A connection could not be established. Please ensure the target device is connected to the network, and that the credentials and IP address in the credentials.py file are correct.")
    input("Press enter to close")
    quit()

# Run speed test

if speedtest_flag == "y":
    print("Running speed test")    
    stdin, stdout, stderr = client.exec_command('speedtest-cli')
    exit_code = stdout.channel.recv_exit_status() # Blocks until command completion

    if exit_code == 0:
        output = (stdout.read().decode('utf8'))
        download_speed = re.search("Download: (\d+(\.\d+)?) Mbit\/s", output)
        upload_speed = re.search("Upload: (\d+(\.\d+)?) Mbit\/s", output)
        print(f"{download_speed.group()}")
        print(f"{upload_speed.group()}")
    else:
        print(f"Speed test failed")

# Show uptime
    
stdin, stdout, stderr = client.exec_command('uptime -p')
exit_code = stdout.channel.recv_exit_status() # Blocks until command completion

if exit_code == 0:
    print(f"Uptime: {stdout.read().decode('utf8')}")
else:
    print(f"Couldn't read uptime, an error occured with exit code {exit_code}, see below:")
    print(f"STDOUT: {stdout.read().decode('utf8')}")
    print(f'STDERR: {stderr.read().decode("utf8")}')

# Update packages

print("Attempting to update packages")
# Some form of progress bar, indicator script is still running?
stdin, stdout, stderr = client.exec_command('sudo apt-get update && sudo apt-get upgrade -y --autoremove')
exit_code = stdout.channel.recv_exit_status() # Blocks until command completion

none_updated = re.search("0 upgraded", stdout.read().decode("utf8"))

if exit_code == 0 and none_updated != None:
    print("Package lists were updated. There was nothing to upgrade.")
elif exit_code == 0:
    # print(f"STDOUT: {stdout.read().decode('utf8')}")  # This STDOUT is blank?
    print("Updates were succesful")
    # Need regex to extract the number and possibly name of the packages.
else:
    print(f"Error occured with exit code {exit_code}, see below:")
    print(f"STDOUT: {stdout.read().decode('utf8')}")
    print(f'STDERR: {stderr.read().decode("utf8")}')

# Close SSH files when done
stdin.close()
stdout.close()
stderr.close()
client.close()

# Check plex web interface is up

plexServer = requests.get(f"http://{credentials.host}:32400/web/index.html#!/")

if plexServer.status_code != 200:
    print(f"Plex server web interface was not reachable, returned code {plexServer.status_code}")
else:
    print("Plex server web interface is up.")