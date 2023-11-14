from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, RedirectResponse

# from conf.config import get_settings

# credential_paths = get_settings()

# templates = Jinja2Templates(directory=credentials_paths.path_templates)

router = APIRouter(tags=['pages'])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@router.get('/profile', response_class=HTMLResponse)
def get_profile_page(request: Request):
    return templates.TemplateResponse('profile.html', {'request': request})


@router.get('/login', response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@router.get('/register')
def get_register_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


# @router.get('/')
# def get_index_page(request: Request):
#     return templates.TemplateResponse('login.html', {'request': request})


@router.get('/')
def get_chat_page(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})