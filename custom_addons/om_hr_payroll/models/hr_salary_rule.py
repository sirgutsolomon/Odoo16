from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

class HrPayrollStructure(models.Model):
    """
    Salary structure used to defined
    - Basic
    - Allowances
    - Deductions
    """
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'

    @api.model
    def _get_parent(self):
        return self.env.ref('om_om_hr_payroll.structure_base', False)

    name = fields.Char(required=True)
    code = fields.Char(string='Reference', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    note = fields.Text(string='Description')
    parent_id = fields.Many2one('hr.payroll.structure', string='Parent', default=_get_parent)
    children_ids = fields.One2many('hr.payroll.structure', 'parent_id', string='Children', copy=True)
    rule_ids = fields.Many2many('hr.salary.rule', 'hr_structure_salary_rule_rel', 'struct_id', 'rule_id', string='Salary Rules')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create a recursive salary structure.'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, code=_("%s (copy)") % (self.code))
        return super(HrPayrollStructure, self).copy(default)

    def get_all_rules(self):
        """
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        """
        all_rules = []
        for struct in self:
            all_rules += struct.rule_ids._recursive_search_of_rules()
        return all_rules

    def _get_parent_structure(self):
        parent = self.mapped('parent_id')
        if parent:
            parent = parent._get_parent_structure()
        return parent + self


class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char(required=True)
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',
        string='Register Line', readonly=True)
    note = fields.Text(string='Description')


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    parent_id = fields.Many2one('hr.salary.rule.category', string='Parent',
        help="Linking a salary category to its parent is used only for the reporting purpose.")
    children_ids = fields.One2many('hr.salary.rule.category', 'parent_id', string='Children')
    note = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive hierarchy of Salary Rule Category.'))


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _order = 'sequence, id'
    _description = 'Salary Rule'

    name = fields.Char(required=True, translate=True)
    is_taxable = fields.Boolean("Is Taxable", default=False)
    code = fields.Char(required=True,
        help="The code of salary rules can be used as reference in computation of other rules. "
             "In that case, it is case sensitive.")
    sequence = fields.Integer(required=True, index=True, default=5,
        help='Use to arrange calculation sequence')
    quantity = fields.Char(default='1.0',
        help="It is used in computation for percentage and fixed amount. "
             "For e.g. A rule for Meal Voucher having fixed amount of "
             u"1€ per worked day can have its quantity defined in expression "
             "like worked_days.WORK100.number_of_days.")
    category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to false, it will allow you to hide the salary rule without removing it.")
    appears_on_payslip = fields.Boolean(string='Appears on Payslip', default=True,
        help="Used to display the salary rule on payslip.")
    parent_rule_id = fields.Many2one('hr.salary.rule', string='Parent Salary Rule', index=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('range', 'Range'),
        ('python', 'Python Expression')
    ], string="Condition Based on", default='none', required=True)
    condition_range = fields.Char(string='Range Based on', default='contract.wage',
        help='This will be used to compute the % fields values; in general it is on basic, '
             'but you can also use categories code fields in lowercase as a variable names '
             '(hra, ma, lta, etc.) and the variable basic.')
    condition_python = fields.Text(string='Python Condition', required=True,
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days
                    # inputs: object containing the computed inputs

                    # Note: returned value have to be set in the variable 'result'

                    result = rules.NET > categories.NET * 0.10''',
        help='Applied this rule for calculation if condition is true. You can specify condition like basic > 1000.')
    condition_range_min = fields.Float(string='Minimum Range', help="The minimum amount, applied for this rule.")
    condition_range_max = fields.Float(string='Maximum Range', help="The maximum amount, applied for this rule.")
    amount_select = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
        ('timeoff', 'Deduct timeoff'),
        ('employee_pension_contributions', 'Employee pension contributions'),
        ('employer_pension_contributions', 'Employer pension contributions'),
        ('income_tax', 'Income Tax'),
        ('total_taxable_income','Total taxable income'),
        ('taxable_travel_allowance', 'Taxable Travel Allowance'),

        ('total_deduction','Total deduction'),
        ('net_salary','Net salary')

    ], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
    amount_fix = fields.Float(string='Fixed Amount')
    amount_percentage = fields.Float(string='Percentage (%)',
        help='For example, enter 50.0 to apply a percentage of 50%')
    amount_python_compute = fields.Text(string='Python Code',
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable 'result'

                    result = contract.wage * 0.10''')
    amount_percentage_base = fields.Char(string='Percentage based on', help='result will be affected to a variable')
    child_ids = fields.One2many('hr.salary.rule', 'parent_rule_id', string='Child Salary Rule', copy=True)
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register',
        help="Eventual third party involved in the salary payment of the employees.")
    input_ids = fields.One2many('hr.rule.input', 'input_id', string='Inputs', copy=True)
    note = fields.Text(string='Description')

    @api.constrains('parent_rule_id')
    def _check_parent_rule_id(self):
        if not self._check_recursion(parent='parent_rule_id'):
            raise ValidationError(_('Error! You cannot create recursive hierarchy of Salary Rules.'))

    def _recursive_search_of_rules(self):
        """
        @return: returns a list of tuple (id, sequence) which are all the children of the passed rule_ids
        """
        children_rules = []
        for rule in self.filtered(lambda rule: rule.child_ids):
            children_rules += rule.child_ids._recursive_search_of_rules()
        return [(rule.id, rule.sequence) for rule in self] + children_rules

    #TODO should add some checks on the type of result (should be float)
    def _compute_rule(self, localdict, absent_day, code = '', salary_ids = []):
        """
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """


        self.ensure_one()
        if self.amount_select == 'fix':
            try:
                return self.amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'percentage':
            try:
                return (float(safe_eval(self.amount_percentage_base, localdict)),
                        float(safe_eval(self.quantity, localdict)),
                        self.amount_percentage)
            except:
                raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'taxable_travel_allowance':
            try:
                taxable_transport = float(safe_eval('contract.taxable_travel_allowance', localdict))
                return taxable_transport, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(
                    _('Wrong taxable transport allowance defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'timeoff':
                try:
                    working_set = localdict.get('worked_days', {})
                    work_key = 'WORK100'
                    days_of_work = working_set.dict
                    basic_salary = float(safe_eval('contract.wage', localdict))
                    number_of_working_days = 22
                    if work_key in days_of_work.keys():
                        number_of_working_days = days_of_work[work_key].number_of_days

                    # Calculate Daily Salary Rate
                    daily_salary_rate = basic_salary / number_of_working_days if number_of_working_days > 0 else 0

                    # Calculate Actual Monthly Basic Salary
                    if number_of_working_days == 0:
                        number_of_working_days = 1
                    actual_monthly_basic_salary = basic_salary - (absent_day * daily_salary_rate/number_of_working_days)

                    # Returning the result: (amount, quantity, rate)
                    return actual_monthly_basic_salary, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
                except Exception as ex:
                    raise UserError(_(
                        """
                        Error calculating timeoff deduction for salary rule %s (%s).
                        Here is the error received:
                        %s
                        """
                    ) % (self.name, self.code, repr(ex)))
        elif self.amount_select == 'employee_pension_contributions':
            try:
                basic_salary = float(safe_eval('contract.wage', localdict)) * 0.07
                return basic_salary, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating employee pension contributions for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))
        elif self.amount_select == 'employer_pension_contributions':
            try:
                basic_salary = float(safe_eval('contract.wage', localdict)) * 0.11
                return basic_salary, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating employer pension contributions for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))
        elif self.amount_select == 'total_taxable_income':
            try:
                total_taxable_income = 0
                for salary_rule in salary_ids:
                    # Assuming taxable earnings have a specific category or flag
                    if  salary_rule.is_taxable and salary_rule.code != code:
                        amount, qty, rate = salary_rule._compute_rule(localdict, absent_day, code, salary_ids)
                        total_taxable_income += amount

                return total_taxable_income, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating total taxable income for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))
        elif self.amount_select == 'income_tax':
            try:
                income_tax = 0
                total_taxable_income = 0
                for salary_rule in salary_ids:
                    # Assuming taxable earnings have a specific category or flag
                    if  salary_rule.is_taxable and salary_rule.code != code:
                        amount, qty, rate = salary_rule._compute_rule(localdict, absent_day, code, salary_ids)
                        total_taxable_income += amount
                if total_taxable_income >= 0 and total_taxable_income <= 600:
                    income_tax = total_taxable_income
                elif total_taxable_income >= 601 and total_taxable_income <= 1650:
                    income_tax = total_taxable_income * 0.1 - 60
                elif total_taxable_income >= 1651 and total_taxable_income <= 3200:
                    income_tax = total_taxable_income * 0.15 - 142.5
                elif total_taxable_income >= 3201 and total_taxable_income <= 5250:
                    income_tax = total_taxable_income * 0.2 - 302.5
                elif total_taxable_income >= 5251 and total_taxable_income <= 7800:
                    income_tax = total_taxable_income * 0.25 - 565
                elif total_taxable_income >= 7801 and total_taxable_income <= 10900:
                    income_tax = total_taxable_income * 0.3 - 955
                else:
                    income_tax = total_taxable_income * 0.35 - 1500
                return income_tax, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating income tax for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))

        elif self.amount_select == 'total_deduction':
            try:
                total_deduction = 0
                for salary_rule in salary_ids:
                    # Assuming taxable earnings have a specific category or flag
                    if  salary_rule.category_id.code == "DED" and salary_rule.code != code:
                        amount, qty, rate = salary_rule._compute_rule(localdict, absent_day, code, salary_ids)
                        total_deduction += amount

                return total_deduction, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating total deduction for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))
        elif self.amount_select == 'net_salary':
            try:
                total_deduction = 0
                total_taxable_income = 0
                for salary_rule in salary_ids:

                    # Assuming taxable earnings have a specific category or flag
                    if  salary_rule.category_id.code == "ALW" or salary_rule.category_id.code == "BASIC" :
                        amount, qty, rate = salary_rule._compute_rule(localdict, absent_day, code, salary_ids)
                        total_taxable_income += amount
                    if  salary_rule.category_id.code == "DED" and salary_rule.code != code:
                        amount, qty, rate = salary_rule._compute_rule(localdict, absent_day, code, salary_ids)
                        total_deduction  += amount

                return total_taxable_income - total_deduction, 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except Exception as ex:
                raise UserError(_(
                    """
                    Error calculating net salary for salary rule %s (%s).
                    Here is the error received:
                    %s
                    """
                ) % (self.name, self.code, repr(ex)))



        else:
                try:
                    safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                    return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
                except Exception as ex:
                    raise UserError(_(
                            """
                            Wrong python code defined for salary rule %s (%s).
                            Here is the error received:
                            %s
                            """
                        ) % (self.name, self.code, repr(ex)))

    def _satisfy_condition(self, localdict):
        """
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        """
        self.ensure_one()

        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'range':
            try:
                result = safe_eval(self.condition_range, localdict)
                return self.condition_range_min <= result and result <= self.condition_range_max or False
            except:
                raise UserError(_('Wrong range condition defined for salary rule %s (%s).') % (self.name, self.code))
        else:  # python code
            try:
                safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except Exception as ex:
                raise UserError(_(
                        """
                        Wrong python condition defined for salary rule %s (%s).
                        Here is the error received:
                        %s
                        """
                    ) % (self.name, self.code, repr(ex)))


class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _description = 'Salary Rule Input'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    input_id = fields.Many2one('hr.salary.rule', string='Salary Rule Input', required=True)
