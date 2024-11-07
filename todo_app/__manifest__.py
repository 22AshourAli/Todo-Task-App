{
    'name': "To-Do-App",
    'author': "Ashour Ali",
    'category': "todo",
    'version': "17.0.0.1.0",
    'depends': ['base', 'mail','hr_timesheet'
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/todo_task_view.xml',
        'views/todo_task_history_view.xml',
        'wizard/change_state_view.xml',
        'reports/todo_report.xml',
    ],
    'assets': {
        'web.assets_backend': ['todo_app/static/src/css/todo.css']
    },
    'application': True,
}
