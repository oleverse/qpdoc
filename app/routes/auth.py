from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User, RoleNames
from app.repository import users as repository_users
from app.schemas.essential import RequestEmail, UserStatusResponse, UserStatusChange
from app.schemas.essential import UserModel, UserResponse, TokenModel
from app.services.auth import auth_service
from app.services.send_email import send_confirmation_email


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserModel, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
     Register new user. If user with this email exists, raise 409 error

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dictionary with the user. Response with 201 status code.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    access_token = await auth_service.create_access_token(data={'sub': body.email}, expires_delta=86400)
    refresh_token = await auth_service.create_refresh_token(data={'sub': body.email})
    background_tasks.add_task(send_confirmation_email, new_user.email, new_user.username, str(request.base_url))
    return {'user': new_user, "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
            'detail': 'User successfully created'}


@router.post('/login', response_model=TokenModel)
async def login(response: Response, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.

    It takes the email and password of the user as input,
    checks if they are valid, and returns an access token.

    :param response: Response
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get a database session
    :return: Access and refresh tokens
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect login or password')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The user is deactivated.')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect login or password')

    access_token = await auth_service.create_access_token(data={'sub': user.email}, expires_delta=86400)
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})

    await repository_users.update_token(user, refresh_token, db)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=False)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_tokens(response: Response, credentials: HTTPAuthorizationCredentials = Security(security),
                         db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns a new access_token,
        refresh_token, and the type of token (bearer).

    :param response: Response
    :param credentials: HTTPAuthorizationCredentials: Get the token from the authorization header
    :param db: Session: Get a database session
    :return: A dict with the access_token, refresh_token and token type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    access_token = await auth_service.create_access_token(data={'sub': email}, expires_delta=86400)
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirm_email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes the token from the URL and uses it to get the user's email address.

    If user with this email doesn't exist raise 400 error.

    IF user is already confirmed, return message 'Your email has already been confirmed'

    :param token: str: Get the token from the url
    :param db: Session: Get a database session
    :return: A message that the email is already confirmed or a message that the email has been confirmed
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.confirm_email(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email_confirmation')
async def request_email_confirmation(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                                     db: Session = Depends(get_db)):
    """
    The request_email_confirmation function is used to send a confirmation email to the user.
    It takes in an email address and sends a confirmation link to that address.
    The function returns a message indicating whether the user's email has been confirmed.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Get a database session
    :return: A message to the user
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_confirmation_email, user.email, user.username, str(request.base_url))
    return {'message': 'Check your email for confirmation.'}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security),
                 db: Session = Depends(get_db)):
    """
    The logout function is used to log out a user.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Create a database session
    :return: A message that the user has been logged out
    """
    token = credentials.credentials

    # yet disable blacklisting...
    # await repository_users.add_to_blacklist(token, db)
    return {"message": 'User has been logged out.'}
