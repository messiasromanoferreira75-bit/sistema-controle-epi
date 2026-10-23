
from fastapi import FastAPI
from pydantic import BaseModel
from database import supabase

app = FastAPI()


class SetorEntrada(BaseModel):
    nome: str


@app.get("/")
def inicio():
    return {"mensagem": "Sistema de controle de EPI funcionando!"}


@app.get("/teste-conexao")
def teste_conexao():
    resposta = supabase.table("setor").select("*").limit(1).execute()
    return {
        "mensagem": "Conexão com Supabase funcionando!",
        "dados": resposta.data
    }


@app.get("/setores")
def listar_setores():
    resposta = supabase.table("setor").select("*").execute()
    return resposta.data


@app.post("/setores")
def criar_setor(setor: SetorEntrada):
    resposta = supabase.table("setor").insert({
        "nome": setor.nome
    }).execute()
    return resposta.data