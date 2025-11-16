import logging
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
        self.page_size = page_size

        self.page = 0
        self.buffer = []
        self.total_pages = None
        self.exhausted = False

    def __iter__(self):
        return self

    def __next__(self):
        # Si se acabaron los resultados de la página actual, cargar la siguiente
        while self._index >= len(self._results):
            if self._exhausted:
                raise StopIteration

            # cargar página desde la API
            page_query = self.query.copy()
            page_query["page"] = self._page
            page_query["page_size"] = self.page_size

            logger.debug(f"Cargando página {self._page} del endpoint {self.endpoint}")
            response = self.client.get_all_pages(self.endpoint, page_query)
            self._results = response.get("results", [])
            self._page += 1
            self._index = 0

            if not self._results:
                self._exhausted = True
                raise StopIteration

        # Tomar el siguiente item
        raw_item = self._results[self._index]
        self._index += 1

        # Convertir a objeto concreto del schema
        item_obj = self.schema(**raw_item) if self.schema else raw_item

        # Aplicar filtro local si existe
        if self.filter_fn:
            if self.filter_fn(item_obj):
                return item_obj
            else:
                return self.__next__()  # Saltar item filtrado
        else:
            return item_obj
