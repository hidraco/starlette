from starlette.background import BackgroundTask, BackgroundTasks
from starlette.responses import Response


def test_async_task(test_client_factory):
    TASK_COMPLETE = False

    async def async_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(async_task)

    async def app(scope, receive, send):
        response = Response("task initiated", media_type="text/plain", background=task)
        await response(scope, receive, send)

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "task initiated"
    assert TASK_COMPLETE


def test_sync_task(test_client_factory):
    TASK_COMPLETE = False

    def sync_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(sync_task)

    async def app(scope, receive, send):
        response = Response("task initiated", media_type="text/plain", background=task)
        await response(scope, receive, send)

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "task initiated"
    assert TASK_COMPLETE


def test_multiple_tasks(test_client_factory):
    TASK_COUNTER = 0

    def increment(amount):
        nonlocal TASK_COUNTER
        TASK_COUNTER += amount

    async def app(scope, receive, send):
        tasks = BackgroundTasks()
        tasks.add_task(increment, amount=1)
        tasks.add_task(increment, amount=2)
        tasks.add_task(increment, amount=3)
        response = Response(
            "tasks initiated", media_type="text/plain", background=tasks
        )
        await response(scope, receive, send)

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "tasks initiated"
    assert TASK_COUNTER == 1 + 2 + 3
