# 🏛️ Comunidade DBA Moderno - Projetos & Aulas

Este é o repositório central da **Comunidade DBA Moderno**, projetado para armazenar uma coleção crescente de projetos e scripts focados em banco de dados, governança, performance e administração moderna (especialmente para cenários de SQL Server).

---

## 📁 Estrutura do Repositório (Múltiplos Projetos)

O repositório foi reestruturado de forma a acomodar diversos projetos focados em cenários reais e aulas práticas. Cada pasta representa uma unidade isolada — ou seja, uma aplicação ou classe em particular —, que deve ser explorada de maneira autônoma com seus próprios scripts (`app.py`, `T-SQL`, `dbatools`, pacotes de `requirements.txt`).

### Projetos e Aulas Disponíveis:

| Pasta / Aula | Resumo | Tecnologias |
|---------|-----------|-----------|
| 🛑 **[01-SQL-Server-Block-Simulator](./01-SQL-Server-Block-Simulator/)** | **Simulador de Locks:** Ferramenta GUI que recria cenários de *deadlocks* e *blocking chains*, acessando as **DMVs** nativas em tempo real para ajudar a investigar as vítimas e os ofensores através do painel. | `Python`, `Streamlit`, `T-SQL`, `PyODBC` |

*(Mais projetos e pastas serão adicionados recorrentemente! Fique ligado!)*

---

## 🛠️ Como Navegar
1. **Escolha o Projeto:** Selecione a pasta com a aula ou projeto que você quer estudar/executar.
2. **Leia a Documentação Específica:** Cada diretório interno terá seu **próprio** `README.md` ou `documentacao.html` com o passo-a-passo detalhado referente àquele tópico.
3. **Ambiente Isolado (Recomendado):** Para projetos envolventes como o Simulador de Streamlit, entre na pasta correspondente pelo terminal e utilize um Ambiente Virtual Python (`venv`) antes de rodar os pip installs.

---
_Acompanhe e contribua para a construção de um ambiente de dados de excelência para a nossa comunidade._
