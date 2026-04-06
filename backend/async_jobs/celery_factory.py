from celery import Celery, Task
from celery.schedules import crontab

def celery_init_app(app) -> Celery:

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
            include=['async_jobs.tasks'], 
            
            beat_schedule={
                'monthly-student-reports': {
                    'task': 'send_monthly_student_reports',
                    'schedule': crontab(day_of_month='1', hour=9, minute=0),
                },
                'monthly-company-reports': {
                    'task': 'send_monthly_company_reports',
                    'schedule': crontab(day_of_month='1', hour=9, minute=0),
                },
                'monthly-admin-reports': {
                    'task': 'send_monthly_admin_reports',
                    'schedule': crontab(day_of_month='1', hour=9, minute=0),
                },
            }
        ),
    )

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            # for tasks access to sql alchemy and flask integration
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app