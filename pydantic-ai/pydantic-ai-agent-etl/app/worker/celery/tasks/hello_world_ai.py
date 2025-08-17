import logging

from core.celery import get_celery_app, AIPipelineTask

app = get_celery_app()


@app.register_task
class HelloWorldAI(AIPipelineTask):
    name = "HelloWorldAI_queue"

    def predict(self, name: str) -> str:
        logging.info("received input name: %s", name)
        return f"Hello {name}"

    def setup(self):
        logging.info("Hello World AI initiated")
