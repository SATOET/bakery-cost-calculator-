import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_password_reset_email(to_email: str, reset_token: str, store_name: str):
    """パスワードリセットメールを送信"""
    if not settings.smtp_user or not settings.smtp_password:
        print("Warning: SMTP settings not configured. Email not sent.")
        return False

    # リセットURL (実際のURLに変更してください)
    reset_url = f"http://localhost:8000/reset-password?token={reset_token}"

    # メール本文
    subject = f"{settings.app_name} - パスワードリセットのご案内"
    html_body = f"""
    <html>
        <body>
            <h2>{store_name}様</h2>
            <p>パスワードリセットのリクエストを受け付けました。</p>
            <p>下記のリンクをクリックして、新しいパスワードを設定してください。</p>
            <p><a href="{reset_url}">パスワードをリセット</a></p>
            <p>このリンクは24時間有効です。</p>
            <p>もしこのリクエストに心当たりがない場合は、このメールを無視してください。</p>
            <br>
            <p>{settings.app_name}</p>
        </body>
    </html>
    """

    text_body = f"""
    {store_name}様

    パスワードリセットのリクエストを受け付けました。

    下記のURLにアクセスして、新しいパスワードを設定してください。
    {reset_url}

    このリンクは24時間有効です。

    もしこのリクエストに心当たりがない場合は、このメールを無視してください。

    {settings.app_name}
    """

    try:
        # メッセージの作成
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.email_from
        message["To"] = to_email

        # テキストとHTMLパートを追加
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)

        # SMTPサーバーに接続して送信
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
