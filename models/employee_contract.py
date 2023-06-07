﻿# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import tempfile
import binascii
import xlrd
from odoo.exceptions import Warning , ValidationError
from odoo import models, fields, exceptions, api, _
import time
from datetime import date, datetime
import io
import logging
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class AccountMove(models.Model):
    _inherit = 'account.move'
    sale_type_id = fields.Char('sale Type id')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    type_id = fields.Char('Type_id')  #ValueError: Invalid field 'type_id' on model 'sale.order'

class ResPartner(models.Model):
    _inherit = 'res.partner'
class Company(models.Model):
    _inherit = 'res.company'
class Currency(models.Model):
    _inherit = 'res.currency'
    
# class GeneralIrregularWage(models.Model):
#     _name = 'irreguller.wage'
    
#     company_id = fields.Many2one('res.company', store=True, copy=False,
#                                 string="Company",
#                                 default=lambda self: self.env.user.company_id.id)
#     currency_id = fields.Many2one('res.currency', string="Currency",
#                                     related='company_id.currency_id',
#                                     default=lambda
#                                     self: self.env.user.company_id.currency_id.id)
#     name= fields.Char('name')
#     # fee = fields.Monetary(string="Fee")
#     value = fields.Monetary('القيمة')
#     contract_id = fields.Many2one('hr.contract')
class Contract(models.Model):
    _inherit = 'hr.contract'

class HrsPayslips(models.Model):
    _inherit = 'hr.payslip'

    hr_revesion = fields.Boolean('مراجعة الموارد البشرية')
    x_revesion_accounting = fields.Boolean()
    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract')
    department_id  = fields.Many2one('hr.department', 
                                     related='employee_id.department_id', 
                                     string='القسم', 
                                     store=True,
                                     readonly=False, 
                                     tracking=True )
    department = fields.Char(string="القسم",related='employee_id.department_id.name', store=True, readonly=False, tracking=True )
    company_id = fields.Many2one('res.company')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                    related='company_id.currency_id',
                                    default=lambda
                                    self: self.env.user.company_id.currency_id.id)
    salary_net = fields.Monetary(related='contract_id.salary_net', string="صافي المرتب",  store=True)
    salary_net_calculated = fields.Monetary(' صافي المرتب',  store=True, readonly=True) #, compute='_clac_tot_salary', track_visibility='always', track_sequence=6) #
    mwama = fields.Monetary('الموائمة')
    unpaid = fields.Monetary('الاستقطاع')
    apsent = fields.Monetary('الغياب')   
    late = fields.Monetary('التأخير')
    loan_cut = fields.Monetary('السلف')
    other_cut = fields.Monetary('استقطاعات أخري')
    total_cut = fields.Monetary('إجمالي الإستقطاعات',  store=True, readonly=True) #, compute='_clac_tot_cut', track_visibility='always', track_sequence=6) #
    solaf  = fields.Monetary('التأخير')
    month_alw = fields.Float()
    month_disc = fields.Float('الخصم')
    month_disc_discription = fields.Char('التعليق')
    days1 = fields.Float('عدد الأيام إضافي ')
    minutes = fields.Float('عدد الدقائق إضافي ')
    adds_days = fields.Monetary(string='قيمة الاضافي أيام', compute =  '_calc_adds_days')
    adds_minutes = fields.Monetary(string='قيمة الاضافي دقائق', compute =  '_calc_adds_minutes')
    total_salary = fields.Monetary(related='contract_id.total_salary')
    x_without_pay = fields.Monetary('بدون أجر')
    x_calc_without_pay =fields.Monetary('قيمة بدون أجر', compute='_calc_without_pay')

    @api.depends('contract_id.salary_net','x_without_pay')
    def x_calc_without_pay(self):
        for rec in self:
            rec.x_calc_without_pay = rec.x_without_pay*(rec.contract_id.salary_net/30)

    apsent2 = fields.Monetary('بدون أجر')
    calc_apsent2 = fields.Monetary('بدون أجر', compute='_calc_apsent2')
    @api.depends('contract_id.salary_net', 'apsent2')
    def _calc_apsent2(self):
        for rec in self:
            rec.calc_apsent2 = rec.apsent2*(rec.contract_id.salary_net/30)
    month_alw_comment = fields.Char('ملاحظات الاجر الإضافي')

    @api.depends('contract_id.salary_net', 'days1')
    def _calc_adds_days(self):
        for rec in self:
            rec.adds_days = rec.days1*(rec.contract_id.salary_net/30)

    
    @api.depends('contract_id.salary_net','minutes')
    def _calc_adds_minutes(self):
        for rec in self:
            rec.adds_minutes = rec.minutes*(rec.contract_id.salary_net/14400)


      # month_alw = fields.Float()

#    precentage = fields.Selection(selection=[('10', '10%'),('25', '25%'),('50', '50%'),], string='النسبة', default='10')
 #   number = fields.Float('عدد الايام')
  #  gazaa = fields.Float(string='الجزاء', compute='_clac_gazaa', default = 0.0)
   # @api.depends('precentage', 'number')
#    def _clac_gazaa(self):
 #       for rec in self:
#            rate = 10
#            tot = rec.contract_id.salary_total
#            if rec.precentage == '10':
#                rate = 10
#            if rec.precentage == '25':
#                rate = 25
#            if rec.precentage == '50':
#                rate = 50
#            rec.gazaa = (tot/30)*rate* rec.number/(100)

#    @api.depends('mwama', 'unpaid', 'apsent', 'late', 'loan_cut', 'other_cut','gazaa')
#    def _clac_tot_cut(self):
#        for rec in self:
#            rec.total_cut = rec.mwama + rec.unpaid + rec.apsent + rec.late + rec.loan_cut + rec.other_cut + rec.gazaa

 #   @api.depends('total_cut', 'contract_id.salary_net','gazaa','mwama', 'unpaid', 'apsent', 'late', 'loan_cut', 'other_cut')
 #   def _clac_tot_salary(self):
  #      for rec in self:
   #         rec.salary_net_calculated = rec.contract_id.salary_net - (rec.mwama + rec.unpaid + rec.apsent + rec.late + rec.loan_cut + rec.other_cut + rec.gazaa)
        # return total_cut
 

# amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
# amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always', track_sequence=6)
# Compute function:

# @api.depends('order_line.price_total')
# def _amount_all(self):
#   #  " ""
#     Compute the total amounts of the SO.
#     """
#     for order in self:
#         amount_untaxed = amount_tax = 0.0
#         for line in order.order_line:
#             amount_untaxed += line.price_subtotal
#             amount_tax += line.price_tax
#         order.update({
#             'amount_untaxed': amount_untaxed,
#             'amount_tax': amount_tax,
#             'amount_total': amount_untaxed + amount_tax,
#         })

 
class EmployeeContract(models.Model):
    _inherit = 'hr.contract'
    
    total_salary = fields.Monetary(string='إجمالي المرتب', compute='_calc_total_salary')
    autorenew = fields.Boolean('تجديد تلقائي ')	# #يتجدد تلقائيًا	قيمة منطقية	
    call_alw	= fields.Monetary('بدل اتصالات')
    call_wage	= fields.Monetary('إضافي  اتصالات')
    look_alw	= fields.Monetary('بدل قيافة')
    look_wage	= fields.Monetary('إضافي  قيافة')
    transport_alw	= fields.Monetary('بدل نقل')
    transport_wage	= fields.Monetary('إضافي  نقل')
    supervise_alw	= fields.Monetary('بدل إشراف')
    supervise_wage	= fields.Monetary('إضافي  إشراف')
    other_alw	= fields.Monetary('بدلات أخري')
    other_wage	= fields.Monetary('إضافي  أخري')
    other_alw_total	= fields.Monetary('مجموع البدلات الأخري')
    pay_cut	= fields.Monetary('مقدار الموائمة')
    rewards	= fields.Monetary('مكافاءات')
    call_allowance	= fields.Monetary('بدل الاتصالات')
    home_allowance	= fields.Monetary('بدل السكن')
    home_wage	= fields.Monetary('إضافي السكن')
    company_portion	= fields.Monetary('استقطاع من الشركة')
    employee_portion	= fields.Monetary('استقطاع من الموظف')
    employee_remission	= fields.Boolean('إعفاء الموظف من الإستقطاع')
    contract_file	= fields.Binary('ملف العقد')
    contract_no	= fields.Char('رقم العقد')
    trail_type = fields.Selection([('1', 'تجريبية 1'),('2', 'تجريبية 2')], string='نوع فترة التجربة', index=True)
    trial_date_adjustment	= fields.Integer('طول فترة التجربة')
    trial_extended_adjustment= fields.Integer('طول التمديد للفترةالتجريبية')
    salary_net = fields.Monetary('صافي المرتب')

    salary_total = fields.Monetary('اجمالي المرتب')
    total_wage = fields.Monetary('مجموع الإضافي')
    total_perquisites  = fields.Monetary('إجمالي الإمتيازات')
    resoom  = fields.Monetary(' خصم الرسوم')
    cell1  = fields.Monetary(' cell1')
    cell2  = fields.Monetary(' cell2')
    cell3  = fields.Monetary(' cell3')
    cell4  = fields.Monetary(' cell4')
    cell5  = fields.Monetary(' cell5')
    badalat_total  = fields.Monetary(' بدلات أحرى')
    bank_name  = fields.Char(' Bank Name')
    bank_account  = fields.Char(' Bank Account')
    path_edu = fields.Selection([('وطني', 'وطني'),('مصري', 'مصري'),('مشترك', 'مشترك'),('الأمناء', 'الأمناء')],string='المسار')
    employee_status = fields.Char('حالة الموظف')
    gosi_register = fields.Selection([('Registered', 'Registered'),('Not Registered', 'Not Registered')], string='التسجيل في التأمينات الاجتماعية', index=True, tracking=True)
    gosi_register_date = fields.Date('تاريخ التسجيل في التأمينات')
    contract_type = fields.Selection([
        ('1', 'Monthly'),
        ('2', 'Quarterly'),
        ('3', 'Semi-annually'),
        ('4', 'Annually'),
        ('5', 'Weekly'),
        ('6', 'Bi-weekly'),
        ('7', 'Bi-monthly'),
    ], string='نوع العقد ', index=True, default='1')
    country_code	= fields.Char('Country Code')
    effictive_date	= fields.Date('تاريخ المباشرة')
    hard_support_end_date	= fields.Date('تاريخ إنتهاء HARD')
    hard_support_start_date	= fields.Date('تاريخ بداية HARD')
    hrdf_company_support_amount = fields.Monetary('مقدار دعم صندوق الموارد البشرية للشركة')
    hrdf_employee_support_amount = fields.Monetary('مقدار دعم صندوق الموارد البشرية الموظف')
    hrdf_support_percentage = fields.Monetary('نسبة دعم صندوق الموارد البشرية')
    hrdf_support = fields.Selection([('1', 'داعم'),('2', 'غير داعم')], string='دعم صندوق الموارد البشرية', index=True)
    employee_name_in_contract	= fields.Char('اسم الموظف في العقد')
    groth_monthly	= fields.Char('الشهرية')
    department_edu	= fields.Char('القسم (بنين/بنات)')
    department_accounting	= fields.Char('القسم الحسابات')
    identification_id = fields.Char(related='employee_id.identification_id', string="ID")
    uploded = fields.Char("Uploaded")
    basic = fields.Monetary('الاساسي')

    @api.depends('basic','call_alw','call_wage','look_alw','look_wage','transport_alw','transport_wage','supervise_alw','supervise_wage','other_alw','other_wage','other_alw_total','rewards','call_allowance','home_allowance','home_wage')
    def _calc_total_salary(self):
        for rec in self:
            rec.total_salary = rec.basic+rec.call_alw+rec.call_wage+rec.look_alw+rec.look_wage+rec.transport_alw+rec.transport_wage+rec.supervise_alw+rec.supervise_wage+rec.other_alw+rec.other_wage+rec.other_alw_total+rec.rewards+rec.call_allowance+rec.home_allowance+rec.home_wage - rec.month_disc




#    @api.depends('mwama', 'unpaid', 'apsent', 'late', 'loan_cut', 'other_cut','gazaa')
#    def _clac_tot_cut(self):
#        for rec in self:
#            rec.total_cut = rec.mwama + rec.unpaid + rec.apsent + rec.late + rec.loan_cut + rec.other_cut + rec.gazaa

 #   @api.depends('total_cut', 'contract_id.salary_net','gazaa','mwama', 'unpaid', 'apsent', 'late', 'loan_cut', 'other_cut')
 #   def _clac_tot_salary(self):
  #      for rec in self:
   #         rec.salary_net_calculated = rec.contract_id.salary_net - (rec.mwama + rec.unpaid + rec.apsent + rec.late + rec.loan_cut + rec.other_cut + rec.gazaa)
        # return total_cut



# general_irregular_wage_list	= fields.Many2Many('irreguller.wage','الإجور المتغيرة العامة')
# x_studio_citizenship_value	citizenship value	اختيار	​
# ​
    unpaid = fields.Monetary('الاستقطاع')
    apsent = fields.Monetary('الغياب')
    late = fields.Monetary('التأخير')
    loan_cut = fields.Monetary('السلف')
    other_cut = fields.Monetary('استقطاعات أخري')
    total_cut = fields.Monetary('إجمالي الإستقطاعات')
    gross_monthly = fields.Monetary('إضافي شهري')
    himaya = fields.Boolean('حماية الإجور')
    paied_type = fields.Selection([
        ('1', 'بنك'),
        ('2', 'نقداً'),
    ], string='الصــرف  ', index=True, default='1')

class Employee(models.Model):
    _inherit = 'hr.employee'
    remining_leaves_paid_dayes = fields.Float('متبقي الإجازة المدفوعة')
    total_leaves_paid_dayes_used = fields.Float('عدد الايام المستخدم من الإجازة المدفوعة')
    Work_permit_no = fields.Integer('leaves_count')
    employee_no = fields.Char('رقم الموظف')
    sponsor_name = fields.Char('الكفيل')
    address_status = fields.Char('حالة العنوان')
    iqama_job = fields.Char('الوظيفة في الاقامة')
    hijri_date_type = fields.Char('تاريخ الميلاد هجري')
    hijri_day = fields.Char('اليوم -هجري')
    hijri_month = fields.Char('الشهر -هجري')
    hijri_year = fields.Char('السنة - هجري')
    medical_insurance_end_date = fields.Char('تاريخ انتهاء التأمين الطبي')
    id_type = fields.Selection([('1', 'هوية وطنية'),('2', ' إقامة نظامية ')],string='نوع الاثبات' ,default='1') 
    citizainship_no = fields.Char('المواطنة')

class gen_employee(models.TransientModel):
    _name = "gen.employee.contract"
    _description = "Import employee Wizard"
    
    file = fields.Binary('File')
    file_name = fields.Char()
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    employee_contract_option = fields.Selection([('create','Create employee'),('update','Update employee')],string='Option', required=True,default="create")
    
    # def find_department(self,val):
    #     if type(val) == dict:
    #         department_search = self.env['hr.department'].search([('name','=',val.get('department_id'))],limit=1)
    #         if department_search:
    #             return department_search.id
    #         else:
    #             department = self.env['hr.employee'].create({'name':val.get('department_id')})
    #             return department.id
    #     else:
    #         department_search = self.env['hr.employee'].search([('name','=',val['department_id'])],limit=1)
    #         if department_search:
    #             return department_search.id
    #         else:
    #             department = self.env['hr.employee'].create({'name':val['department_id']})
    #             return department.id

    def create_employee_contract(self, values):
        # parent = state = country = saleperson =  vendor_pmt_term = cust_pmt_term = False
        if values.get('department_id'):
            department = self.find_department(values)
        # if valsale_typesaleperson = saleperson_search.id
        # if values.get('cust_pmt_term'):
        #     cust_payment_term_search = self.env['account.payment.term'].search([('name','=',values.get('cust_pmt_term'))])
        #     if cust_payment_term_search:
            # cust_pmt_term = cust_payment_term_search.id
        # if values.get('vendor_pmt_term'):
        #     vendor_payment_term_search = self.env['account.payment.term'].search([('name','=',values.get('vendor_pmt_term'))])
        #     if vendor_payment_term_search:
            # vendor_pmt_term = vendor_payment_term_search.id
        # customer = values.get('customer')
        # supplier = values.get('vendor')
        # is_customer = False
        # is_supplier = False
        # if ((values.get('customer')) == '1'):
        # 	is_customer = True
        # if ((values.get('vendor')) == '1'):
        #     is_supplier = True
        # if ((values.get('customer')) == 'True'):
        #     is_customer = True
        # if ((values.get('vendor')) == 'True'):
        #     is_supplier = True
           
        if values.get('address_home_id'):
        # department = self.find_department(values)
        # if type(val) == dict:
            address_home_search = self.env['res.partner'].search([('name','=',values.get('address_home_id'))],limit=1)
            if address_home_search:
                address_home_id =  address_home_search.id
            else:
                address_home_search = self.env['res.partner'].create({'name':values.get('address_home_id')})
                address_home_id =  address_home_search.id
        # else:
        #     address_home_search = self.env['res.partner'].search([('name','=',values.get('address_home_id'))],limit=1)
        #     if address_home_search:
        #         address_home_id =  address_home_search.id
        #     else:
        #         address_home_search = self.env['hr.department'].create({'name':values.get('address_home_id')})
                #         address_home_id =  address_home_search.id  
           
        vals = {
                    'name':values.get('name'),
                    'contract_ids':values.get('contract_ids'),
                    'work_phone':values.get('work_phone'),
                    'work_email':values.get('work_email'),
                    'company_id':values.get('company_id'),
                    'department_id':values.get('department_id'),
                    'gender':values.get('gender'),
                    'identification_id':values.get('identification_id'),
                    'bank_account_id':values.get('bank_account_id'),
                    'private_email':values.get('private_email'),
                    'user_id':values.get('user_id'),
                    'visa_expire':values.get('visa_expire'),
                    'Work_permit_no':values.get('Work_permit_no'),
                    'work_location_id':values.get('work_location_id'),
                    'mobile_phone':values.get('mobile_phone'),
                    'address_id':values.get('address_id'),
                    'website_message_ids':values.get('website_message_ids'),
                    'resource_calendar_id':values.get('resource_calendar_id'),
                    'address_home_id':values.get('address_home_id'),
                    'citizainship':values.get('citizainship'),
                    'employee_no':values.get('employee_no'),
                    'sponsor_name':values.get('sponsor_name'),
                    'gender':values.get('gender'),
                    'address_status':values.get('address_status'),
                    'certificate':values.get('certificate'),
                    'iqama_job':values.get('iqama_job'),
                    'hijri_date_type':values.get('hijri_date_type'),
                    'hijri_day':values.get('hijri_day'),
                    'hijri_month':values.get('hijri_month'),
                    'hijri_year':values.get('hijri_year'),
                    'sponsor_identification':values.get('sponsor_identification'),
                    'medical_insurance_end_date':values.get('medical_insurance_end_date'),
                    'website_message_id':values.get('website_message_id'),
                    'id_expiry_date':values.get('id_expiry_date'),
                    'id_type':values.get('id_type'),
                    'contract_id':values.get('contract_id'),
                    'citizainship_no':values.get('citizainship_no'),
                    'country_id':values.get('country_id'),
                    'remining_leaves_paid_dayes':values.get('remining_leaves_paid_dayes'),
                    'total_leaves_paid_dayes_used':values.get('total_leaves_paid_dayes_used'),
                    'leaves_count':values.get('leaves_count'),
                    'current_leave_state':values.get('current_leave_state'),
                    'from':values.get('from'),
                    'to':values.get('to'),
                    'job_id':values.get('job_id'),
                    'contract_date':values.get('contract_date'),
                    }
        employee_search = self.env['hr.contract'].search([('name','=',values.get('name'))]) 
        if employee_search:
            # raise ValidationError(_('"%s" هذا الموظف موجود بالفعل.') % values.get('name'))  
            x =1 
        else:      	
            res = self.env['hr.contract'].create(vals)

    def import_employee_contract(self):
        if self.import_option == 'csv':
            if self.file:
                file_name = str(self.file_name)
                extension = file_name.split('.')[1]
                if extension not in ['csv','CSV']:
                    raise ValidationError(_('Please upload only csv file.!'))  
            keys = ['name','type','parent','street','street2','city','state','zip','country','website','phone','mobile','email','customer','vendor','saleperson','ref']#,'cust_pmt_term','vendor_pmt_term'
            
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                res = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Invalid file!"))
            values = {}
            for i in range(len(file_reader)):
                field = map(str, file_reader[i])
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'option':self.import_option})
                        if self.employee_contract_option == 'create':
                            res = self.create_employee_contract(values)
                        else:
                            search_employee = self.env['hr.contract'].search([('name','=',values.get('name'))])
                            parent = False
                            state = False
                            country = False
                            saleperson = False
                            # vendor_pmt_term = False
                            # cust_pmt_term = False
                            is_customer = False
                            is_supplier = False
                            if ((values.get('customer')) == '1'):
                                is_customer = True
        	
                            if ((values.get('vendor')) == '1'):
                                is_supplier = True
        	
                            if ((values.get('customer')) == 'True'):
                                is_customer = True
        	
                            if ((values.get('vendor')) == 'True'):
                                is_supplier = True

                            if values.get('type') == 'company_id':
                                if values.get('parent'):
                                    raise ValidationError(_('You can not give parent if you have select type is company_id'))
                                type =  'company_id'
                            else:
                                type =  'person'
                                parent_search = self.env['res.employee'].search([('name','=',values.get('parent'))])
                                if parent_search:
                                    parent =  parent_search.id
                                # else:
                                #     raise ValidationError(_("Parent contact  not available"))
                            
                            # if values.get('state'):
                            #     state = self.find_state(values)
                            # if values.get('country'):
                            #     country = self.find_country(values)
                            # if values.get('country_id'):
                            #     country = self.find_country_id(values)
                            # if values.get('saleperson'):
                            # #     saleperson_search = self.env['res.users'].search([('name','=',values.get('saleperson'))])
                            # #     if not saleperson_search:
                            # #         raise ValidationError(_("Salesperson not available in system"))
                            # #     else:
                            #     saleperson = saleperson_search.id
                            # if values.get('cust_pmt_term'):
                            #     cust_payment_term_search = self.env['account.payment.term'].search([('name','=',values.get('cust_pmt_term'))])
                            #     # if not cust_payment_term_search:
                            #     #     raise ValidationError(_("Payment term not available in system"))
                            #     # else:
                            #     # cust_pmt_term = cust_payment_term_search.id
                            #     cust_pmt_term = 1
                            # if values.get('vendor_pmt_term'):
                            #     vendor_payment_term_search = self.env['account.payment.term'].search([('name','=',values.get('vendor_pmt_term'))])
                            #     # if not vendor_payment_term_search:
                            #     #     raise ValidationError(_("Payment term not available in system"))
                            #     # else:
                            #     vendor_pmt_term = 1
                                # vendor_pmt_term = vendor_payment_term_search.id
                            # if (values.get('company_id') == 'شركة الحياة المحدودة'):
                            #     company_id = 1
                            # else:
                            #     company_id = 2

                            # if values.get('city'):
                            #     company_id = 1
                            # else:
                            #     company_id = 2

                            # if values.get('vendor_pmt_term'):
                            #     vendor_payment_term_search = self.env['account.payment.term'].search([('name','=',values.get('vendor_pmt_term'))])
                            #     # if not vendor_payment_term_search:
                            #     #     raise ValidationError(_("Payment term not available in system"))
                            #     # else:
                            #     vendor_pmt_term = 1
                            #     # vendor_pmt_term = vendor_payment_term_search.id
                            #get_birth_date(self, birth_date):
                            if values.get('birth_date'):
                                b_date = values.get('birth_date')
                                birth_date = b_date.strftime("'%Y/%m/%d")
                                birth_date = datetime.strptime(b_date, '%Y/%m/%d')
                                if(birth_date):
                                    birth_date = datetime.strptime(b_date, '%Y/%m/%d')
                                else: 
                                    b_date = '1444-9-9'
                                    birth_date = b_date.strftime("'%Y/%m/%d")
                                    birth_date = datetime.strptime(b_date, '%Y/%m/%d')

                                    # return birth_date
                                # except Exception:
                                #     raise ValidationError(_('تنسيق تاريخ الميلاد غير صحيح ! التاريخ يجب أن يكون بهذا التنسيق  YYYY/MM/DD'))

                                #  "شركة الحياة المحدودة"
                                # LINE 1: ...artner" SET "city"='المدينة المنورة',"company_id"='شركة الحي...                            
                            if search_employee:
                                # search_employee_contract.department_id = department_id
                                # search_employee_contract.user_id = values.get('user_id')
                                # search_employee_contract.visa_expire = values.get('visa_expire')
                                # search_employee_contract.address_id = values.get('address_id')
                                # search_employee_contract.website_message_id = values.get('website_message_id')
                                # search_employee_contract.resource_calender_id = values.get('resource_calender_id')
                                # search_employee_contract.address_home_id = values.get('address_home_id')
                                # search_employee_contract.citizainship = citizainship
                                # search_employee_contract.employee_no = values.get('employee_no')
                                search_employee_contract.sponsor_name = values.get('sponsor_name')
                                search_employee_contract.gender = values.get('gender')
                                search_employee_contract.address_status = values.get('address_status')
                                search_employee_contract.certificate = values.get('certificate')
                                # search_employee_contract.iqama_job = values.get('iqama_job')
                                # search_employee_contract.hijri_date_type = values.get('hijri_date_type')
                                # search_employee_contract.hijri_day = values.get('hijri_day')
                                # search_employee_contract.hijri_month = values.get('hijri_month')
                                # search_employee_contract.hijri_year = values.get('hijri_year')
                                # search_employee_contract.sponsor_identification = values.get('sponsor_identification')
                                # search_employee_contract.medical_insurance_end_date = values.get('medical_insurance_end_date')
                                
                                search_employee_contract.id_expiry_date = values.get('id_expiry_date')
                                search_employee_contract.id_type = values.get('id_type')
                                search_employee_contract.currentcontract_active = values.get('currentcontract_active')
                                search_employee_contract.remining_leaves = values.get('remining_leaves')
                                # search_employee_contract.allocation_used_count = allocation_used_count
                                search_employee_contract.allocation_count = values.get('allocation_count')
                                search_employee_contract.current_leave_state = values.get('current_leave_state')
                                search_employee_contract.job_id = values.get('job_id')
                                                     
                            # else:
                            #     raise ValidationError(_('%s هذا الموظف غير موجود  .') % values.get('name'))
        else:
            if self.file:
                file_name = str(self.file_name)
                extension = file_name.split('.')[1]
                if extension not in ['xls','xlsx','XLS','XLSX']:
                    raise ValidationError(_('Please upload only xls file.!'))
            try:
                fp = tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                values = {}
                res = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_("Please upload only xls file.!"))
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if self.employee_contract_option == 'create':
                        values.update( {'name':str(line[0]),
                                        'contract_ids':line[1],
                                        'work_phone':line[2],
                                        'work_email':line[3],
                                        'company_id':line[4],
                                        'department_id': line[5],
                                        'gender': line[6],
                                        'identification_id': line[7],
                                        'bank_account_id': line[8],
                                        'private_email': line[9],                                   
                                        'user_id': line[10],
                                        'visa_expire': line[11],
                                        'Work_permit_no': line[12],
                                        'work_location_id': line[13],
                                        'mobile_phone': line[14],
                                        'address_id': line[15],
                                        'website_message_ids': line[16],
                                        'resource_calendar_id': line[17],
                                        'address_home_id': line[18],
                                        'citizainship': line[19],
                                        'employee_no': line[20],
                                        'sponsor_name': line[21],
                                        'gender': line[22],
                                        'address_status': line[23],
                                        'certificate': str(line[24]),
                                        'iqama_job': str(line[25]),
                                        'hijri_date_type': line[26],
                                        'hijri_day': line[27],
                                        'hijri_month': line[28],
                                        'hijri_year': line[29],
                                        'sponsor_identification': line[30],
                                        'medical_insurance_end_date': line[31],
                                        'website_message_id': line[32],
                                        'id_expiry_date': line[33],
                                        'id_type': line[34],
                                        'contract_id': line[35],
                                        'citizainship_no': line[36],
                                        'country_id': line[37],
                                        'remining_leaves_paid_dayes': line[38],
                                        'total_leaves_paid_dayes_used': line[39],
                                        'leaves_count': line[40],
                                        'current_leave_state': line[41],
                                        'from': line[42],
                                        'to': line[43],
                                        'job_id': line[44],               
                                        'contract_date': line[45],               
                                        'leave_date': line[46],               
                                        })
                        res = self.create_employee_contract(values)
                    else:
                        employee = self.env['hr.employee'].search([('name','=',line[1])],limit=1)
                        # employee = self.env['hr.employee'].search([('identification_id','=',line[8])],limit=1)
                        # # employee = self.env['hr.employee'].search([('identification_id','=',line[2])],limit=1)
                        employee_id = employee.id
                        search_employee_contract = self.env['hr.contract'].search([('employee_id','=',employee_id)], limit=1, order='id desc')
#################################################################ID search #############################################################################################################################################################################
                        # id = line[8]
                        # separator = '.'
                        # emp_id = id.split(separator, 1)[0]
##############################################################################################################################################################################################################################################                        
                        # my_str = 'one!two!three'
                        # ✅ remove everything after FIRST occurrence of character
                        # separator = '!'
                        # result_1 = my_str.split(separator, 1)[0]
                        # search_employee_contract = self.env['hr.contract'].search([('identification_id','=', emp_id)], limit=1, order='id desc')
                        
                        # if line[1]:
                        #     # department = self.find_department(values)
                        #     # if type(val) == dict:
                        #     department_search = self.env['hr.department'].search([('name','=',line[1])],limit=1)
                        #     if department_search:
                        #         department =  department_search.id
                        #     else:
                        #         department = self.env['hr.department'].create({'name':line[1]})
                        #         department =  department.id
                        # else:
                        #     department_search = self.env['hr.department'].search([('name','=',line[1])],limit=1)
                        #     if department_search:
                        #         department =  department_search.id
                        #     else:
                        #         department = self.env['hr.department'].create({'name':line[1]})
                        #         department =  department.id
                        # if line[4]:
                        #     company = self.env['res.company'].search([('name','=',line[4])])
                        #     company_id = company.id
                        # if line[6]:
                        #     if line[6] =='ذكر':
                        #         gender = 'male'
                        #     else:
                        #         gender = 'female'
                        # user_id = False
                        # if line[29]:
                        #     gosi_register_contract = line[29]
                        #     if ((gosi_register_contract != 'Registered') , (gosi_register_contract != ' Registered')):
                        #         gosi_register_contract = 'Not Registered'
                        #     else:
                        #         gosi_register_contract = 'Registered'

                        if search_employee_contract:
                            # search_employee_contract.department_id = department
                            # if resource_calendar_id_search:
                            #     resource_calendar_id_search_id =  resource_calendar_id_search.id
                            # else:
                            #     search_employee_contract.department_id = department
#####################################################################مسودة الرواتب #####################################################################
                            # search_employee_contract.wage = line[6]
                            # search_employee_contract.department_edu = line[6]
                            # search_employee_contract.department_accounting = line[7]
                            # search_employee_contract. = line[4]
                            # search_employee_contract.citizainship = line[4]
                            # search_employee_contract.apsent = line[20]
                            # search_employee_contract.late = line[21]
                            # search_employee_contract.employee_portion = line[22]
                            # search_employee_contract.loan_cut = line[23]
                            # search_employee_contract.resoom = line[24]
                            # search_employee_contract.pay_cut = line[25]
                            # # search_employee_contract.himaya = line[29]
##########################################################################################################################################
                            # # search_employee_contract.identification_id = line[2]
                            # search_employee_contract.travel_allowance = line[10]
                            # search_employee_contract.supervise_alw = line[11]
                            # search_employee_contract.other_alw = line[12]
                            # # search_employee_contract.other_wage = line[13]
                            # search_employee_contract.home_allowance = line[14]
                            # search_employee_contract.look_alw = line[15]
                            # search_employee_contract.gross_monthly = line[17]
                            # # # search_employee_contract.loan_wage = line[18]
                            # search_employee_contract.call_alw = line[19]
                            # # search_employee_contract.call_allowance = line[19]
                            # search_employee_contract.pay_cut = line[20]
                            # search_employee_contract.other_wage = line[26]
                            # # search_employee_contract.loan_cut = line[33]
                            # search_employee_contract.employee_portion = line[34]
                            # search_employee_contract.company_portion = line[43]
                            # search_employee_contract.total_perquisites = line[44]
                            # # search_employee_contract.unpaid = line[46]
                            # # search_employee_contract.pay_cut = line[47]
                            # # search_employee_contract.state = line[50]

                            # citizainship_no = fields.Char('citizainship_no')
                            # en_name = fields.Char(string='Name EN')
                            # citizainship = fields.Boolean(string='التوطين', default=False)
                            # # path_edu = fields.Selection([('1', 'وطني'),('2', 'مصري'),('3', 'مشترك'),('4', 'الأمناء')],string='المسار',default='1')
                            # department_edu = fields.Char(string='القسم دراسي')
                            # department_accounting = fields.Char(string='القسم - الحسابات')
                            # hemaiat_egoor = fields.Boolean(string='حماية الإجور', default=False)
                            # search_employee_contract.name_en = line[2]

                            # # search_employee_contract.job = line[4]
                            # search_employee_contract.path_edu = line[5]
                            # search_employee_contract.department_edu = line[6]
                            # search_employee_contract.department_accounting = line[7]
                            search_employee_contract.identification_id = line[8]
                            # search_employee_contract.bank_name = line[11]
                            # search_employee_contract.bank_account = line[12]
                            # # # search_employee_contract. = line[4]
                            # # # search_employee_contract.citizainship = line[4]
                            # search_employee_contract.wage = line[14]
                            # search_employee_contract.home_allowance = line[15]
                            # search_employee_contract.salary_total = line[17]
                            search_employee_contract.wage = line[12]

                            search_employee_contract.other_wage = line[16]
                            search_employee_contract.apsent = line[18]
                            search_employee_contract.late = line[19]
                            # search_employee_contract.employee_portion = line[22]
                            search_employee_contract.loan_cut = line[21]
                            search_employee_contract.resoom = line[22]
                            search_employee_contract.himaya = line[23]
                            search_employee_contract.pay_cut = line[24]
                            search_employee_contract.total_cut = line[25]
                            search_employee_contract.salary_net = line[26]
                            # if gosi_register_contract:
                            #     search_employee_contract.gosi_register = gosi_register_contract
                            # else:
                            # search_employee_contract.gosi_register = line[29]
                            # search_employee_contract.employee_status = line[39]
                            # search_employee_contract.badalat_total = line[40]
                            #  resoom  = fields.Monetary(' خصم الرسوم')
                            # cell1  = fields.Monetary(' cell1')
                            # cell2  = fields.Monetary(' cell2')
                            # cell3  = fields.Monetary(' cell3')
                            # cell4  = fields.Monetary(' cell4')
                            search_employee_contract.uploded = line[27]
                        else:
                            raise ValidationError(_('%s employee not found.') % emp_id)
        
        return res
