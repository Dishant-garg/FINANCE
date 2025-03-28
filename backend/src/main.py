from fastapi import FastAPI
from src.Routers import viz, story, chat, article

app = FastAPI(title='AIFinance', version='1.0.0')

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # For development - restrict in production
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
@app.get("/", description='Health check route')
async def health_check():
    return {"status": "healthy"}

# Include all routers
app.include_router(chat.router, prefix="/api")
app.include_router(story.router, prefix='/api')
app.include_router(viz.router, prefix="/api")
app.include_router(article.router, prefix="/api")
