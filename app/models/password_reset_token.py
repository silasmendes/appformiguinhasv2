import uuid
from datetime import datetime, timedelta
from app import db


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('reset_tokens', lazy='dynamic'))

    def __init__(self, user_id, expiration_hours=24):
        self.token = uuid.uuid4().hex + uuid.uuid4().hex  # 64-char hex token
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=expiration_hours)
        self.used = False

    @property
    def is_valid(self):
        """Check if the token is still valid (not used and not expired)."""
        return not self.used and datetime.utcnow() < self.expires_at

    def mark_used(self):
        """Mark the token as used."""
        self.used = True
