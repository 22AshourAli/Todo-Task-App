# from email.policy import default

from odoo import fields, api, models
from odoo.exceptions import ValidationError


class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Task Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default="Task", readonly=1)
    name = fields.Char(string='Task Name', required=True, default="Task ", tracking=True , translate=True)
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    description = fields.Text(tracking=True)
    assign_to_id = fields.Many2one('res.partner', string="Assigned to")
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ], default='new', tracking=True)
    active = fields.Boolean(default=True)
    is_late = fields.Boolean()

    estimated_time = fields.Float(string='Estimated Time (in hours)', default=0.0, tracking=True)

    total_time_spent = fields.Float(string='Total Time Spent (in hours)', compute='_compute_total_time_spent',
                                    store=True)

    timesheet_line_ids = fields.One2many('timesheet.line', 'task_id', string='Timesheet Lines')

    @api.depends('timesheet_line_ids.worked_hours')
    def _compute_total_time_spent(self):
        for task in self:
            total_time = sum(task.timesheet_line_ids.mapped('worked_hours'))
            task.total_time_spent = total_time

    @api.constrains('timesheet_line_ids')
    def _check_timesheet_limit(self):
        for task in self:
            if task.total_time_spent > task.estimated_time:
                raise ValidationError("Total time spent cannot exceed the estimated time for the task.")

    @api.model
    def action_add_timesheet(self, **kwargs):
        new_timesheet = self.env['timesheet.line'].create({
            'task_id': self.id,
            'worked_hours': 0.0,
            'date': fields.Date.today(),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.line',
            'view_mode': 'form',
            'view_id': self.env.ref('your_module_name.timesheet_line_form_view').id,
            'res_id': new_timesheet.id,
            'target': 'new',
        }

    def action_new(self):
        for rec in self:
            rec.create_history_record(rec.state, 'new')
            rec.state = 'new'

    def action_in_progress(self):
        for rec in self:
            rec.create_history_record(rec.state, 'in_progress')
            rec.state = 'in_progress'

    def action_completed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'completed')
            rec.state = 'completed'

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    def check_due_date(self):
        todo_ids = self.search([])
        for rec in todo_ids:
            if rec.due_date and rec.due_date < fields.Date.today():
                rec.is_late = True

    @api.model
    def create(self, vals):
        res = super(TodoTask, self).create(vals)
        if res.ref == 'Task':
            res.ref = self.env['ir.sequence'].next_by_code('todo_seq')
        return res

    def create_history_record(self, old_state, new_state,reason=""):
        for rec in self:
            rec.env['todo.task.history'].create({
                'user_id': rec.env.uid,
                'todo_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or "",
            })
    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('todo_app.change_state_wizard_action')
        action['context'] = {'default_todo_id':self.id}
        return action


class TimesheetLine(models.Model):
    _name = 'timesheet.line'
    _description = 'Timesheet Line'

    task_id = fields.Many2one('todo.task', string='Task', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    worked_hours = fields.Float(string='Worked Hours', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
