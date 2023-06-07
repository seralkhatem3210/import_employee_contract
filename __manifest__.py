# -*- coding: utf-8 -*-
 
{
    'name': ' استيراد عقود الموظفين النظام',
    'version': '15.0.0.3',
    'category' : 'Sales',
    'sequence'  : '-10',
    'summary': 'تحميل عقود الموظفين و كذلك تعديل الموظفين الموجودين عبر ملفات اكسل بالصيغتين XLS && CSV',
    'description': """
	
    import employees from CSV or Excel file,
    import employee in odoo apps,
    from csv import employees in odoo,
    from excel import employees in odoo,
    import employees from XLS and CSV file,
    import vendors from CSV and Excel in odoo,
    import supplier from CSV and Excel in odoo,
    import employees/vendors/suppliers from CSV and Excel in odoo,
   
    """,
    'author': 'سرالختم جمال',
    'website': 'http://sirelkhatim.unaux.com',
    'depends': ['base','sale','sale_management','stock','purchase', 'contacts','import_employee', 'hr'],
    'data': [
        'security/ir.model.access.csv',
	     "views/employee_contract.xml",
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
    'application' : True,
}
