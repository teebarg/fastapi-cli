import typer
import os
from rich.prompt import Prompt

def generate_controller_file(model_name: str):
    return f"""from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from typing import Annotated
from sqlmodel import func, or_, select

import crud
from core.deps import (
    CurrentUser,
    SessionDep,
    get_current_user,
)

from models.message import Message
from models.{model_name.lower()} import (
    {model_name},
    {model_name}Create,
    {model_name}Public,
    {model_name}s,
    {model_name}Update,
)
from core.logging import logger
from services.export import export, process_file, validate_file

# Create a router for {model_name.lower()}s
router = APIRouter()

@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model={model_name}s,
)
def index(
    db: SessionDep,
    name: str = "",
    page: int = Query(default=1, gt=0),
    per_page: int = Query(default=20, le=100),
) -> {model_name}s:
    \"\"\"
    Retrieve {model_name.lower()}s.
    \"\"\"
    query = {{"name": name}}
    filters = crud.{model_name.lower()}.build_query(query)

    count_statement = select(func.count()).select_from({model_name})
    if filters:
        count_statement = count_statement.where(or_(*filters))
    total_count = db.exec(count_statement).one()

    {model_name.lower()}s = crud.{model_name.lower()}.get_multi(
        db=db,
        filters=filters,
        per_page=per_page,
        offset=(page - 1) * per_page,
    )

    total_pages = (total_count // per_page) + (total_count % per_page > 0)

    return {model_name}s(
        {model_name}s={model_name.lower()}s,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
    )


@router.post(
    "/", dependencies=[Depends(get_current_user)], response_model={model_name}Public
)
def create(*, db: SessionDep, create_data: {model_name}Create) -> {model_name}Public:
    \"\"\"
    Create new {model_name.lower()}.
    \"\"\"
    {model_name.lower()} = crud.{model_name.lower()}.get_by_key(db=db, value=create_data.name)
    if {model_name.lower()}:
        raise HTTPException(
            status_code=400,
            detail="The {model_name.lower()} already exists in the system.",
        )

    {model_name.lower()} = crud.{model_name.lower()}.create(db=db, obj_in=create_data)
    return {model_name.lower()}


@router.get("/{{id}}", response_model={model_name}Public)
def read(
    id: int, db: SessionDep
) -> {model_name}Public:
    \"\"\"
    Get a specific {model_name.lower()} by id.
    \"\"\"
    {model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
    if not {model_name.lower()}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {model_name.lower()}


@router.patch(
    "/{{id}}",
    dependencies=[Depends(get_current_user)],
    response_model={model_name}Public,
)
def update(
    *,
    db: SessionDep,
    id: int,
    update_data: {model_name}Update,
) -> {model_name}Public:
    \"\"\"
    Update a {model_name.lower()}.
    \"\"\"
    db_{model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
    if not db_{model_name.lower()}:
        raise HTTPException(
            status_code=404,
            detail="{model_name} not found",
        )

    try:
        db_{model_name.lower()} = crud.{model_name.lower()}.update(db=db, db_obj=db_{model_name.lower()}, obj_in=update_data)
        return db_{model_name.lower()}
    except IntegrityError as e:
        logger.error(f"Error updating tag, str(e.orig.pgerror)")
        raise HTTPException(
            status_code=422, detail=str(e.orig.pgerror)
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e


@router.delete("/{{id}}", dependencies=[Depends(get_current_user)])
def delete(db: SessionDep, id: int) -> Message:
    \"\"\"
    Delete a {model_name.lower()}.
    \"\"\"
    try:
        {model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
        if not {model_name.lower()}:
            raise HTTPException(status_code=404, detail="{model_name} not found")
        crud.{model_name.lower()}.remove(db=db, id=id)
        return Message(message="{model_name} deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e


@router.post("/excel/{{task_id}}")
async def upload_{model_name.lower()}s(
    file: Annotated[UploadFile, File()],
    batch: Annotated[str, Form()],
    task_id: str,
    db: SessionDep,
    background_tasks: BackgroundTasks,
):
    await validate_file(file=file)

    contents = await file.read()
    background_tasks.add_task(process_file, contents, task_id, db, crud.{model_name.lower()}.bulk_upload)
    return {{"batch": batch, "message": "File upload started"}}


@router.post("/export")
async def export_{model_name.lower()}s(
    current_user: deps.CurrentUser, db: SessionDep, bucket: deps.Storage
):
    try:
        {model_name.lower()}s = db.exec(select({model_name}))
        file_url = await export(data={model_name.lower()}s, name="{model_name}", bucket=bucket, email=current_user.email)

        return {{"message": "Data Export successful", "file_url": file_url}}
    except Exception as e:
        logger.error(f"Export {model_name.lower()}s error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e)) from e

"""

def make_controller(model_name: str = None):
    """
    Create a new controller file.
    """
    if not model_name:
        model_name = Prompt.ask("Enter the model name for this controller")
    controller_content = generate_controller_file(model_name=model_name.capitalize())

    os.makedirs("./api", exist_ok=True)

    with open(f"./api/{model_name.lower()}.py", "w") as f:
        f.write(controller_content)

    typer.echo(f"Controller file created: ./api/{model_name.lower()}.py")