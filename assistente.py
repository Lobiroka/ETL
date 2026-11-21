import json

from openai import OpenAI


class AssistenteGPT:
    def __init__(self, chave_api: str, modelo="gpt-6-luna", base_url=None):
        if not chave_api:
            raise ValueError("Defina GPT (ou OPENAI_API_KEY) no .env para usar a IA.")
        self.cliente = OpenAI(
            api_key=chave_api, base_url=base_url or None, timeout=60.0
        )
        self.modelo = modelo

    def perguntar(self, instrucao: str, pergunta: str) -> str:
        resposta = self.cliente.chat.completions.create(
            model=self.modelo,
            messages=[
                {"role": "system", "content": instrucao},
                {"role": "user", "content": pergunta},
            ],
        )
        texto = resposta.choices[0].message.content
        if not texto:
            raise ValueError("O modelo não retornou uma resposta em texto.")
        return texto.strip()

    def gerar_sql(self, pergunta: str, esquema: str) -> str:
        instrucao = (
            "Você é especialista em PostgreSQL. Escreva UM SELECT que responda "
            "à pergunta usando apenas as tabelas e colunas abaixo, do schema public. "
            "Não altere dados nem configurações. Responda somente com SQL, sem "
            "explicações e sem blocos Markdown.\n\n"
            f"Tabelas:\n{esquema}"
        )
        return self.perguntar(instrucao, pergunta).replace("```sql", "").replace("```", "").strip()

    def explicar_resultado(self, pergunta: str, dados: list[dict]) -> str:
        instrucao = (
            "Responda em português, de forma curta, usando apenas os dados fornecidos. "
            "As consultas retornam no máximo 10 linhas: não trate uma amostra como "
            "o conjunto completo. Agregações SQL consideram todos os registros."
        )
        return self.perguntar(
            instrucao,
            f"Pergunta: {pergunta}\nDados: {json.dumps(dados, default=str, ensure_ascii=False)}",
        )
