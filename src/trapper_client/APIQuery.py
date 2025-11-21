import logging
import re
from typing import Dict, Any, Type, Callable, Iterator
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class APIQuery:
    def __init__(self, client, endpoint, query=None, schema=None
                 ,filter_fn: Callable[[BaseModel], bool] = None, page_size: int = 50):
        self.client = client
        self.endpoint = endpoint
        self.query = {} if query is None else query.copy()
        self.schema = schema
        self.filter_fn = filter_fn

        self._page_size = page_size
        self._page =-1
        self._pages=0
        self._count=0
        self._last_results = []
        self._last_index=0
        self.exhausted = self._exhausted = False

    def __iter__(self):
        return self

    def __next__(self):

        if self._last_index >= len(self._last_results) and self._page < self._pages:
            # cargar página desde la API
            page_query = self.query.copy()
            page_query["page"] = self._page+1
            page_query["page_size"] = self._page_size

            # Resolver placeholders en el endpoint usando valores de la query
            endpoint_resolved = self.endpoint
            for key in re.findall(r"\{([^}]+)\}", self.endpoint):
                if key in page_query:
                    endpoint_resolved = endpoint_resolved.replace("{" + key + "}", str(page_query.pop(key)))

            logger.debug(f"Cargando página {page_query["page"]} del endpoint {endpoint_resolved}")
            response = self.client.get(endpoint_resolved, page_query, raise_on_error=True)

            self._last_results = response.get("results", [])

            if len(self._last_results) == 0:
                self._exhausted = True
                raise StopIteration

            pagination = response.get("pagination", {"page": -1, "pages": 1})
            self._page = int(pagination.get("page", -1))
            self._pages = int(pagination.get("pages", 1))
            self._last_index=0
        elif self._last_index >= len(self._last_results) and self._page >= self._pages:
            self._exhausted = True
            raise StopIteration

        logger.debug(f"Devolviendo el elemento {self._last_index} de la página {self._page} que tiene {len(self._last_results)} elementos")

        # Tomar el siguiente item
        raw_item = self._last_results[self._last_index]
        self._last_index += 1

        # Convertir a objeto concreto del schema
        data = {
            "pagination": {
                "page": 1,
                "page_size": 10,
                "pages": 1,
                "count": 1,
            },
            "results": [raw_item],
        }

        item_obj = self.schema(**data).results[0] if self.schema else raw_item

        # Aplicar filtro local si existe
        if self.filter_fn:
            if self.filter_fn(item_obj):
                return item_obj
            else:
                return self.__next__()  # Saltar item filtrado
        else:
            return item_obj

    def close(self):
        # limpieza sencilla: marcar agotado y vaciar buffers
        self._exhausted = True
        self._last_results = []
        self._last_index = -1
        self._pages = 0
        self._page = -1

    def __enter__(self):
        # Permite "with APIQuery(...)" y devuelve el propio iterable
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Si existe un método close, llamarlo para liberar recursos
        close = getattr(self, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                # no propagar en la limpieza
                pass
        # devolver False para que las excepciones se propaguen normalmente
        return False
