# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.depends('expected_hours', 'consumed_hours')
    def _get_hours_left(self):
        for analytic_account in self:
            analytic_account.hours_left = \
                analytic_account.expected_hours - \
                analytic_account.consumed_hours

    @api.depends('line_ids', 'line_ids.unit_amount')
    def _get_consumed_hours(self):
        for analytic_account in self:
            # total quantity of timesheet lines on projects of this analytic account
            consumed_hours = 0.0
            projects = analytic_account.project_ids
            for line in analytic_account.line_ids:
                if line.project_id in projects:
                    consumed_hours += line.unit_amount
            analytic_account.consumed_hours = consumed_hours

    @api.depends('expected_turnover', 'expected_costs')
    def _get_expected_contribution(self):
        for analytic_account in self:
            analytic_account.expected_contribution = \
                analytic_account.expected_turnover - \
                analytic_account.expected_costs
            if analytic_account.expected_turnover != 0:
                analytic_account.expected_contribution_perc = \
                    100 * analytic_account.expected_contribution / \
                    analytic_account.expected_turnover
            else:
                analytic_account.expected_contribution_perc = 0.0

    @api.depends('line_ids', 'line_ids.amount')
    def _get_realized_data(self):
        for analytic_account in self:
            debit = 0.0
            credit = 0.0
            for line in analytic_account.line_ids:
                if line.account_id:
                    if line.amount > 0:
                        credit += line.amount
                    else:
                        debit += line.amount
                else:
                    debit += line.amount
            analytic_account.realized_turnover = credit
            analytic_account.realized_costs = - debit
            analytic_account.contribution = credit + debit
            if credit != 0:
                analytic_account.contribution_perc = \
                    100 * (credit + debit) / credit
            else:
                analytic_account.contribution_perc = 0.0

    @api.depends(
        'expected_turnover',
        'expected_costs',
        'realized_turnover',
        'realized_costs',
        'expected_contribution',
        'expected_contribution_perc',
        'contribution',
        'contribution_perc')
    def _get_budget_results(self):
        for analytic_account in self:
            analytic_account.budget_result_turnover = \
                analytic_account.realized_turnover - \
                analytic_account.expected_turnover
            analytic_account.budget_result_cost = \
                analytic_account.expected_costs - \
                analytic_account.realized_costs
            analytic_account.budget_result_contribution = \
                analytic_account.contribution - \
                analytic_account.expected_contribution
            analytic_account.budget_result_contribution_perc = 0.0
            if analytic_account.expected_contribution:
                analytic_account.budget_result_contribution_perc = \
                    100 * (analytic_account.contribution -
                           analytic_account.expected_contribution) / \
                    analytic_account.expected_contribution

    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.context_today
    )
    end_date = fields.Date(string='End Date')
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
        readonly=True
    )

    expected_hours = fields.Float(
        string='Expected Hours',
        digits=(16, 2)
    )
    consumed_hours = fields.Float(
        compute='_get_consumed_hours',
        store=True,
        string='Consumed Hours'
    )
    hours_left = fields.Float(
        compute='_get_hours_left',
        store=True,
        string='Hours Left'
    )

    expected_turnover = fields.Monetary(string='Turnover')
    expected_costs = fields.Monetary(string='Costs')
    expected_contribution = fields.Monetary(
        compute='_get_expected_contribution',
        store=True,
        string='Contribution'
    )
    expected_contribution_perc = fields.Float(
        compute='_get_expected_contribution',
        store=True,
        string='Contribution [%]'
    )

    realized_turnover = fields.Monetary(
        compute='_get_realized_data',
        store=True,
        string='Turnover'
    )
    realized_costs = fields.Monetary(
        compute='_get_realized_data',
        store=True,
        string='Costs'
    )
    contribution = fields.Monetary(
        compute='_get_realized_data',
        store=True,
        string='Contribution'
    )
    contribution_perc = fields.Float(
        compute='_get_realized_data',
        store=True,
        string='Contribution [%]'
    )

    budget_result_turnover = fields.Monetary(
        compute='_get_budget_results',
        store=True,
        string='Result Turnover'
    )
    budget_result_cost = fields.Monetary(
        compute='_get_budget_results',
        store=True,
        string='Result Costs'
    )
    budget_result_contribution = fields.Monetary(
        compute='_get_budget_results',
        store=True,
        string='Result Contribution'
    )
    budget_result_contribution_perc = fields.Float(
        compute='_get_budget_results',
        store=True,
        string='Result Contribution [%]')
