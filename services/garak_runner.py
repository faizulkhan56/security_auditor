from garak.cli import main
import subprocess
import threading

def run_garak_live(cmd, on_update):
    CMD = "--model_type ollama --model_name phi3 --probes dan.AntiDAN --report_prefix dan.AntiDAN"
    main(CMD.split(' '))