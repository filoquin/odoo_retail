from odoo import fields, models, api
from datetime import datetime, timedelta


DAYS = [('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')]

DAYS_NAMES = {'0': 'Lunes',
              '1': 'Martes',
              '2': 'Miercoles',
              '3': 'Jueves',
              '4': 'Viernes',
              '5': 'Sabado',
              '6': 'Domingo'}


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


class stock_supply_rule(models.Model):
    _name = 'stock.supply.rule'
    _description = 'warehouse supply rule'

    name = fields.Char(
        compute="_compute_name",
        store=True
    )

    orig_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='From Warehouse',
        required=True
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='To Warehouse',
        required=True
    )
    route_ids = fields.Many2many(
        'stock.location.route', string='Preferred Routes',
        help="Apply specific route(s) for the replenishment instead of product's default routes.",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    domain = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    request_day = fields.Selection(
        DAYS,
        string='Limit request day',
        required=True,
        select=True
    )
    request_hour = fields.Float(
        string='Limit request hour',
    )

    recept_day = fields.Selection(
        DAYS,
        string='Limit recept day',
        required=True,
        select=True
    )
    recept_hour = fields.Float(
        string='Limit recept hour',
    )

    preparation_day = fields.Selection(
        DAYS,
        string='Limit preparation day',
        required=True,
        select=True
    )
    preparation_hour = fields.Float(
        string='Limit preparation hour',
    )
    active = fields.Boolean(
        default=True
    )



    def make_calendar(self):
        date_from = datetime.now()
        for rule in self:
            recept_day = next_weekday(date_from, int(
                rule.recept_day)).replace(hour=0, second=0, microsecond=0, minute=0) + timedelta(hours=(rule.recept_hour + 3.0))
            exists = self.env['stock.supply.calendar'].search_count([
                ('rule_id', '=', rule.id),
                ('deadline', '=', fields.Datetime.to_string(recept_day))])
            if not exists:
                request_day = next_weekday(date_from, int(
                    rule.request_day)).replace(hour=0, second=0, microsecond=0, minute=0) + timedelta(hours=(rule.request_hour + 3.0))
                preparation_day = next_weekday(date_from, int(
                    rule.preparation_day)).replace(hour=0, second=0, microsecond=0, minute=0) + timedelta(hours=(rule.preparation_hour + 3.0))

                calendar = {}

                calendar['deadline'] = recept_day
                calendar['request_deadline'] = request_day
                calendar['preparation_deadline'] = preparation_day
                calendar['rule_id'] = rule.id
                calendar['company_id'] = rule.company_id.id

                calendar_id = self.env[
                    'stock.supply.calendar'].create(calendar)
                # calendar_id.action_budget_lines()
                # calendar_id.compute_used_amount()

    @api.model
    def cron_create_calendar(self):
        self.search([]).make_calendar()

    @api.depends('warehouse_id', 'recept_day')
    def _compute_name(self):
        for rule in self:
            rule.name = '%s %s ' % (
                DAYS_NAMES[rule.recept_day],  rule.warehouse_id.name)
