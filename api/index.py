from app import create_app

app = create_app()

# entry point for Vercel
def handler(request):
    return app(request)
