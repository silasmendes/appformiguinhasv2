import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def enviar_email_reset(usuario_email, token, reset_url):
    """
    Envia email de redefinição de senha usando SendGrid.

    Args:
        usuario_email: Email do destinatário
        token: Token de reset (para referência, não usado diretamente aqui)
        reset_url: URL absoluta para a página de reset de senha
    """
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_api_key:
        raise ValueError("SENDGRID_API_KEY não configurada no ambiente.")

    from_email = Email("silasmendes.dev@gmail.com", "Formiguinhas Solidárias")
    to_email = To(usuario_email)
    subject = "Redefinição de Senha - Formiguinhas Solidárias"

    html_content = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #333;">Formiguinhas Solidárias</h2>
        </div>

        <div style="background-color: #f8f9fa; border-radius: 12px; padding: 30px; border-left: 4px solid #81c784;">
            <h3 style="color: #333; margin-top: 0;">Redefinição de Senha</h3>

            <p style="color: #555; line-height: 1.6;">
                Olá,<br><br>
                Recebemos uma solicitação para redefinir a senha da sua conta.
                Clique no botão abaixo para criar uma nova senha:
            </p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background: linear-gradient(135deg, #007bff, #0056b3);
                          color: white;
                          padding: 14px 40px;
                          text-decoration: none;
                          border-radius: 8px;
                          font-weight: 600;
                          font-size: 16px;
                          display: inline-block;">
                    Redefinir Senha
                </a>
            </div>

            <p style="color: #555; line-height: 1.6; font-size: 14px;">
                Ou copie e cole o link abaixo no seu navegador:<br>
                <a href="{reset_url}" style="color: #007bff; word-break: break-all;">{reset_url}</a>
            </p>

            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">

            <p style="color: #888; font-size: 13px; line-height: 1.5;">
                ⚠️ Este link é válido por <strong>24 horas</strong>. Após esse período, será necessário solicitar um novo link.<br><br>
                Se você não solicitou a redefinição de senha, ignore este email. Sua senha permanecerá inalterada.
            </p>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #aaa; font-size: 12px;">
            <p>© Formiguinhas Solidárias — Este é um email automático, por favor não responda.</p>
        </div>
    </div>
    """

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=Content("text/html", html_content)
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return response.status_code in (200, 201, 202)
    except Exception as e:
        print(f"[ERROR] Falha ao enviar email de reset: {e}")
        return False
