from typing import Any, Callable, TypeVar

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from postgrest.exceptions import APIError

from database import supabase

app = FastAPI(title="Sistema de Controle de EPI")

# Em produção, troque * pela origem pública do frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

T = TypeVar("T")


def executar(consulta: Callable[[], T]) -> T:
    """Executa uma operação do Supabase e converte erros SQL em HTTP."""
    try:
        return consulta()
    except APIError as erro:
        codigo = str(getattr(erro, "code", ""))
        mensagem = getattr(erro, "message", None) or str(erro)
        status = {
            "23505": 409,
            "23503": 400,
            "23514": 400,
        }.get(codigo, 500)
        descricoes = {
            "23505": "Registro duplicado.",
            "23503": "Referência inválida: confira os registros relacionados.",
            "23514": "Valor inválido ou estoque insuficiente.",
        }
        raise HTTPException(status_code=status, detail=descricoes.get(codigo, mensagem)) from erro
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {erro}") from erro


class Entrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class SetorEntrada(Entrada):
    nome: str = Field(min_length=1, max_length=120)


class FuncionarioEntrada(Entrada):
    nome: str = Field(min_length=1, max_length=120)
    matricula: str = Field(min_length=1, max_length=120)
    cargo: str | None = Field(default=None, max_length=120)
    id_setor: int = Field(gt=0)


class EpiEntrada(Entrada):
    nome: str = Field(min_length=1, max_length=120)
    tipo: str | None = Field(default=None, max_length=120)
    ca: str | None = Field(default=None, max_length=20)
    estoque: int = Field(default=0, ge=0)
    estoque_minimo: int = Field(default=0, ge=0)


class ItemEntrega(Entrada):
    id_epi: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class EntregaEntrada(Entrada):
    id_funcionario: int = Field(gt=0)
    id_responsavel: int = Field(gt=0)
    assinatura_path: str | None = Field(default=None, max_length=500)
    itens: list[ItemEntrega] = Field(min_length=1)


@app.get("/")
def inicio():
    return {"mensagem": "Sistema de controle de EPI funcionando!"}


@app.get("/teste-conexao")
def teste_conexao():
    resposta = executar(lambda: supabase.table("setor").select("*").limit(1).execute())
    return {"mensagem": "Conexão com Supabase funcionando!", "dados": resposta.data}


@app.get("/setores")
def listar_setores():
    return executar(lambda: supabase.table("setor").select("*").order("nome").execute()).data


@app.post("/setores", status_code=201)
def criar_setor(setor: SetorEntrada):
    resposta = executar(lambda: supabase.table("setor").insert(setor.model_dump()).execute())
    return resposta.data


@app.get("/funcionarios")
def listar_funcionarios():
    resposta = executar(
        lambda: supabase.table("funcionario")
        .select("id,nome,matricula,cargo,id_setor,setor(nome)")
        .order("nome")
        .execute()
    )
    return [
        {**funcionario, "setor_nome": (funcionario.get("setor") or {}).get("nome")}
        for funcionario in resposta.data
    ]


@app.post("/funcionarios", status_code=201)
def criar_funcionario(funcionario: FuncionarioEntrada):
    resposta = executar(
        lambda: supabase.table("funcionario").insert(funcionario.model_dump()).execute()
    )
    return resposta.data


@app.get("/epis")
def listar_epis():
    return executar(lambda: supabase.table("epi").select("*").order("nome").execute()).data


@app.post("/epis", status_code=201)
def criar_epi(epi: EpiEntrada):
    resposta = executar(lambda: supabase.table("epi").insert(epi.model_dump()).execute())
    return resposta.data


@app.get("/epis/estoque-baixo")
def listar_estoque_baixo():
    epis = executar(lambda: supabase.table("epi").select("*").execute()).data
    return [epi for epi in epis if epi["estoque"] <= epi["estoque_minimo"]]


@app.post("/entregas", status_code=201)
def registrar_entrega(entrega: EntregaEntrada):
    parametros: dict[str, Any] = {
        "p_id_funcionario": entrega.id_funcionario,
        "p_id_responsavel": entrega.id_responsavel,
        "p_itens": [item.model_dump() for item in entrega.itens],
        "p_assinatura_path": entrega.assinatura_path,
    }
    resposta = executar(lambda: supabase.rpc("registrar_entrega", parametros).execute())
    return {"id_entrega": resposta.data, "mensagem": "Entrega registrada com sucesso."}
