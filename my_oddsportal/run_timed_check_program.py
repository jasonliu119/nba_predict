import os
import time
import subprocess

GREP_FILE = 'grep.txt'

# check whether a program is running by looking at the "ps -aux | grep <some str>"
def check_is_running(grep_param, want_str):
    os.system("ps -aux | grep \"{}\" > {}".format(grep_param, GREP_FILE))
    content = ''
    with open(GREP_FILE) as f:
        content = f.read()
    print 'Got content from grep:\n' + content
    return (want_str in content)

def loop_and_check(cmd, grep_param, want_str):
    while True:
        subprocess.Popen(cmd, shell=True)
        print "Started: " + cmd
        time.sleep(10)

        while True:
            try:
                is_running = check_is_running(grep_param, want_str)
                if not is_running:
                    break
                else:
                    print "Found " + want_str + " from grep"
            except Exception as e:
                print "Exception in loop_and_check: " + e.message
                break

            time.sleep(3 * 60)

if __name__ == "__main__":
    cmd = 'sudo docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600'
    grep_param = 'docker run'
    want_str = 'sudo docker run -p'
    loop_and_check(cmd, grep_param, want_str) 