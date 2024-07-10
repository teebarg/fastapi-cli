import typer
import os
from typing import List, Dict
from rich.prompt import Prompt

def generate_model_file(model_name: str, fields: List[Dict[str, str]]):
    template = f"""from typing import Optional
from sqlmodel import Field, SQLModel
from models.base import BaseModel

class {model_name}Base(BaseModel):
{generate_fields(fields)}

class {model_name}Create({model_name}Base):
    pass

class {model_name}Update({model_name}Base):
    pass

class {model_name}(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class {model_name}Public({model_name}Base):
    id: int

class {model_name}s(SQLModel):
    {model_name.lower()}s: list[{model_name}Public]
    page: int
    per_page: int
    total_count: int
    total_pages: int
"""
    return template

def generate_fields(fields):
    field_strings = []
    for field in fields:
        property_string = ", ".join(f"{k}={v}" for k, v in field['properties'].items())
        field_strings.append(f"    {field['name']}: {field['type']} = Field({property_string})")
    return "\n".join(field_strings)

def prompt_for_fields() -> List[Dict[str, str]]:
    fields = []
    while True:
        field_name = Prompt.ask("Enter field name (or press Enter to finish)")
        if not field_name:
            break

        field_type = Prompt.ask(f"Enter type for {field_name}", choices=["int", "str", "bool", "EmailStr"], default="str")

        field_properties = {}
        while True:
            property = Prompt.ask(f"Enter property for {field_name} (e.g., default=None, unique=True, index=True, or press Enter to finish)")
            if not property:
                break
            try:
                key, value = property.split('=')
                field_properties[key.strip()] = value.strip()
            except Exception as e:
                print(f"{e}")

        fields.append({"name": field_name, "type": field_type, "properties": field_properties})
    return fields

def make_model(name: str):
    """
    Create a new model file.
    """
    if not name:
        print(f"No provided model name (raw input = {name})")
        raise typer.Abort()
    fields = prompt_for_fields()
    model_content = generate_model_file(name, fields)

    os.makedirs("./models", exist_ok=True)

    with open(f"./models/{name.lower()}.py", "w") as f:
        f.write(model_content)

    typer.echo(f"Model file created: ./models/{name.lower()}.py")