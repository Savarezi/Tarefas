import sqlite3
from datetime import datetime, timedelta

# Conectar ao banco de dados (cria se não existir)
conn = sqlite3.connect("organizacao.db")
cur = conn.cursor()

# Criar tabelas
cur.execute("""
CREATE TABLE IF NOT EXISTS Projetos (
    id_projeto INTEGER PRIMARY KEY,
    nome TEXT,
    descricao TEXT,
    prazo DATE,
    status TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Tarefas (
    id_tarefa INTEGER PRIMARY KEY,
    descricao TEXT,
    data_inicio DATE,
    data_vencimento DATE,
    status TEXT,
    prioridade TEXT,
    id_projeto INTEGER,
    FOREIGN KEY (id_projeto) REFERENCES Projetos(id_projeto)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS RegistroHorasTrabalhadas (
    id_registro INTEGER PRIMARY KEY,
    id_tarefa INTEGER,
    id_projeto INTEGER,
    data DATE,
    horas_trabalhadas REAL,
    FOREIGN KEY (id_tarefa) REFERENCES Tarefas(id_tarefa),
    FOREIGN KEY (id_projeto) REFERENCES Projetos(id_projeto)
)
""")

# Inserir dados fictícios
cur.execute("INSERT INTO Projetos (nome, descricao, prazo, status) VALUES ('Projeto 1', 'Descrição do Projeto 1', '2024-07-31', 'Em andamento')")
cur.execute("INSERT INTO Projetos (nome, descricao, prazo, status) VALUES ('Projeto 2', 'Descrição do Projeto 2', '2024-08-15', 'Em andamento')")

cur.execute("INSERT INTO Tarefas (descricao, data_inicio, data_vencimento, status, prioridade, id_projeto) VALUES ('Tarefa 1', '2024-07-10', '2024-07-20', 'Pendente', 'Alta', 1)")
cur.execute("INSERT INTO Tarefas (descricao, data_inicio, data_vencimento, status, prioridade, id_projeto) VALUES ('Tarefa 2', '2024-07-12', '2024-07-25', 'Pendente', 'Média', 2)")
cur.execute("INSERT INTO Tarefas (descricao, data_inicio, data_vencimento, status, prioridade, id_projeto) VALUES ('Tarefa 3', '2024-07-15', '2024-07-22', 'Pendente', 'Alta', 1)")

# Inserir registros de horas trabalhadas fictícias
cur.execute("INSERT INTO RegistroHorasTrabalhadas (id_tarefa, id_projeto, data, horas_trabalhadas) VALUES (1, 1, '2024-07-10', 2.5)")
cur.execute("INSERT INTO RegistroHorasTrabalhadas (id_tarefa, id_projeto, data, horas_trabalhadas) VALUES (1, 1, '2024-07-11', 3.0)")
cur.execute("INSERT INTO RegistroHorasTrabalhadas (id_tarefa, id_projeto, data, horas_trabalhadas) VALUES (2, 2, '2024-07-12', 1.5)")
cur.execute("INSERT INTO RegistroHorasTrabalhadas (id_tarefa, id_projeto, data, horas_trabalhadas) VALUES (3, 1, '2024-07-15', 4.0)")

# Commit para salvar as alterações
conn.commit()

# 1. UPDATE: Atualizar o status de um projeto
cur.execute("UPDATE Projetos SET status = 'Concluído' WHERE id_projeto = 1")

# 2. ALTER: Adicionar uma nova coluna à tabela Projetos
cur.execute("ALTER TABLE Projetos ADD COLUMN prioridade TEXT")

# 3. UPDATE: Atualizar a nova coluna com valores
cur.execute("UPDATE Projetos SET prioridade = 'Alta' WHERE id_projeto = 1")
cur.execute("UPDATE Projetos SET prioridade = 'Média' WHERE id_projeto = 2")

# 4. DROP: Remover a coluna 'prioridade' da tabela Projetos (SQLite não suporta DROP COLUMN diretamente, então faremos um workaround)
cur.execute("CREATE TABLE Projetos_temp AS SELECT id_projeto, nome, descricao, prazo, status FROM Projetos")
cur.execute("DROP TABLE Projetos")
cur.execute("ALTER TABLE Projetos_temp RENAME TO Projetos")

# Commit para salvar as alterações
conn.commit()

# Consultar dados atualizados dos projetos
cur.execute("SELECT * FROM Projetos")
projetos = cur.fetchall()
print("Dados atualizados dos Projetos:")
for projeto in projetos:
    print(projeto)

# Consultar distribuição de tempo entre as diferentes áreas de estudo e projetos
cur.execute("""
SELECT Projetos.nome AS projeto, SUM(RegistroHorasTrabalhadas.horas_trabalhadas) AS horas_totais
FROM RegistroHorasTrabalhadas
JOIN Projetos ON RegistroHorasTrabalhadas.id_projeto = Projetos.id_projeto
GROUP BY Projetos.nome
ORDER BY horas_totais DESC
""")

# Obter e imprimir os resultados
resultados = cur.fetchall()
print("\nDistribuição de tempo entre áreas de estudo e projetos:")
for row in resultados:
    print(f"Projeto: {row[0]}, Horas Totais: {row[1]}")

# Consultar tarefas e projetos prioritários para esta semana
data_atual = datetime.now().date()
data_seguinte = data_atual + timedelta(days=7)

cur.execute("""
SELECT Tarefas.descricao AS tarefa, Projetos.nome AS projeto, Tarefas.data_vencimento, Tarefas.prioridade
FROM Tarefas
JOIN Projetos ON Tarefas.id_projeto = Projetos.id_projeto
WHERE Tarefas.data_vencimento BETWEEN ? AND ?
ORDER BY Tarefas.prioridade DESC, Tarefas.data_vencimento ASC
""", (data_atual, data_seguinte))

# Obter e imprimir os resultados
resultados = cur.fetchall()
print("\nTarefas e projetos prioritários para esta semana:")
for row in resultados:
    print(f"Tarefa: {row[0]}, Projeto: {row[1]}, Data de Vencimento: {row[2]}, Prioridade: {row[3]}")

# Consultar progresso por tarefa
cur.execute("""
SELECT Tarefas.descricao AS tarefa, SUM(RegistroHorasTrabalhadas.horas_trabalhadas) AS horas_totais
FROM RegistroHorasTrabalhadas
JOIN Tarefas ON RegistroHorasTrabalhadas.id_tarefa = Tarefas.id_tarefa
GROUP BY Tarefas.descricao
ORDER BY horas_totais DESC
""")

# Obter e imprimir os resultados
resultados = cur.fetchall()
print("\nProgresso por tarefa:")
for row in resultados:
    print(f"Tarefa: {row[0]}, Horas Totais: {row[1]}")

# Fechar a conexão
conn.close()
