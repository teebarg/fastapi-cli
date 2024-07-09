import typer
import os
from rich.prompt import Prompt

def generate_controller_file(controller_name: str, model_name: str):
    template = f"""from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlmodel import func, or_, select

import crud
from core.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)

from models.message import Message
from models.{model_name.lower()} import (
    {model_name},
    {model_name}Create,
    {model_name}Public,
    {model_name}sPublic,
    {model_name}Update,
)

# Create a router for {model_name.lower()}s
router = APIRouter()

@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model={model_name}sPublic,
)
def index(
    db: SessionDep,
    name: str = "",
    page: int = Query(default=1, gt=0),
    per_page: int = Query(default=20, le=100),
) -> Any:
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

    return {model_name}sPublic(
        data={model_name.lower()}s,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
    )


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model={model_name}Public
)
def create(*, db: SessionDep, {model_name.lower()}_in: {model_name}Create) -> Any:
    \"\"\"
    Create new {model_name.lower()}.
    \"\"\"
    {model_name.lower()} = crud.{model_name.lower()}.create(db=db, obj_in={model_name.lower()}_in)
    return {model_name.lower()}

@router.get("/{{id}}", response_model={model_name}Public)
def read(
    id: int, db: SessionDep, current_user: CurrentUser
) -> Any:
    \"\"\"
    Get a specific {model_name.lower()} by id.
    \"\"\"
    {model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
    if not {model_name.lower()}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {model_name.lower()}


@router.patch(
    "/{{id}}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model={model_name}Public,
)
def update(
    *,
    db: SessionDep,
    id: int,
    {model_name.lower()}_in: {model_name}Update,
) -> Any:
    \"\"\"
    Update a {model_name.lower()}.
    \"\"\"
    db_{model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
    if not db_{model_name.lower()}:
        raise HTTPException(
            status_code=404,
            detail="The {model_name.lower()} with this id does not exist in the system",
        )
    db_{model_name.lower()} = crud.{model_name.lower()}.update(db=db, db_obj=db_{model_name.lower()}, obj_in={model_name.lower()}_in)
    return db_{model_name.lower()}


@router.delete("/{{id}}", dependencies=[Depends(get_current_active_superuser)])
def delete(db: SessionDep, id: int) -> Message:
    \"\"\"
    Delete a {model_name.lower()}.
    \"\"\"
    {model_name.lower()} = crud.{model_name.lower()}.get(db=db, id=id)
    if not {model_name.lower()}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    crud.{model_name.lower()}.remove(db=db, id=id)
    return Message(message="{model_name} deleted successfully")
"""
    return template

def make_controller(name: str, model_name: str = None):
    """
    Create a new controller file.
    """
    if not name:
        print(f"No provided controller name (raw input = {name})")
        raise typer.Abort()
    if model_name is None:
        model_name = Prompt.ask("Enter the model name for this controller")
    controller_content = generate_controller_file(name, model_name=model_name.capitalize())
    
    os.makedirs("./api", exist_ok=True)
    
    with open(f"./api/{name.lower()}.py", "w") as f:
        f.write(controller_content)
    
    typer.echo(f"Controller file created: ./api/{name.lower()}.py")