from .job_processor import JobExecutor
from .task_executor import TaskExecutor


def to_job_executor(task_executor: TaskExecutor) -> JobExecutor:
    return lambda doc: task_executor(tasks=doc.get('tasks'), vars=doc.get('vars'))
