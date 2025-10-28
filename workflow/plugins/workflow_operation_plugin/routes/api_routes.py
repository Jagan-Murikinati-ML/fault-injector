# workflow_operation_plugin/routes/api_routes.py
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
import os
import yaml
import json
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader


 
print("WorkflowOperationPlugin FastAPI app loaded")
 
app = FastAPI(title="WorkflowOperationPlugin", version="1.0.0")
 


print("WorkflowOperationPlugin FastAPI app loaded 21")
# Load templates once at startup
TEMPLATE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../templates_config.yaml")
try:
    with open(TEMPLATE_CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
        TEMPLATES = data.get("templates", [])
except Exception as e:
    TEMPLATES = []
    print(f"Failed to load templates_config.yaml: {e}")
 
print("WorkflowOperationPlugin FastAPI app loaded 32") 



# --- Configure Jinja template ---
TEMPLATE_FILE = "dag_template.yaml.j2"  # your template file
OUTPUT_DIR = "./generated_workflows"
env = Environment(
    loader=FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), "..")
    )
)

def load_json_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template JSON not found: {path}")
    with open(path, "r") as f:
        return json.load(f)
    


@app.post("/user_operation")
async def user_operation(request: Request, filename: str = Query(..., description="Name of the file to save")):
    try:
        # Read and parse the request body as JSON
        try:
            payload = await request.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
 
        # Ensure generated_workflows folder exists
        folder = "./generated_workflows"
        os.makedirs(folder, exist_ok=True)
 
        # Make filename safe and append .json
        safe_name = filename.lower().replace(" ", "_") + ".json"
        file_path = os.path.join(folder, safe_name)
 
        # Save JSON to file
        with open(file_path, "w") as f:
            json.dump(payload, f, indent=4)
 
        return JSONResponse(status_code=201, content={
            "message": "JSON saved successfully",
            "saved_file": file_path
        })
 
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class WorkflowRequest(BaseModel):
    dag_id: str
    task_id: str
    task_name: str
    experiment_json: str
    tags: list[str] = Field(default_factory=list, description="List of tags for the workflow")
    description: str = Field("", description="Description of the workflow")
    schedule: str = Field("", description="Schedule for the workflow")
 
@app.post("/workflow")
def generate_user_workflow(payload: WorkflowRequest):
    """
    Save incoming workflow payload as JSON file in ./generated_workflow
    with filename based on dag_id only.
    """
    try:
        # --- Validation ---
        data = payload.dict()
        required_fields = ["dag_id", "task_id", "task_name", "experiment_json"]
        for field in required_fields:
            if not data.get(field):
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        # --- Prepare file path (using dag_id only) ---
        safe_file_name = f"{data['dag_id'].lower().replace(' ', '_')}.json"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_path = os.path.join(OUTPUT_DIR, safe_file_name)
        # --- Write JSON to file ---
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return JSONResponse(
            status_code=201,
            content={
                "message": "Workflow JSON saved successfully",
                "file_path": file_path,
                "workflow_data": data
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
