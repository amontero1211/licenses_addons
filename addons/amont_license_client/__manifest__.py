{
    "name": "Amont - License Client",
    "version": "17.0.0.1",
    "sequence": 1,
    "description": """This is an Addon from Andrea for his pastanty""",
    "summary": """Server for Validation of Licenses""",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["account"],
    "data": [
        "views/res_company_views.xml",
        "views/account_move_views.xml",
        "data/service_cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "amont_license_client/static/src/views/*",
            "amont_license_client/static/src/services/*",
        ],
    },
    "demo": [],
}
