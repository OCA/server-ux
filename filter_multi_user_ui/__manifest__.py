{
    'name': 'Filter Multi User UI',
    'version': '18.0.1.0.0',
    'category': 'Filter',
    'summary': 'Provide nicer UI to select users to share filter with',
    'author': 'AFI-BibLibre',
    'website': 'https://www.afi.fr',
    'depends': ['web', 'filter_multi_user'],
     "assets": {
        "web.assets_backend": [
            "filter_multi_user_ui/static/src/js/custom_favorite_item.js",
            "filter_multi_user_ui/static/src/js/search_model_patch.js",
            "filter_multi_user_ui/static/src/xml/custom_favorite_item.xml",
            "filter_multi_user_ui/static/src/js/search_bar_menu_patch.js",
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
