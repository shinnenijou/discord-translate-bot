import os
import sys

def main():
    logs_dir = 'data/logs'
    if not os.path.exists(logs_dir) or not os.path.isdir(logs_dir):
        print(f"[Error]Directory {logs_dir} not Exists.")
        return

    log_files = os.listdir(logs_dir)
    total_token = 0

    targets = sys.argv
    for arg in sys.argv:
        if arg == '-a' or arg == '--all':
            targets = log_files
            break

    for arg in targets:
        if not arg.endswith('.log'):
            filename = arg + '.log'
        else:
            filename = arg

        if filename not in log_files:
            continue

        with open(os.path.join(logs_dir, filename)) as file:
            for line in file.readlines():
                index = line.find('token')
                if index == -1:
                    continue

                token = ''
                start_flag = False
                for c in line[index:]:
                    if c.isnumeric():
                        start_flag = True
                        token += c
                    elif start_flag:
                        break

                if token and token.isnumeric():
                    total_token += int(token)

    print('[Successful]Total token: ', total_token)


if __name__ == '__main__':
    main()
