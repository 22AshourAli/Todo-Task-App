from odoo import fields, api, models

class ChangeState(models.TransientModel):
    _name = 'change.state'

    todo_id = fields.Many2one('todo.task', string="Task", required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
    ], default='new', required=True)
    reason = fields.Char(string="Reason", required=True)

    def action_confirm(self):
        if self.todo_id:
            old_state = self.todo_id.state
            self.todo_id.state = self.state
            self.todo_id.create_history_record(old_state, self.state, self.reason)
