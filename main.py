from threading import Lock

from fastapi import FastAPI, HTTPException

from database import pedidos_db
from schemas import RecogidaEntrada

app = FastAPI(title="Picking")

bloqueo_db = Lock()


def buscar_pedido(pedido_id: int):
    pedido = pedidos_db.get(pedido_id)

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado",
        )

    return pedido


@app.get("/pedidos")
def listar_pedidos():
    return list(pedidos_db.values())


@app.get("/pedidos/{pedido_id}")
def consultar_pedido(pedido_id: int):
    return buscar_pedido(pedido_id)


@app.post("/pedidos/{pedido_id}/recogidas")
def registrar_recogida(
    pedido_id: int,
    datos: RecogidaEntrada,
):
    with bloqueo_db:
        pedido = buscar_pedido(pedido_id)

        producto = next(
            (
                producto
                for producto in pedido["productos"]
                if producto["sku"] == datos.sku
            ),
            None,
        )

        if producto is None:
            raise HTTPException(
                status_code=404,
                detail="El producto no pertenece al pedido",
            )

        pendientes = producto["cantidad_solicitada"] - producto["cantidad_recogida"]

        if datos.cantidad > pendientes:
            raise HTTPException(
                status_code=400,
                detail=f"Solo quedan {pendientes} unidades por recoger",
            )

        producto["cantidad_recogida"] += datos.cantidad

        completado = all(
            producto["cantidad_recogida"] == producto["cantidad_solicitada"]
            for producto in pedido["productos"]
        )

        pedido["estado"] = "COMPLETADO" if completado else "EN_PROCESO"

        return {
            "mensaje": "Recogida registrada",
            "pedido_id": pedido_id,
            "sku": producto["sku"],
            "cantidad_recogida": producto["cantidad_recogida"],
            "cantidad_pendiente": (
                producto["cantidad_solicitada"] - producto["cantidad_recogida"]
            ),
            "estado": pedido["estado"],
        }
