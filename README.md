# FastAPI CLI

A command-line interface for generating models and controllers in FastAPI projects.

## Installation

```bash
pip install git+https://github.com/teebarg/fastapi-cli.git
```

## Usage

After installation, you can use the `fastapi-cli` command in your terminal:

```bash
fastapi-cli make-model User
fastapi-cli make-controller UserController
fastapi-cli make-crud User
fastapi-cli make:all User
```

## Commands

- `make-model`: Create a new model file
- `make-controller`: Create a new controller file
- `make-crud` : Create a new crud file
- `make:all`: Create both model and controller files

## Help

```bash
fastapi-cli make-model --help
```

## License

This project is licensed under the MIT License.