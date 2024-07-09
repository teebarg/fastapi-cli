import typer
import os

def generate_crud_file(model_name: str):
    template = f"""from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlmodel import Session, select

from crud.base import CRUDBase
from models.{model_name.lower()} import {model_name}, {model_name}Create, {model_name}Update


class CRUD{model_name}(CRUDBase[{model_name}, {model_name}Create, {model_name}Update]):
    def create(self, db: Session, {model_name.lower()}_create: {model_name}Create) -> {model_name}:
        db_obj = {model_name}.model_validate(
            {model_name.lower()}_create,
            update={"key":1},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

{model_name.lower()} = CRUD{model_name}({model_name})
"""
    return template


def make_crud(model_name: str):
    """
    Create a new crud file.
    """
    if not model_name:
        print(f"No provided model name (raw input = {model_name})")
        raise typer.Abort()
    controller_content = generate_crud_file(model_name=model_name.capitalize())
    
    os.makedirs("./crud", exist_ok=True)
    
    with open(f"./crud/{model_name.lower()}.py", "w") as f:
        f.write(controller_content)
    
    typer.echo(f"Crud file created: ./crud/{model_name.lower()}.py")