import os

CUR_DIR = os.path.dirname(__file__)

print("------------------------")
cmd = "git pull"
print(cmd)
os.system(cmd)

print("------------------------")
cmd = "docker stop discord_bot"
print(cmd)
os.system(cmd)

print("------------------------")
cmd = "docker rm discord_bot"
print(cmd)
os.system(cmd)

print("------------------------")
cmd = "docker image rm discord_bot"
print(cmd)
os.system(cmd)

print("------------------------")
cmd = "docker build -t discord_bot ."
print(cmd)
os.system(cmd)

ENV_FILE = os.path.join(CUR_DIR, '.env')
if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'w') as file:
        pass

CONFIG_FILE = os.path.join(CUR_DIR, 'config.json') 
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as file:
        file.write('{}')

LOG_DIR = os.path.join(CUR_DIR, 'logs') 
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

print("------------------------")
cmd = "docker run --name discord_bot " \
    + f"--mount type=bind,source={CUR_DIR}/logs,target=/app/logs " \
    + f"--mount type=bind,source={CUR_DIR}/.env,target=/app/.env " \
    + f"--mount type=bind,source={CUR_DIR}/config.json,target=/app/config.json " \
    + f"--mount type=bind,source={CUR_DIR}/dictionary.py,target=/app/dictionary.py " \
    + "--restart=always " \
    + "-d " \
    + "discord_bot:latest" 

print(cmd)
os.system(cmd)