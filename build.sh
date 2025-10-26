#!/bin/bash
set -o errexit

echo "🚀 Iniciando proceso de despliegue..."
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🗄️ Aplicando migraciones de base de datos..."
python manage.py migrate

echo "🤖 Verificando modelo de Machine Learning..."
python manage.py shell -c "
import os
from titanic.views import train_and_save_model, MODEL_PATH

print(f'📂 Ruta del modelo: {MODEL_PATH}')

if os.path.exists(MODEL_PATH):
    print('✅ Modelo ya existe, no es necesario entrenar')
else:
    print('🆕 Entrenando nuevo modelo...')
    model = train_and_save_model()
    if model is not None:
        print('✅ Modelo entrenado exitosamente')
    else:
        print('❌ Error: No se pudo entrenar el modelo')
"

echo "✅ ¡Despliegue completado con éxito!"