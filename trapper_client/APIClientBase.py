from json import JSONDecodeError
import logging
import csv
import io
import time
from typing import Dict

import requests
import attr
from typing_extensions import Literal

from trapper_client import err

logging.basicConfig(
    level=logging.DEBUG,  # muestra DEBUG y superior
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

@attr.s
class APIClientBase:
    access_token: str = attr.ib(repr=False)
    user_name: str = attr.ib(repr=False)
    user_password: str = attr.ib(repr=False)
    verify_ssl: bool = attr.ib(repr=False, default=True)
    base_url: str = attr.ib(repr=False, default="https://wildintel-trap.uhu.es")

    name = "zoom_api_client"
    user_id: str = "me"

    def _paginate(self, items, page: int, per_page: int = 10):
        """Devuelve los registros de la página indicada (1-indexed)."""
        start = (page - 1) * per_page
        end = start + per_page
        return items[start:end]

    def _auth(self):
        """Devuelve headers o auth tuple según el modo de autenticación."""
        if self.access_token:
            return {"Authorization": f"Token {self.access_token}"}, None
        elif self.user_name and self.user_password:
            return {}, (self.user_name, self.user_password)
        else:
            raise ValueError("No se ha configurado ni token ni usuario/clave")

    def make_request(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        query: Dict = None,
        body: Dict = None,
        raise_on_error=True,
    ) -> requests.Response:
        allowed_methods = "GET POST PATCH DELETE PUT".split()
        if method not in allowed_methods:
            raise ValueError(
                f'Invalid method: {method}. Must be one of {", ".join(allowed_methods)}'
            )

        headers, auth = self._auth()
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        logging.debug(f"Making {method} request to {endpoint}")
        session = requests.Session()

        logging.debug(f"Request headers: {headers}")
        logging.debug(f"Request auth: {auth}")

        r = session.request(method, url, headers=headers, auth=auth,params=query, json=body, verify=self.verify_ssl)

        if 200 <= r.status_code < 300:
            content_type = r.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = r.json()  # <- notar los paréntesis
                #logging.debug("Response JSON:\n%s", json.dumps(data, indent=4))
                logging.debug(f"Results json {r.json()}")

                if "pagination" not in data or "results" not in data:
                    page = 1
                    per_page = len(data) if isinstance(data, list) else 1
                    pages = 1
                    total = len(data) if isinstance(data, list) else 1
                    paged_rows = data if isinstance(data, list) else [data]

                    response_obj = {
                        "pagination": {
                            "page": page,
                            "page_size": per_page,
                            "pages": pages,
                            "count": total,
                        },
                        "results": paged_rows,
                    }

                    import json
                    r._content = json.dumps(response_obj).encode("utf-8")
                    r.headers["Content-Type"] = "application/json"
                    r.json = lambda: response_obj

                return r
            elif "text/csv" in content_type or r.text.strip().startswith(
                    tuple("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")):
                csv_text = r.text
                reader = csv.DictReader(io.StringIO(csv_text))
                rows = list(reader)
                total = len(rows)

                response_obj = {
                    "pagination": {
                        "page": 1,
                        "page_size": total,
                        "pages": 1,
                        "count": total,
                    },
                    "results": rows,
                }

                import json
                r._content = json.dumps(response_obj).encode("utf-8")
                r.headers["Content-Type"] = "application/json"
                r.json = lambda: response_obj

                logging.debug(f"Results from csv {response_obj}")
                return r
            else:
                return r
        try:
            body = r.json()
            try:
                message = body["_error"]["message"]
            except KeyError:
                message = body
        except JSONDecodeError:
            body = r.text
            message = body

        logging.error(f"Unsuccessful request to {r.url}: [{r.status_code}] {message}")

        logging.debug(f"Full response: {body}")
        logging.debug(f"Headers: {r.headers}")
        logging.debug(f"Params: {query}")
        logging.debug(f"Body: {body}")
        if not raise_on_error:
            logging.warning(
                f"raise_on_error is False, ignoring API error and returning response"
            )
            return r

        if r.status_code in err.HTTP_ERRORS_MAP:
            raise err.HTTP_ERRORS_MAP[r.status_code](message)
        else:
            raise err.APIError(message)

    def get(
        self, endpoint: str, query: Dict = None, raise_on_error: bool = True
    ) -> requests.Response:
        return self.make_request(
            endpoint, method="GET", query=query, raise_on_error=raise_on_error
        )

    def get_all_pages(
        self, endpoint: str, query: Dict = None, raise_on_error: bool = True
    ) -> Dict:
        query = {} if query is None else query.copy()
        res = self.get(endpoint, query=query, raise_on_error=raise_on_error).json()
        pagination = res.get("pagination")
        page = pagination.get("page")
        pages = pagination.get("pages")

        if pages <= 1:
            return res

        results = {k: (v[:] if isinstance(v, list) else v) for k, v in res.items()}

        # Siguientes páginas
        while page < pages:
            page += 1
            query["page"] = page

            next_res = self.get(
                endpoint,
                query=query,
                raise_on_error=raise_on_error,
            ).json()

            # Unificamos listas
            for k, v in next_res.items():
                if isinstance(v, list) and k in results:
                    results[k].extend(v)
                elif k not in results:
                    results[k] = v

            # actualizamos paginación
            pagination = next_res.get("pagination", pagination)

        results["pagination"] = pagination
        return results

    def post(
        self,
        endpoint: str,
        query: Dict = None,
        body: Dict = None,
        raise_on_error: bool = True,
    ) -> requests.Response:
        return self.make_request(
            endpoint,
            method="POST",
            query=query,
            body=body,
            raise_on_error=raise_on_error,
        )

    def patch(
        self,
        endpoint: str,
        query: Dict = None,
        body: Dict = None,
        raise_on_error: bool = True,
    ) -> requests.Response:
        return self.make_request(
            endpoint,
            method="PATCH",
            query=query,
            body=body,
            raise_on_error=raise_on_error,
        )

    def put(
        self,
        endpoint: str,
        query: Dict = None,
        body: Dict = None,
        raise_on_error: bool = True,
    ) -> requests.Response:
        return self.make_request(
            endpoint,
            method="PUT",
            query=query,
            body=body,
            raise_on_error=raise_on_error,
        )

    def delete(
        self,
        endpoint: str,
        query: Dict = None,
        body: Dict = None,
        raise_on_error: bool = True,
    ) -> requests.Response:
        return self.make_request(
            endpoint,
            method="DELETE",
            query=query,
            body=body,
            raise_on_error=raise_on_error,
        )
