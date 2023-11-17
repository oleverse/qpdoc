from pathlib import Path
from fastapi import APIRouter, Request, WebSocket
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, RedirectResponse
from app.conf.config import settings

# credential_paths = get_settings()

# templates = Jinja2Templates(directory=credentials_paths.path_templates)

router = APIRouter(tags=['pages'])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

app_title_main = 'QPDoc'
app_title = {
    '/profile': f'{app_title_main}',
    '/': f'{app_title_main}',
    '/chat': f'{app_title_main}',
    '/auth': f'{app_title_main}: login',
}


@router.get('/profile', response_class=HTMLResponse)
async def get_profile_page(request: Request):
    return templates.TemplateResponse('profile.html',
                                      {
                                          'request': request,
                                          'title': app_title[request['path']],
                                          'page_header': 'User profile'
                                      })


@router.get('/auth', response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse('auth.html', {
        'request': request,
        'title': app_title[request['path']]
    })


@router.get('/login', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse('auth.html', {
                                          'request': request,
                                          'title': app_title[request['path']]
                                      })


@router.get('/register')
async def get_register_page(request: Request):
    return templates.TemplateResponse('auth.html', {
                                          'request': request,
                                          'title': app_title[request['path']]
                                      })


@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Lorem ipsum dolor sit amet")


@router.get('/')
async def get_chat_page(request: Request):
    return templates.TemplateResponse('chat.html',
                                      {
                                          'request': request,
                                          'title': app_title[request['path']],
                                          'page_header': 'Query Processed Documents Chat',
                                          'ws_address': f'localhost:{settings.app_port}'
                                      })
