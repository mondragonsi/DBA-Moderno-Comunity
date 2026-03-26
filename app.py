import streamlit as st
import pyodbc
import time
import subprocess
import json
import pandas as pd
import threading

# Configuração da página Streamlit
st.set_page_config(
    page_title="SQL Server Block Simulator & Monitor",
    page_icon="🛑",
    layout="wide"
)

# Configurações de Conexão com o SQL Server
SERVER = r'localhost\DEV2022' 
INSTANCE_NAME = r'MONDRAGONACER\DEV2022'
DATABASE = 'AdventureWorks2022'
USERNAME = 'sa'
PASSWORD = 'Antigravity2026'

def get_odbc_driver():
    """Tenta encontrar um driver ODBC instalado para o SQL Server."""
    drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
    if not drivers:
        return 'SQL Server'
    
    preferred = [
        'ODBC Driver 18 for SQL Server', 
        'ODBC Driver 17 for SQL Server', 
        'ODBC Driver 13 for SQL Server', 
        'SQL Server Native Client 11.0'
    ]
    for p in preferred:
        if p in drivers:
            return p
    return drivers[0]

def simulate_block(duration_seconds):
    """Executa a transação de lock de forma não bloqueante para a thread do Streamlit."""
    driver = get_odbc_driver()
    trust_cert = ";TrustServerCertificate=yes" if "18" in driver else ""
    conn_str = f'DRIVER={{{driver}}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}{trust_cert}'
    
    try:
        conn = pyodbc.connect(conn_str, autocommit=False)
        cursor = conn.cursor()
        
        cursor.execute("BEGIN TRAN;")
        query_update = "UPDATE Person.Person SET ModifiedDate = GETDATE() WHERE BusinessEntityID = 1;"
        cursor.execute(query_update)
        
        wait_time_str = time.strftime('%H:%M:%S', time.gmtime(duration_seconds))
        query_waitfor = f"WAITFOR DELAY '{wait_time_str}';"
        cursor.execute(query_waitfor)
        
        cursor.execute("ROLLBACK TRAN;")
        conn.close()
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        print(f"Erro no background: {e}")

# --- Interface ---
st.title("Simulador e Monitor de Blocks do SQL Server 🛑")

tab1, tab2 = st.tabs(["🚦 Simulador de Blocks", "📊 Monitoramento com dbatools"])

with tab1:
    st.markdown("Gere um bloqueio longo na tabela `Person.Person`. **(Roda em background para que você possa ir para a aba de Monitoramento!)**")
    
    duration = st.slider("Tempo do Bloqueio (em segundos)", min_value=10, max_value=120, value=60, step=10)
    
    if st.button("Gerar Block no Background", type="primary", use_container_width=True):
        # Disparamos numa thread para não travar a UI de monitoramento
        threading.Thread(target=simulate_block, args=(duration,), daemon=True).start()
        st.success(f"⏳ Processo de bloqueio disparado no background por {duration} segundos! Vá rápido para a aba **Monitoramento com dbatools**.")

with tab2:
    st.markdown("### Relatório de Bloqueios e Transações")
    st.info(f"Instância: `{INSTANCE_NAME}` | Banco: `{DATABASE}`")
    
    if st.button("🔄 Atualizar Relatório", type="primary"):
        with st.spinner("Consultando o SQL Server..."):
            driver = get_odbc_driver()
            trust_cert = ";TrustServerCertificate=yes" if "18" in driver else ""
            conn_str = f'DRIVER={{{driver}}};SERVER={SERVER};DATABASE=master;UID={USERNAME};PWD={PASSWORD}{trust_cert}'
            
            try:
                conn = pyodbc.connect(conn_str, autocommit=True)
                cursor = conn.cursor()
                
                # ============================================================
                # 1) BLOCKING CHAIN - Query direta nas DMVs (sem lixo!)
                # ============================================================
                blocking_query = """
                SELECT
                    blocked.session_id       AS blocked_spid,
                    blocked.blocking_session_id AS blocker_spid,
                    DB_NAME(blocked.database_id) AS blocked_database,
                    blocked.status           AS blocked_status,
                    blocked.command          AS blocked_command,
                    blocked.wait_type        AS blocked_wait_type,
                    blocked.wait_resource    AS blocked_wait_resource,
                    blocked.wait_time / 1000 AS blocked_wait_seconds,
                    s_blocked.login_name     AS blocked_login,
                    s_blocked.host_name      AS blocked_host,
                    COALESCE(
                        (SELECT SUBSTRING(st.text, (blocked.statement_start_offset/2)+1,
                            ((CASE blocked.statement_end_offset WHEN -1 THEN DATALENGTH(st.text) ELSE blocked.statement_end_offset END 
                              - blocked.statement_start_offset)/2)+1)
                         FROM sys.dm_exec_sql_text(blocked.sql_handle) st), '') AS blocked_sql,
                    s_blocker.login_name     AS blocker_login,
                    s_blocker.host_name      AS blocker_host,
                    DB_NAME(r_blocker.database_id) AS blocker_database,
                    r_blocker.command        AS blocker_command,
                    r_blocker.status         AS blocker_status,
                    COALESCE(
                        (SELECT SUBSTRING(st2.text, 
                            CASE WHEN r_blocker.statement_start_offset IS NULL THEN 1 ELSE (r_blocker.statement_start_offset/2)+1 END,
                            CASE WHEN r_blocker.statement_end_offset IS NULL OR r_blocker.statement_end_offset = -1 THEN DATALENGTH(st2.text) ELSE
                            ((r_blocker.statement_end_offset - COALESCE(r_blocker.statement_start_offset,0))/2)+1 END)
                         FROM sys.dm_exec_sql_text(r_blocker.sql_handle) st2), 'N/A (idle session)') AS blocker_sql
                FROM sys.dm_exec_requests blocked
                INNER JOIN sys.dm_exec_sessions s_blocked ON blocked.session_id = s_blocked.session_id
                LEFT JOIN sys.dm_exec_sessions s_blocker ON blocked.blocking_session_id = s_blocker.session_id
                LEFT JOIN sys.dm_exec_requests r_blocker ON blocked.blocking_session_id = r_blocker.session_id
                WHERE blocked.blocking_session_id > 0
                """
                
                cursor.execute(blocking_query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                st.subheader("🔥 Blocking Chain (Cadeia de Bloqueio)")
                
                if rows:
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    # Resumo
                    blocker_spids = set(r['blocker_spid'] for r in data)
                    blocked_spids = set(r['blocked_spid'] for r in data)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🛑 Bloqueadores", len(blocker_spids))
                    with col2:
                        st.metric("⚠️ Vítimas", len(blocked_spids))
                    with col3:
                        max_wait = max(r['blocked_wait_seconds'] for r in data)
                        st.metric("⏱️ Maior Espera", f"{max_wait}s")
                    
                    # Árvore visual por bloqueador
                    st.markdown("#### Árvore de Dependência")
                    for bspid in sorted(blocker_spids):
                        first_row = next(r for r in data if r['blocker_spid'] == bspid)
                        st.markdown(
                            f"🔴 **BLOQUEADOR SPID {bspid}** — "
                            f"`{first_row['blocker_login']}` @ `{first_row.get('blocker_database') or 'N/A'}` — "
                            f"SQL: `{(first_row['blocker_sql'] or 'N/A')[:80]}`"
                        )
                        victims = [r for r in data if r['blocker_spid'] == bspid]
                        for v in victims:
                            st.markdown(
                                f"&nbsp;&nbsp;&nbsp;&nbsp;↳ ⚠️ **SPID {v['blocked_spid']}** bloqueado há "
                                f"**{v['blocked_wait_seconds']}s** — Wait: `{v['blocked_wait_type']}` — "
                                f"SQL: `{(v['blocked_sql'] or 'N/A')[:80]}`"
                            )
                    
                    st.markdown("#### Detalhes Completos")
                    df_blocks = pd.DataFrame(data)
                    st.dataframe(df_blocks, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ Nenhum bloqueio ativo no momento. O banco está operando normalmente.")
                
                # ============================================================
                # 2) OPEN TRANSACTIONS via T-SQL (DMVs diretas)
                # ============================================================
                st.markdown("---")
                st.subheader("📂 Transações Abertas")
                
                open_tx_query = """
                SELECT
                    st.session_id AS SPID,
                    at.name AS TransactionName,
                    DB_NAME(dt.database_id) AS [Database],
                    at.transaction_begin_time AS BeginTime,
                    DATEDIFF(SECOND, at.transaction_begin_time, GETDATE()) AS DurationSeconds,
                    CASE at.transaction_state
                        WHEN 0 THEN 'Inicializando'
                        WHEN 1 THEN 'Inicializada'
                        WHEN 2 THEN 'Ativa'
                        WHEN 3 THEN 'Finalizada (somente leitura)'
                        WHEN 4 THEN 'Commit iniciado'
                        WHEN 5 THEN 'Preparada'
                        WHEN 6 THEN 'Committed'
                        WHEN 7 THEN 'Rolling back'
                        WHEN 8 THEN 'Rolled back'
                        ELSE CAST(at.transaction_state AS VARCHAR)
                    END AS Estado,
                    s.login_name AS Login,
                    s.host_name AS Host
                FROM sys.dm_tran_active_transactions at
                INNER JOIN sys.dm_tran_session_transactions st ON at.transaction_id = st.transaction_id
                INNER JOIN sys.dm_exec_sessions s ON st.session_id = s.session_id
                LEFT JOIN sys.dm_tran_database_transactions dt ON at.transaction_id = dt.transaction_id
                WHERE DB_NAME(dt.database_id) NOT IN ('master', 'tempdb', 'msdb', 'model')
                  AND at.transaction_type != 4
                ORDER BY at.transaction_begin_time ASC
                """
                
                cursor.execute(open_tx_query)
                tx_columns = [desc[0] for desc in cursor.description]
                tx_rows = cursor.fetchall()
                
                if tx_rows:
                    tx_data = [dict(zip(tx_columns, row)) for row in tx_rows]
                    df_tx = pd.DataFrame(tx_data)
                    st.dataframe(df_tx, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma transação aberta em bancos de usuário.")
                
                conn.close()
                
            except Exception as e:
                st.error(f"Erro de conexão com o SQL Server: {e}")

st.markdown("---")
st.markdown("""
**Teste do Bloqueador e Monitor (Passo a Passo):**
1. Vá na aba `Simulador de Blocks` e clique em **Gerar Block no Background**.
2. Abra seu SSMS e tente atualizar a tabela: `UPDATE AdventureWorks2022.Person.Person SET Title = 'Mr.' WHERE BusinessEntityID = 1` (Esta query ficará pendurada/bloqueada).
3. Volte aqui, vá para a aba `Monitoramento com dbatools` e clique em `Atualizar Relatório`. 
Você verá a transação principal aberta e o SPID da sua query no SSMS sendo alertado como Bloqueado!
""")
