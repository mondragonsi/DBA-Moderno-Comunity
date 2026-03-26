import subprocess
import json

INSTANCE_NAME = r'MONDRAGONACER\DEV2022'

ps_script = f"""
$ErrorActionPreference = "Stop"
Set-DbatoolsConfig -FullName sql.connection.trustcert -Value $true -ErrorAction SilentlyContinue | Out-Null

# Buscar processos bloqueados
$processes = Get-DbaProcess -SqlInstance '{INSTANCE_NAME}' | Where-Object BlockingSessionId -gt 0 | Select-Object SessionId, BlockingSessionId, Database, Login, Status, Command, WaitResource, WaitTime

# Buscar transações abertas
$openTxs = Get-DbaOpenTransaction -SqlInstance '{INSTANCE_NAME}' | Select-Object SessionId, Name, TransactionTime, TransactionState, Database

$result = @{{
    OpenTransactions = @($openTxs)
    Processes = @($processes)
}}

# Transforma as propriedades JSON
$result | ConvertTo-Json -Depth 3 -Compress
"""

process = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out_bytes, err_bytes = process.communicate(timeout=60)

out = out_bytes.decode('mbcs', errors='replace') if out_bytes else ""
err = err_bytes.decode('mbcs', errors='replace') if err_bytes else ""

print(f"RC: {process.returncode}")
print(f"OUT: {out}")
print(f"ERR: {err}")
