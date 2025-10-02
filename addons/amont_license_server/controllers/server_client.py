from odoo import http
from odoo.http import route, request 
import logging

_logger = logging.getLogger(__name__)

class ServerClient(http.Controller):

    @route("/license/validate", type="json", methods=["POST"], auth="public")
    def validate_license(self):
        print("------------------")
        print("making license validation")
        print("------------------")
        data = request.get_json_data()
        
        res = request.env["amont.server.client"].sudo().validate_license(
            client=data.get("name"),
            database=data.get("database"),
            license=data.get("license")
        )

        return res[0] if res else {}

