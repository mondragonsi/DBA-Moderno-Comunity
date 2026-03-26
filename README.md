# 🛑 SQL Server Block Simulator & Monitor

Um projeto de código aberto voltado para a **Comunidade de DBAs Modernos**, projetado para simular cenários complexos de bloqueios de banco de dados (locks) e diagnosticá-los em tempo real utilizando visões de gerenciamento dinâmico (**DMVs**) nativas e Python.

## 🌟 O que a aplicação faz?

Criado com **Streamlit** e **PyODBC**, o aplicativo possui duas frentes atuando em uníssono:
1. **Simulador de Blocks (Assíncrono):** Dispara transações perigosas (`WAITFOR DELAY`, `X-Locks`) em tabelas críticas simulando gargalos de produção. Rodando em background via threads Python, a interface permanece totalmente responsiva aos seus cliques.
2. **Monitoramento via DMVs (Sem overhead):** Em vez de depender de chamadas externas complexas ao PowerShell (como o `Get-DbaProcess` do `dbatools`), a aplicação evoluiu para usar consultas **T-SQL puras diretamente nas DMVs**. Extrai e processa a cadeia de bloqueio (Blocking Chain) inteira quase instantaneamente na tela, facilitando a vida do DBA na hora do incidente.

## ⚙️ Funcionalidades Inclusas
- 🌳 **Árvore de Dependência Visual:** Saiba instantaneamente quem é o *SPID raiz (bloqueador)* e quem são as *Vítimas (bloqueados)*.
- ⏱️ **Monitoramento de Transações Abertas:** Extraia status, horários de início e duração explícita de execuções pendentes.
- 📜 **Captura de Comandos Nativos:** Acesso transparente às exatas queries SQL que estão causando o desastre via `sys.dm_exec_sql_text`.
- ⚡ **Alta Performance:** Uso otimizado da trindade de DMVs DBA: `sys.dm_exec_requests`, `sys.dm_exec_sessions` e `sys.dm_tran_active_transactions`.

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.9+
- Microsoft ODBC Driver for SQL Server
- Uma instância SQL Server ativa (O app aponta nativamente para uma string SQL Server, mas pode ser configurado em `app.py`).

### Script de Instalação e Execução
```bash
# Clone este repositório
git clone https://github.com/mondragonsi/DBA-Moderno-Comunity.git
cd DBA-Moderno-Comunity

# Crie um ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows PowerShell

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação Streamlit
streamlit run app.py
```

## 📚 Documentação Adicional
Consulte o arquivo `documentacao.html` incluído no repositório para uma explicação detalhada da arquitetura, do fluxo de performance, do abandono do dbatools para adoção do T-SQL puro, e screenshots de uso.

## 💡 Contribuições
Sinta-se à vontade para enviar _Pull Requests_ com melhorias nas queries de proteção das DMVs, otimizações na interface interativa com o Pandas ou suporte a novos cenários no Banco AdventureWorks2022!

---
_Construindo um futuro mais ágil e analítico para Desenvolvedores e Administradores de Banco de Dados._
