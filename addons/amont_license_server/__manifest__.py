{
    "name": "Amont - License Server",
    "version": "17.0.0.1",
    "sequence": 1,
    "description": """This is an Addon from Andrea for his pastanty""",
    "summary": """Server for Validation of Licenses""",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/server_clients_views.xml",
        "views/menu.xml",
        "data/mail_template_data.xml",
        "data/service_cron.xml",
    ],
    "demo": [],
}
