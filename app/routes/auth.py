from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token,
    PasswordResetRequest, PasswordReset
)
from app.utils.security import (
    verify_password, get_password_hash, create_access_token,
    generate_password_reset_token, get_password_reset_token_expiry
)
from app.utils.email import send_password_reset_email
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    # メールアドレスの重複チェック
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )

    # 店舗IDの重複チェック
    if db.query(User).filter(User.store_id == user_data.store_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この店舗IDは既に使用されています"
        )

    # 新規ユーザーの作成
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        store_id=user_data.store_id,
        email=user_data.email,
        store_name=user_data.store_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """ログイン"""
    # ユーザーの検索
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています"
        )

    # アクセストークンの生成
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password-reset-request", status_code=status.HTTP_200_OK)
def request_password_reset(request_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """パスワードリセットリクエスト"""
    user = db.query(User).filter(User.email == request_data.email).first()

    # セキュリティのため、ユーザーが存在しない場合も同じレスポンスを返す
    if not user:
        return {"message": "パスワードリセットメールを送信しました(該当するアカウントが存在する場合)"}

    # トークンの生成
    reset_token = generate_password_reset_token()
    expires_at = get_password_reset_token_expiry()

    # 既存の未使用トークンを無効化
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})

    # 新しいトークンをDBに保存
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    db.add(token_record)
    db.commit()

    # メール送信
    send_password_reset_email(user.email, reset_token, user.store_name)

    return {"message": "パスワードリセットメールを送信しました"}


@router.post("/password-reset", status_code=status.HTTP_200_OK)
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """パスワードリセット"""
    # トークンの検証
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なトークンです"
        )

    if not token_record.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="トークンの有効期限が切れているか、既に使用されています"
        )

    # パスワードの更新
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    user.hashed_password = get_password_hash(reset_data.new_password)
    token_record.is_used = True

    db.commit()

    return {"message": "パスワードが正常にリセットされました"}
