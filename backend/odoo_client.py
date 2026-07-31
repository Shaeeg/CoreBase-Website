import os
import xmlrpc.client


class OdooConnectionError(Exception):
    """Raised when Odoo can't be reached, auth fails, or rejects the write."""


class OdooClient:
    def __init__(self, url=None, db=None, username=None, api_key=None):
        try:
            self.url = (url or os.environ["ODOO_URL"]).rstrip("/")
            self.db = db or os.environ["ODOO_DB"]
            self.username = username or os.environ["ODOO_USERNAME"]
            self.api_key = api_key or os.environ["ODOO_API_KEY"]
        except KeyError as exc:
            raise OdooConnectionError(
                f"Missing required environment variable: {exc.args[0]}"
            ) from exc
        self._uid = None

    def _get_uid(self):
        if self._uid is None:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            try:
                self._uid = common.authenticate(self.db, self.username, self.api_key, {})
            except (OSError, xmlrpc.client.ProtocolError, xmlrpc.client.Fault) as exc:
                raise OdooConnectionError(f"Could not reach Odoo: {exc}") from exc
            if not self._uid:
                raise OdooConnectionError(
                    "Odoo authentication failed — check ODOO_DB/ODOO_USERNAME/ODOO_API_KEY."
                )
        return self._uid

    def create_lead(self, *, name, company, phone):
        uid = self._get_uid()
        models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        lead_values = {
            "name": f"Website inquiry — {company}",
            "contact_name": name,
            "partner_name": company,
            "phone": phone,
            "type": "lead",
            "description": "Submitted via the corebase.az contact form.",
        }
        try:
            return models.execute_kw(
                self.db, uid, self.api_key,
                "crm.lead", "create",
                [lead_values],
            )
        except xmlrpc.client.Fault as fault:
            raise OdooConnectionError(f"Odoo rejected the lead: {fault.faultString}") from fault
        except (OSError, xmlrpc.client.ProtocolError) as exc:
            raise OdooConnectionError(f"Could not reach Odoo: {exc}") from exc
