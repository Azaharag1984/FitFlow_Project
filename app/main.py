from fastapi import FastAPI
from connection.database import connect_to_mongo, close_mongo_connection # Importa tus funciones de conexión
from routes import usuarios, registros, logros, ejercicios, chatbot # Tus routers

app = FastAPI()

# Eventos de startup/shutdown para manejar la conexión a la DB
@app.on_event("startup")
async def startup_db_client():
    print("Conectando a la base de datos MongoDB...")
    await connect_to_mongo() # ¡CORREGIDO: Añadido await!

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Cerrando conexión a la base de datos MongoDB...")
    await close_mongo_connection() # ¡CORREGIDO: Añadido await si no estaba!

# Incluir los routers
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(registros.router, prefix="/registros", tags=["Registros de Entrenamiento"])
app.include_router(logros.router, prefix="/logros", tags=["Logros"])
app.include_router(ejercicios.router, prefix="/ejercicios", tags=["Ejercicios"])
app.include_router(chatbot.router, prefix="/conversaciones", tags=["Conversaciones y Chatbot"])

# Puedes añadir una ruta raíz de ejemplo si lo deseas
@app.get("/")
async def read_root():
    return {"message": "Welcome to FitFlow FastAPI Backend!"}
    