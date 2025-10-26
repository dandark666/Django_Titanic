#!/bin/bash
set -o errexit

echo "🚀 Iniciando despliegue..."
echo "🐍 Versión de Python:"
python --version

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "📁 Archivos estáticos..."
python manage.py collectstatic --noinput

echo "🗄️ Base de datos..."
python manage.py migrate

echo "🤖 Modelo ML..."
python manage.py shell -c "
import os
from titanic.views import train_and_save_model, MODEL_PATH
print(f'Ruta modelo: {MODEL_PATH}')
if not os.path.exists(MODEL_PATH):
    print('Entrenando modelo...')
    train_and_save_model()
    print('Modelo listo')
else:
    print('Modelo existe')
"

echo "✅ ¡Listo!"
