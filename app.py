from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = "troque-por-uma-chave-forte"  # necessário para session (sessão do navegador)

DATA_FILE = Path("respostas.json")

def salvar(payload: dict) -> None:
    payload["criado_em"] = datetime.now().isoformat(timespec="seconds")

    dados = []
    if DATA_FILE.exists():
        try:
            dados = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dados = []

    dados.append(payload)
    DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


@app.route("/", methods=["GET"])
def home():
    session.pop("form", None)
    return redirect(url_for("step1"))


@app.route("/step/1", methods=["GET", "POST"])
def step1():
    if request.method == "POST":
        form = session.get("form", {})
        form.update({
            "nome_empresa": request.form.get("nome_empresa", "").strip(),  # NOVO
            "empresa_tamanho": request.form.get("empresa_tamanho", ""),
            "segmento": request.form.get("segmento", "").strip(),
            "rh_estruturado": request.form.get("rh_estruturado", "")
        })
        session["form"] = form
        return redirect(url_for("step2"))

    return render_template("step1.html", progress=33, data=session.get("form", {}))


@app.route("/step/2", methods=["GET", "POST"])
def step2():
    if request.method == "POST":
        if request.form.get("_action") == "back":
            return redirect(url_for("step1"))

        form = session.get("form", {})
        form.update({
            "retencao_desafio": request.form.get("retencao_desafio", ""),
            "perdeu_por_adaptacao": request.form.get("perdeu_por_adaptacao", ""),
            "custo_substituicao": request.form.get("custo_substituicao", ""),
            "conflitos_frequencia": request.form.get("conflitos_frequencia", ""),
            "comunicacao_retrabalho": request.form.get("comunicacao_retrabalho", ""),
            "treinamento_perfis": request.form.get("treinamento_perfis", ""),
            "protocolo_integracao": request.form.get("protocolo_integracao", ""),
            "afastamentos": request.form.get("afastamentos", ""),
            "lideranca_preparada": request.form.get("lideranca_preparada", ""),
        })
        session["form"] = form
        return redirect(url_for("step3"))

    return render_template("step2.html", progress=66, data=session.get("form", {}))


@app.route("/step/3", methods=["GET", "POST"])
def step3():
    if request.method == "POST":
        if request.form.get("_action") == "back":
            return redirect(url_for("step2"))

        form = session.get("form", {})
        form.update({
            "investimento_lideranca": request.form.get("investimento_lideranca", ""),
            "interesse_diagnostico": request.form.get("interesse_diagnostico", ""),
            "faixa_investimento": request.form.get("faixa_investimento", ""),
            "padrao_oculto": request.form.get("padrao_oculto", "").strip(),

            # 17–19 (neurodiversidade)
            "neuro_diag": request.form.get("neuro_diag", ""),
            "adaptacoes_simples": request.form.get("adaptacoes_simples", ""),
            "treinamento_neurodiv": request.form.get("treinamento_neurodiv", ""),
        })
        salvar(form)
        session.pop("form", None)
        return redirect(url_for("thanks"))

    return render_template("step3.html", progress=100, data=session.get("form", {}))


@app.route("/thanks", methods=["GET"])
def thanks():
    return render_template("thanks.html", progress=100)


if __name__ == "__main__":
    app.run(debug=True)