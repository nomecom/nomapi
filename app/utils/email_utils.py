def send_verification_email(domain: str, verification_token: str):
    subject = "Verify Your Account"
    verification_url = f"{domain}/verify?token={verification_token}"
    
    body = f"""Please verify your account by clicking this link:
    {verification_url}"""
    
    html_body = f"""
    <h1>Verify Your Account</h1>
    <p>Click <a href="{verification_url}">here</a> to verify.</p>
    <p>Or copy this link: {verification_url}</p>
    """
    return subject, body, html_body

def send_password_reset_email(domain: str, reset_token: str):
    subject = "Reset Your Password"
    reset_url = f"{domain}/reset-password?token={reset_token}"
    
    body = f"""You requested to reset your password. Please click this link:
    {reset_url}
    
    This link will expire in 1 hour. If you didn't request this, please ignore this email."""
    
    html_body = f"""
    <h1>Reset Your Password</h1>
    <p>Click <a href="{reset_url}">here</a> to reset your password.</p>
    <p>Or copy this link: {reset_url}</p>
    <p><strong>This link will expire in 1 hour.</strong></p>
    <p>If you didn't request this password reset, please ignore this email.</p>
    """
    return subject, body, html_body