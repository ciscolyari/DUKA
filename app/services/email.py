# from datetime import datetime, timedelta
# import random
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
# from pydantic import EmailStr

# # Weka mipangilio yako ya Email (SMTP)
# conf = ConnectionConfig(
#     MAIL_USERNAME="your_email@gmail.com",
#     MAIL_PASSWORD="your_email_password",
#     MAIL_FROM="your_email@gmail.com",
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
# )


# def generate_otp() -> str:
#   """Inatengeneza namba 6 za nasibu kwa ajili ya verification"""
#   return str(random.randint(100000, 999999))


# async def send_verification_email(email: EmailStr, code: str):
#   html = f"""
#     <p>Hellow!,</p>
#     <p>Your verification codes are:</p>
#     <h2>{code}</h2>
#     <p>This codes will expire within 10 minutes.</p>
#     """

#   message = MessageSchema(
#       subject="Verify your email",
#       recipients=[email],
#       body=html,
#       subtype=MessageType.html,
#   )

#   fm = FastMail(conf)
#   await fm.send_message(message)