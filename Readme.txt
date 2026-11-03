Start the Virtual Enviroment
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
PS C:\LocalAI\Agents> .\.venv\Scripts\Activate.ps1


Run the ai server
.\llama-server.exe -m "C:\LocalAI\Models\qwen2.5-coder-7b-instruct-q4_k_m.gguf" -c 4096 -ngl 99 --host 127.0.0.1 --port 8080

Server link
http://127.0.0.1:8080/