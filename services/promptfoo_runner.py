import subprocess
import threading

def run_promptfoo_live(cmd, on_update):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_lines = []
    def reader():
        for line in process.stdout:
            log_lines.append(line)
            on_update(''.join(log_lines))
        process.stdout.close()
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    process.wait()
    return ''.join(log_lines), process.returncode
