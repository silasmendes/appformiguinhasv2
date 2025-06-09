from app.routes.familia import bp as familia_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
