# -*- coding: utf-8 -*-
"""Agente de Promoções - aplicação principal (Flask)."""
import json
import logging
import os
import threading
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request, send_from_directory, abort
from apscheduler.schedulers.background import BackgroundScheduler

from config import AUTO_REFRESH_MINUTES, MIN_DISCOUNT_PERCENT, CACHE_FILE, DATA_DIR, HISTORY_DIR
from agents.scraper import run_all_agents, filter_by_discount
from utils.pdf_export import export_products_to_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("promo_agent.app")
app = Flask(__name__)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
_lock = threading.Lock()
_state = {"all_products": [], "last_updated": None, "next_update": None, "min_discount": MIN_DISCOUNT_PERCENT, "is_refreshing": False}


def _persist_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_state["all_products"], f, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.warning("Não foi possível salvar cache: %s", exc)


def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _state["all_products"] = json.load(f)
        except (OSError, json.JSONDecodeError):
            _state["all_products"] = []


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "sim", "yes", "on")


def refresh_products():
    with _lock:
        if _state["is_refreshing"]:
            return
        _state["is_refreshing"] = True
    try:
        products = run_all_agents()
        with _lock:
            _state["all_products"] = products
            _state["last_updated"] = datetime.now().isoformat()
            _state["next_update"] = (datetime.now() + timedelta(minutes=AUTO_REFRESH_MINUTES)).isoformat()
            _persist_cache()
    finally:
        with _lock:
            _state["is_refreshing"] = False


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(refresh_products, "interval", minutes=AUTO_REFRESH_MINUTES, id="auto_refresh", next_run_time=None)


@app.route("/")
def index():
    return render_template("index.html", refresh_minutes=AUTO_REFRESH_MINUTES, min_discount=MIN_DISCOUNT_PERCENT)


@app.route("/api/products")
def api_products():
    category = request.args.get("category", "").strip()
    min_discount_raw = request.args.get("min_discount")
    try:
        min_discount = int(float(min_discount_raw)) if min_discount_raw not in (None, "") else MIN_DISCOUNT_PERCENT
    except (TypeError, ValueError):
        min_discount = MIN_DISCOUNT_PERCENT
    ignore_discount = _parse_bool(request.args.get("ignore_discount", "false"))
    with _lock:
        products = list(_state["all_products"])
    if category and category.lower() != "todas":
        products = [p for p in products if p["category"] == category]
    products = filter_by_discount(products, min_discount=min_discount, ignore_discount=ignore_discount)
    return jsonify({"products": products, "count": len(products), "min_discount": min_discount, "ignore_discount": ignore_discount})


@app.route("/api/categories")
def api_categories():
    with _lock:
        products = list(_state["all_products"])
    return jsonify({"categories": sorted({p["category"] for p in products})})


@app.route("/api/status")
def api_status():
    with _lock:
        return jsonify({"last_updated": _state["last_updated"], "next_update": _state["next_update"], "is_refreshing": _state["is_refreshing"], "total_products": len(_state["all_products"]), "default_min_discount": MIN_DISCOUNT_PERCENT, "refresh_interval_minutes": AUTO_REFRESH_MINUTES})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    body = request.get_json(silent=True) or {}
    min_discount = body.get("min_discount", MIN_DISCOUNT_PERCENT)
    ignore_discount = _parse_bool(body.get("ignore_discount", False))
    refresh_products()
    with _lock:
        all_products = list(_state["all_products"])
        last_updated = _state["last_updated"]
        next_update = _state["next_update"]
    visible_products = filter_by_discount(all_products, min_discount=min_discount, ignore_discount=ignore_discount)
    return jsonify({"ok": True, "count": len(visible_products), "total_collected": len(all_products), "last_updated": last_updated, "next_update": next_update})


@app.route("/api/export-pdf", methods=["POST"])
def api_export_pdf():
    body = request.get_json(silent=True) or {}
    ids = body.get("ids") or []
    with _lock:
        products = list(_state["all_products"])
    if ids:
        products = [p for p in products if p["id"] in ids]
    if not products:
        return jsonify({"ok": False, "error": "Nenhum produto para exportar."}), 400
    filepath = export_products_to_pdf(products)
    filename = os.path.basename(filepath)
    return jsonify({"ok": True, "filename": filename, "url": f"/historico/{filename}"})


@app.route("/historico")
def historico_list():
    files = sorted(os.listdir(HISTORY_DIR), reverse=True)
    return jsonify({"files": [f for f in files if f.endswith(".pdf")]})


@app.route("/historico/<path:filename>")
def historico_download(filename):
    if not filename.endswith(".pdf") or "/" in filename or "\\" in filename:
        abort(404)
    return send_from_directory(HISTORY_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    _load_cache()
    scheduler.start()
    threading.Thread(target=refresh_products, daemon=True).start()
    logger.info("Servidor iniciado em http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
