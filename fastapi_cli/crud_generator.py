import typer
import os

def generate_crud_file(model_name: str):
    template = f"""
from typing import Any, Dict
from sqlmodel import Session, select

from core.utils import generate_slug
from crud.base import CRUDBase
from models.{model_name.lower()} import {model_name}, {model_name}Create, {model_name}Update

from core.logging import logger


class CRUD{model_name}(CRUDBase[{model_name}, {model_name}Create, {model_name}Update]):
    def create(self, db: Session, obj_in: {model_name}Create) -> {model_name}:
        db_obj = {model_name}.model_validate(
            obj_in,
            update={"slug:generate_slug(name=obj_in.name)"},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def bulk_upload(self, db: Session, *, records: list[Dict[str, Any]]) -> None:
        for {model_name.lower()} in records:
            try:
                if model := db.exec(
                    select({model_name}).where({model_name}.name == {model_name.lower()}.get("slug"))
                ).first():
                    model.sqlmodel_update({model_name.lower()})
                else:
                    model = {model_name}(**{model_name.lower()})
                    db.add(model)
                db.commit()
            except Exception as e:
                logger.error(e)

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