def send_verification_email(verification_token: str):
    subject = "Verify Your Account"
    verification_url = f"http://localhost:5173/verify?token={verification_token}"
    
    body = f"""Please verify your account by clicking this link:
    {verification_url}"""
    
    html_body = f"""
    <h1>Verify Your Account</h1>
    <p>Click <a href="{verification_url}">here</a> to verify.</p>
    <p>Or copy this link: {verification_url}</p>
    """
    return subject, body, html_body