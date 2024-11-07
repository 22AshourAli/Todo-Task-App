
from odoo import fields, models


class TodoTaskHistory(models.Model):
    _name = 'todo.task.history'
    _description = 'Todo Task History'

    user_id= fields.Many2one('res.users')
    todo_id = fields.Many2one('todo.task', string='Task Name')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()