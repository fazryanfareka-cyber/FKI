{
    "name": "LL - Asset Management",
    "version": "18.0.1.0.1",
    "summary": "Assign and track of company assets like laptops, appliances, and peripherals.",
    "description": """
Asset Management
===================

Manage and track company assets including laptops, desktops and appliances.

Features:
---------
- Asset registration and categorization
- Employee asset assignment
- Issuance and Return tracking
- Maintenance logging
- Asset location tracking
- (Optional) Depreciation integration
""",
    "author": "Lawrence Lanzaderas",
    "website": "https://lawrencelanzaderas-portfolio.netlify.app",
    "license": "LGPL-3",
    "category": "Operations/Assets",
    "depends": ["base", "hr"],
    "data": [
        "security/asset_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",

        "data/ir_sequence.xml",

        "views/ll_asset_category_views.xml",
        "views/ll_asset_location_views.xml",
        "views/ll_asset_views.xml",
        "views/ll_asset_issuance_views.xml",
        "views/ll_asset_return_views.xml",

        #inherited views
        "views/res_company_views.xml",
        "views/asset_hr_emp_views.xml",
        "views/asset_hr_dept_views.xml",
        "views/asset_res_partner_views.xml",

        "views/asset_menu.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [],
    # },

    "installable": True,
    "application": True,
    "auto_install": False,

    # 'price': 14.29,
    # 'currency': 'USD',
    'support': 'lslanzaderas@gmail.com',
    'images': [
        'static/description/banner.gif',
        'static/description/icon.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
        'static/description/screenshot3.png',
        'static/description/screenshot4.png',
        'static/description/screenshot5.png',
        'static/description/screenshot6.png',
        'static/description/screenshot7.png',
        'static/description/screenshot8.png',
        'static/description/screenshot9.png',
        'static/description/screenshot10.png',
    ],

    'maintainer': 'Lawrence S. Lanzaderas <lslanzaderas@gmail.com>',
}
