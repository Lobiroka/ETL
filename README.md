# Projeto de Engenharia de Dados — Smart City Recife

Pipeline de Engenharia de Dados desenvolvido para coletar, armazenar, transformar e analisar dados públicos dos bairros do Recife utilizando dados do Censo Demográfico do IBGE.

O projeto demonstra um fluxo completo de ETL utilizando dois tipos de banco de dados:

- MongoDB Atlas — banco de dados NoSQL;
- NeonDB — banco de dados relacional PostgreSQL.

---

# Sobre o projeto

O projeto aplica conceitos de Engenharia de Dados em um cenário de Smart City.

São utilizados dados reais disponibilizados pelo IBGE através da API SIDRA, permitindo analisar informações relacionadas à população e ao saneamento dos bairros do Recife.

O pipeline segue obrigatoriamente o seguinte fluxo:

```text
API IBGE
    ↓
MongoDB Atlas (NoSQL)
    ↓
Recuperação dos dados brutos
    ↓
Transformação com Pandas
    ↓
NeonDB (PostgreSQL)
```

---

# Objetivo

Coletar dados públicos do IBGE referentes aos bairros do Recife, armazená-los inicialmente no MongoDB Atlas, recuperar esses dados para realizar a transformação e, posteriormente, armazenar os dados transformados no NeonDB.

O projeto demonstra na prática um processo de ETL utilizando banco NoSQL e banco relacional em nuvem.

---

# Dados utilizados

O projeto utiliza dados do Censo Demográfico  disponibilizados pela API SIDRA do IBGE.

São utilizados:

- População residente por bairro;
- Total de domicílios particulares permanentes;
- Domicílios ligados à rede geral de esgoto ou pluvial;
- Percentual de cobertura da rede geral de esgoto.

---

# Tecnologias utilizadas

- Python 3
- Requests
- Pandas
- PyMongo
- Psycopg
- python-dotenv
- MongoDB Atlas
- NeonDB
- PostgreSQL
- API SIDRA / IBGE

---

# Estrutura do projeto

```text
ETL-main/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── run_etl.py
│
├── exemplos/
├── jsons/
├── notebooks/
│
└── src/
    ├── __init__.py
    ├── extract.py
    ├── transform.py
    └── load.py
```

---

# Responsabilidade dos arquivos

## `src/extract.py`

Responsável pela extração dos dados da API do IBGE.

A classe `Extract` realiza:

- configuração das consultas da API;
- requisições HTTP;
- validação das respostas;
- extração da população;
- extração dos dados de saneamento;
- leitura dos dados armazenados no MongoDB Atlas.

A requisição à API utiliza `requests.get()` e valida a resposta através de `raise_for_status()`.

## `src/transform.py`

Responsável pela transformação dos dados utilizando Pandas.

A classe `Transform` realiza:

- normalização dos dados;
- conversão de tipos;
- integração entre população e saneamento;
- organização dos registros;
- cálculo do percentual de cobertura de esgoto;
- criação do DataFrame final.

## `src/load.py`

Responsável pela persistência dos dados.

A classe `Load` realiza:

- armazenamento dos dados brutos no MongoDB Atlas;
- armazenamento dos dados transformados no NeonDB.

## `run_etl.py`

Responsável por executar e orquestrar todo o pipeline de Engenharia de Dados.

---

# Fonte dos dados

Os dados são obtidos através da API SIDRA do IBGE.

## População

É utilizada a tabela:

**202 — População residente, por sexo e situação do domicílio**

Configuração utilizada:

```text
Variável: 93
Descrição: População residente

Sexo:
0 = Total

Situação do domicílio:
0 = Total



Nível territorial:
N102 = Bairro
```

## Saneamento

É utilizada a tabela:

**1394 — Domicílios particulares permanentes segundo o tipo de esgotamento sanitário**

Configuração utilizada:

```text
Variável: 96
Descrição: Domicílios particulares permanentes

Situação do domicílio:
0 = Total

Banheiro/sanitário:
0 = Total

Tipo de domicílio:
0 = Total

Condição de ocupação:
0 = Total

Tipo de esgotamento sanitário:

0 = Total
92855 = Rede geral de esgoto ou pluvial

Ano:


Nível territorial:
N102 = Bairro
```

---

# MongoDB Atlas

O MongoDB Atlas é utilizado como banco de dados NoSQL para armazenar os dados brutos obtidos da API do IBGE antes da transformação.

## Coleções utilizadas

```text
RECIFE_POPULACAO_BAIRROS
RECIFE_SANEAMENTO_TOTAL
RECIFE_SANEAMENTO_REDE_GERAL
```

### `RECIFE_POPULACAO_BAIRROS`

Armazena os dados brutos de população retornados pela API do IBGE.

### `RECIFE_SANEAMENTO_TOTAL`

Armazena o total de domicílios dos bairros.

### `RECIFE_SANEAMENTO_REDE_GERAL`

Armazena os domicílios ligados à rede geral de esgoto ou pluvial.

---

# NeonDB

O NeonDB é utilizado como banco de dados relacional em nuvem.

O NeonDB utiliza PostgreSQL.

Após a transformação dos dados utilizando Pandas, o resultado é carregado na tabela:

```text
recife_populacao_saneamento
```

## Estrutura da tabela

| Coluna | Descrição |
|---|---|
| `codigo_bairro` | Código do bairro no IBGE |
| `bairro` | Nome do bairro |
| `populacao` | População residente |
| `domicilios_total` | Total de domicílios |
| `domicilios_rede_geral` | Domicílios ligados à rede geral |
| `percentual_rede_esgoto` | Percentual de cobertura |
| `ano` | Ano dos dados |

---

# Cálculo do indicador

O percentual de cobertura da rede geral de esgoto é calculado durante a transformação:

```text
percentual_rede_esgoto =
(domicilios_rede_geral / domicilios_total) × 100
```

Exemplo:

```text
Domicílios totais:       1.937
Rede geral:              1.906

Cobertura:
1.906 / 1.937 × 100 = 98,40%
```

---

# Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
MONGODB_URI=mongodb+srv://USUARIO:SENHA@cluster.mongodb.net/?appName=Cluster0

DATABASE_URL=postgresql://USUARIO:SENHA@ep-exemplo.neon.tech/neondb?sslmode=require
```

As credenciais devem ser substituídas pelas informações dos respectivos serviços.

---

# Segurança

O arquivo `.env` não deve ser versionado no Git.

O `.gitignore` deve conter:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

As credenciais do MongoDB Atlas e do NeonDB devem permanecer somente nas variáveis de ambiente.

---

# Instalação

Clone o projeto:

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre na pasta:

```bash
cd ETL-main
```

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Dependências principais:

```text
requests
pymongo
python-dotenv
pandas
psycopg[binary]
```

---

# Executando a ETL

Com o ambiente virtual ativado e o `.env` configurado:

```bash
python run_etl.py
```

O pipeline executará:

```text
Etapa 1
Extração da população
        ↓
API IBGE

Etapa 2
Armazenamento
        ↓
MongoDB Atlas

Extração do saneamento
        ↓
MongoDB Atlas

Etapa 3
Recuperação dos dados
        ↓
MongoDB Atlas

Etapa 4
Transformação
        ↓
Pandas / DataFrame

Etapa 5
Carga
        ↓
NeonDB
```

---

# Resultado da execução

O pipeline foi executado com sucesso.

Resultado obtido:

```text
População: 94 bairros encontrados.

Saneamento total: 94 bairros encontrados.

Rede geral de esgoto: 94 bairros encontrados.

Total de bairros processados: 94

NeonDB: tabela 'recife_populacao_saneamento'
atualizada com sucesso.

Pipeline concluído com sucesso!

94 bairros carregados no NeonDB.
```

---

# Validação no NeonDB

Para verificar a quantidade de registros:

```sql
SELECT COUNT(*)
FROM recife_populacao_saneamento;
```

Resultado esperado:

```text
94
```

Para consultar registros:

```sql
SELECT *
FROM recife_populacao_saneamento
LIMIT 10;
```

---

# Exemplos de consultas

## Bairros mais populosos

```sql
SELECT
    bairro,
    populacao
FROM recife_populacao_saneamento
ORDER BY populacao DESC
LIMIT 10;
```

## Menores coberturas de esgoto

```sql
SELECT
    bairro,
    percentual_rede_esgoto
FROM recife_populacao_saneamento
ORDER BY percentual_rede_esgoto ASC
LIMIT 10;
```

## Maiores coberturas de esgoto

```sql
SELECT
    bairro,
    percentual_rede_esgoto
FROM recife_populacao_saneamento
ORDER BY percentual_rede_esgoto DESC
LIMIT 10;
```

---

# Exemplos de resultados

## Bairros mais populosos

| Bairro | População |
|---|---:|
| Boa Viagem | 122.922 |
| Várzea | 70.453 |
| Cohab | 67.283 |
| Iputinga | 52.200 |
| Ibura | 50.617 |

## Maiores coberturas de esgoto

| Bairro | Cobertura |
|---|---:|
| Santo Antônio | 100,00% |
| Paissandu | 99,44% |
| Soledade | 99,21% |
| Aflitos | 98,40% |
| Ilha do Leite | 98,34% |

## Menores coberturas de esgoto

| Bairro | Cobertura |
|---|---:|
| Jordão | 4,84% |
| Pau Ferro | 6,25% |
| Beberibe | 6,81% |
| Córrego do Jenipapo | 7,36% |
| Vasco da Gama | 11,63% |

---

# Análise

A partir dos dados processados:

```text
Bairros analisados:       94
População total:          1.537.704
População média/bairro:   16.358,55
Cobertura média:          56,28%
Menor cobertura:          4,84%
Maior cobertura:          100,00%
```

Os resultados demonstram uma diferença significativa na cobertura de esgotamento sanitário entre os bairros analisados.

Essa informação pode ser utilizada como indicador para estudos relacionados à infraestrutura urbana e planejamento de uma cidade inteligente.

---

# Engenharia de Dados

O projeto aplica o conceito de pipeline ETL.

## Extract

Os dados são extraídos diretamente da API SIDRA do IBGE utilizando Python e `requests`.

A aplicação utiliza:

```python
requests.get()
```

e:

```python
response.raise_for_status()
```

para realizar e validar as requisições.

## Load — MongoDB Atlas

Os dados brutos retornados pela API são armazenados no MongoDB Atlas.

```text
API IBGE
   ↓
MongoDB Atlas
```

## Transform

Os dados armazenados no MongoDB Atlas são recuperados e processados utilizando Pandas.

São realizadas operações de:

- limpeza;
- conversão de tipos;
- integração dos dados;
- cálculo de indicadores;
- organização do DataFrame.

```text
MongoDB Atlas
      ↓
    Pandas
      ↓
DataFrame
```

## Load — NeonDB

Após a transformação, o DataFrame é carregado no NeonDB.

```text
DataFrame
    ↓
PostgreSQL
    ↓
  NeonDB
```

---

# Orientação a Objetos

O projeto foi desenvolvido em Python utilizando orientação a objetos.

As principais classes são:

```text
Extract
Transform
Load
```

### `Extract`

Responsável pela extração e recuperação dos dados.

### `Transform`

Responsável pela transformação e integração dos dados.

### `Load`

Responsável pela persistência dos dados no MongoDB Atlas e NeonDB.

O arquivo `run_etl.py` realiza a orquestração das classes.

---

# Smart City

O projeto utiliza dados públicos para criar indicadores relacionados à infraestrutura urbana do Recife.

A análise permite identificar diferenças entre os bairros em relação à população e à cobertura da rede geral de esgoto.

Dessa forma, o pipeline demonstra como dados públicos podem ser utilizados para apoiar análises e decisões relacionadas ao planejamento urbano.

---

# Fluxo completo da atividade

O fluxo implementado atende à sequência solicitada:

```text
┌───────────────┐
│   API IBGE    │
└───────┬───────┘
        │
        ▼
┌───────────────────┐
│  MongoDB Atlas    │
│      NoSQL        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Transformação   │
│      Pandas       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│      NeonDB       │
│ PostgreSQL / SQL  │
└───────────────────┘
```

---

# Critérios atendidos

- [x] Extração de dados reais através de API;
- [x] Uso de `requests.get()`;
- [x] Uso de `raise_for_status()`;
- [x] Métodos com parâmetros tipados;
- [x] Validação de cidades através de dicionário;
- [x] Configurações da API centralizadas;
- [x] Transformação utilizando Pandas;
- [x] Métodos documentados com docstrings;
- [x] Orientação a objetos em Python;
- [x] Armazenamento dos dados brutos no MongoDB Atlas;
- [x] Utilização da variável `MONGODB_URI`;
- [x] Recuperação dos dados do MongoDB Atlas;
- [x] Cálculo do percentual de cobertura de esgoto;
- [x] Armazenamento dos dados transformados no NeonDB;
- [x] Utilização do PostgreSQL;
- [x] Utilização da variável `DATABASE_URL`;
- [x] Pipeline executado sem erros;
- [x] Dados de 94 bairros processados;
- [x] Fluxo API → MongoDB Atlas → Transformação → NeonDB.

---

# Autores

Projeto desenvolvido para a disciplina de Engenharia de Dados.

## Tema

**Smart City — Análise de População e Saneamento dos Bairros do Recife.**
