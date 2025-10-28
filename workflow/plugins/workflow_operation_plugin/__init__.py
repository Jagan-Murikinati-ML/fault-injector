from airflow.plugins_manager import AirflowPlugin
from workflow_operation_plugin.routes.api_routes import app
print("Hello loaded from outer init")
class WorkflowOperationPlugin(AirflowPlugin):
    name = "workflow_operation_plugin"
    fastapi_apps = [
        {"app": app, "url_prefix": "/myapi", "name": "WorkflowOperationPlugin"}
    ]