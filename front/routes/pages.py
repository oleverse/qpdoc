import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Request, WebSocket, HTTPException, status, UploadFile
from fastapi import Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.websockets import WebSocketDisconnect

import app.routes.upload_pdf
from app.conf.config import settings
from app.repository.user_files import get_user_files
from app.routes.llm_endpoint import llm_endpoint
from app.schemas.essential import UserModel

from app.services.auth import auth_service
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import User, RoleNames
from front.routes.forms import LoginForm, UserCreateForm
from app.routes import auth as auth_route
from psycopg2 import IntegrityError
from app.repository.users import user_exists

from app.repository.users import add_to_blacklist


router = APIRouter(tags=['pages'])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

app_title_main = 'QPDoc'


async def get_user_token(request: Request) -> str:
    if request and "access_token" in request.cookies:
        return request.cookies["access_token"].split()[1].strip()


async def get_logged_in_user(request: Request, db: Session) -> User:
    access_token = await get_user_token(request)
    try:
        logged_in_user = await auth_service.get_current_user(access_token, db)
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad access token!")
    else:
        return logged_in_user


@router.get('/profile', response_class=HTMLResponse)
async def get_profile_page(request: Request, db: Session = Depends(get_db)):
    try:
        logged_in_user = await get_logged_in_user(request, db)
    except HTTPException as http_ex:
        return RedirectResponse("/login",
                                headers={"Location": "/login"})
    else:
        return templates.TemplateResponse('profile.html',
                                          {
                                              'request': request,
                                              'title': app_title_main,
                                              'page_header': 'User profile',
                                              'user_name': logged_in_user.username,
                                              'user_email': logged_in_user.email,
                                          })


@router.get('/login', response_class=HTMLResponse)
async def get_login_page(request: Request, db: Session = Depends(get_db)):
    try:
        logged_in_user = await get_logged_in_user(request, db)
    except HTTPException as http_ex:
        return templates.TemplateResponse('auth.html',
                                          {
                                              'request': request,
                                              'page_header': 'Authorization',
                                              'title': app_title_main
                                          })
    return RedirectResponse("/chat",
                            headers={"Location": "/chat"})


@router.post("/login", response_class=HTMLResponse)
async def post_login_page(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/chat",
                                        status_code=status.HTTP_302_FOUND)
            login_result = await auth_route.login(response=response, body=form, db=db)
            form.__dict__.update(msg="Login Successful :)")

            logged_in_user = await auth_service.get_current_user(login_result["access_token"], db)
            response.headers["location"] = f"/chat"

            return response
        except HTTPException as http_ex:
            print('Error!')
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(http_ex.detail)
            return templates.TemplateResponse("auth.html", form.__dict__)
    return templates.TemplateResponse("/auth.html", form.__dict__)


@router.get('/register')
async def get_register_page(request: Request):
    return templates.TemplateResponse('auth.html',
                                      {
                                          'request': request,
                                          'title': app_title_main,
                                          'page_header': 'Registration',
                                      })


@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        try:
            await auth_route.register(request=request,
                                      background_tasks=background_tasks,
                                      body=UserModel(username=form.username, email=form.email, password=form.password),
                                      db=db)
            # default is post request, to use get request added status code 302
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("/auth.html", form.__dict__)

    return templates.TemplateResponse("/auth.html", form.__dict__)


@router.get('/chat')
async def get_chat_page(request: Request, db: Session = Depends(get_db)):
    try:
        logged_in_user = await get_logged_in_user(request, db)
    except HTTPException as http_ex:
        return RedirectResponse("/login",
                                headers={"Location": "/login"})
    else:
        user_files = await get_user_files(logged_in_user.id, db)
        return templates.TemplateResponse('chat.html',
                                          {
                                              'request': request,
                                              'title': app_title_main,
                                              'page_header': 'Query Processed Documents Chat',
                                              'ws_address': f'localhost:{settings.app_port}',
                                              'user': logged_in_user,
                                              'user_files': user_files
                                          })


@router.get('/')
async def get_main_page(request: Request, db: Session = Depends(get_db)):
    try:
        logged_in_user = await get_logged_in_user(request, db)
    except HTTPException as http_ex:
        return RedirectResponse("/login",
                                headers={"Location": "/login"})

    return RedirectResponse("/chat",
                            headers={"Location": "/chat"})


@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        # try:
        data = await websocket.receive_text()
        data = json.loads(data)

        if not await user_exists(data["user_id"], db):
            answer = {
                "code": 403,
                "message": "You are not authorized! Please log in."
            }
            await websocket.send_text(json.dumps(answer))
        else:
            try:
                llm_data = await llm_endpoint(data["message"], data["user_id"], data["file_id"], db)
                answer = {
                    "code": 200,
                    "message": llm_data["answer"]
                }
                await websocket.send_text(json.dumps(answer))
            except ValueError as error:
                answer = {
                    "code": 404,
                    "message": error
                }
                await websocket.send_text(json.dumps(answer))
        # except (RuntimeError, WebSocketDisconnect):
        #     await websocket.close()


@router.get("/logout_user")
async def logout_user(request: Request, db: Session = Depends(get_db)):
    access_token = await get_user_token(request)
    if not access_token:
        return RedirectResponse("/", headers={"Location": "/"})

    await add_to_blacklist(access_token, db)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    response.delete_cookie("access_token")
    response.headers["location"] = "/"

    return response


@router.post("/upload")
async def upload_files(request: Request, files: List[UploadFile], db: Session = Depends(get_db)):
    try:
        logged_in_user = await get_logged_in_user(request, db)
        await app.routes.upload_pdf.upload(files, logged_in_user.id, db)
    except HTTPException as http_ex:
        return RedirectResponse("/login",
                                headers={"Location": "/login"},
                                status_code=status.HTTP_302_FOUND)

    return RedirectResponse("/chat", headers={"Location": "/chat"}, status_code=status.HTTP_302_FOUND)
