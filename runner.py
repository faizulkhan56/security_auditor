from services.garak_runner import run_garak_live

cmd = '--model_type ollama --model_name phi3 --probes dan.DAN_Jailbreak --generations 1 --report_prefix ollama.phi3.DAN_Jailbreak.20250801'

response_date = run_garak_live(cmd)
print(response_date)