# Projeto de Engenharia de Dados — Smart City Recife

Pipeline de Engenharia de Dados desenvolvido para coletar, armazenar, transformar e analisar dados públicos dos bairros do Recife utilizando dados do Censo Demográfico do IBGE.

## Sobre o projeto

O projeto aplica conceitos de Engenharia de Dados em um cenário de Smart City.

São utilizados dados reais disponibilizados pelo IBGE através da API SIDRA, permitindo analisar informações relacionadas à população e ao saneamento dos bairros do Recife.

O pipeline realiza as seguintes etapas:

```text
API do IBGE
     ↓
   Extract
     ↓
  MongoDB
     ↓
  Transform
   (Pandas)
     ↓
   SQLite
     ↓
   Análise
```

## Objetivo

Coletar dados públicos do IBGE referentes aos bairros do Recife e transformá-los em uma estrutura organizada para análise.

O projeto utiliza:

- População residente por bairro;
- Total de domicílios particulares permanentes;
- Domicílios ligados à rede geral de esgoto ou pluvial;
- Percentual de cobertura da rede geral de esgoto.



---

## Tecnologias utilizadas

- Python 3
- Requests
- Pandas
- PyMongo
- python-dotenv
- MongoDB
- SQLite
- API SIDRA / IBGE

---

## Estrutura do projeto

```text
ProjEngDados-202602-master/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── run_etl.py
│
├── exemplos/
│   ├── exemplos.py
│   └── teste_mongo.py
│
├── jsons/
│
├── notebooks/
│   └── aula4.ipynb
│
└── src/
    ├── __init__.py
    ├── extract.py
    ├── transform.py
    └── load.py
```

### Responsabilidade dos arquivos

#### `src/extract.py`

Responsável pela extração dos dados da API do IBGE.

Também possui a funcionalidade de leitura dos dados armazenados no MongoDB.

#### `src/transform.py`

Responsável pela transformação dos dados utilizando Pandas.

Realiza:

- normalização dos dados;
- integração entre população e saneamento;
- organização dos registros;
- cálculo do percentual de cobertura de esgoto.

#### `src/load.py`

Responsável pela persistência dos dados.

Realiza a carga:

- dos dados brutos no MongoDB;
- dos dados transformados no SQLite.

#### `run_etl.py`

Responsável por executar todo o pipeline de Engenharia de Dados.

---

# Fonte dos dados

Os dados são obtidos através da API SIDRA do IBGE.

## População

É utilizada a tabela **202 — População residente, por sexo e situação do domicílio**.

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

É utilizada a tabela **1394 — Domicílios particulares permanentes... segundo o tipo de esgotamento sanitário**.

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



Nível territorial:
N102 = Bairro
```

---

# Banco de dados

## MongoDB

O MongoDB é utilizado para armazenar os dados brutos obtidos da API.

São utilizadas três coleções:

```text
RECIFE_POPULACAO_BAIRROS
RECIFE_SANEAMENTO_TOTAL
RECIFE_SANEAMENTO_REDE_GERAL
```

### População

A coleção:

```text
RECIFE_POPULACAO_BAIRROS
```

armazena os dados brutos de população retornados pelo IBGE.

### Saneamento

A coleção:

```text
RECIFE_SANEAMENTO_TOTAL
```

armazena o total de domicílios.

A coleção:

```text
RECIFE_SANEAMENTO_REDE_GERAL
```

armazena os domicílios ligados à rede geral de esgoto ou pluvial.

---

# SQLite

Depois da transformação, os dados são armazenados no banco:

```text
ibge.db
```

Na tabela:

```text
recife_populacao_saneamento
```

A tabela possui as seguintes colunas:

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
MONGODB_URI=mongodb://localhost:27017
```

O arquivo `.env` não deve ser versionado no Git.

---

# Instalação

Clone o projeto e entre na pasta:

```bash
cd ProjEngDados-202602-master
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
pip install -r requirements.txt
```

---

# MongoDB

O projeto utiliza MongoDB para armazenamento dos dados brutos.

É possível executar o MongoDB através do Docker.

Verifique se o container está em execução:

```bash
docker ps
```

O MongoDB deve estar disponível na porta:

```text
27017
```

Exemplo de container:

```text
mongodb-ibge
```

---

# Executando o pipeline

Com o ambiente virtual ativado:

```bash
python run_etl.py
```

O pipeline executará as seguintes etapas:

```text
Etapa 1: extração da população
        ↓
MongoDB

Etapa 2: extração do saneamento
        ↓
MongoDB

Etapa 3: leitura dos dados do MongoDB
        ↓
Transformação

Etapa 4: transformação com Pandas
        ↓
DataFrame

Etapa 5: carga no SQLite
```

Ao final deverá aparecer:

```text
Pipeline concluído com sucesso!
```

---

# Validação

O pipeline foi executado com sucesso utilizando os dados dos bairros do Recife.

Resultado:

```text
94 bairros processados
```

O SQLite contém:

```text
Tabela: recife_populacao_saneamento
Registros: 94
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

A partir dos dados processados, foram obtidos os seguintes resultados:

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

O projeto aplica o conceito de pipeline ETL:

## Extract

Extração dos dados diretamente da API do IBGE utilizando Python e `requests`.

A aplicação utiliza:

```python
requests.get()
```

e:

```python
response.raise_for_status()
```

para realizar e validar as requisições.

## Transform

Os dados brutos são processados utilizando Pandas.

São realizadas operações de:

- limpeza;
- conversão de tipos;
- integração dos dados;
- cálculo de indicadores;
- organização do DataFrame.

## Load

Os dados brutos são armazenados no MongoDB.

Os dados transformados são armazenados no SQLite.

---

# Smart City

O projeto utiliza dados públicos para criar indicadores relacionados à infraestrutura urbana do Recife.

A análise permite identificar diferenças entre os bairros em relação à população e à cobertura da rede geral de esgoto.

Dessa forma, o pipeline demonstra como dados públicos podem ser utilizados para apoiar análises e decisões relacionadas ao planejamento urbano.

---

# Critérios atendidos

O projeto atende aos seguintes requisitos:

- [x] Extração de dados reais através de API;
- [x] Uso de `requests.get()`;
- [x] Uso de `raise_for_status()`;
- [x] Métodos com parâmetros tipados;
- [x] Validação de cidades através de dicionário;
- [x] Configurações da API centralizadas;
- [x] Transformação utilizando Pandas;
- [x] Métodos documentados com docstrings;
- [x] Armazenamento dos dados brutos no MongoDB;
- [x] Utilização da variável `MONGODB_URI`;
- [x] Armazenamento dos dados transformados no SQLite;
- [x] Pipeline executado sem erros;
- [x] Dados de 94 bairros processados.

---

# Autores

Projeto desenvolvido para a disciplina de Engenharia de Dados.

Tema:

**Smart City — Análise de População e Saneamento dos Bairros do Recife.**
