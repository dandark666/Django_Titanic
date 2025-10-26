import os
import joblib
import pandas as pd
import numpy as np
import seaborn as sns
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_PATH = os.path.join(settings.BASE_DIR, 'titanic_model.joblib')

def train_and_save_model():
    """Entrena el modelo con datos del Titanic"""
    try:
        print("🔍 Cargando dataset Titanic...")
        df = sns.load_dataset('titanic')
        
        print("🧹 Limpiando datos...")
        df = df[['survived', 'pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']]
        df = df.dropna(subset=['embarked'])
        
        X = df.drop('survived', axis=1)
        y = df['survived']
        
        print("⚙️ Configurando preprocesamiento...")
        num_cols = ['age', 'sibsp', 'parch', 'fare']
        cat_cols = ['pclass', 'sex', 'embarked']
        
        num_transformer = make_pipeline(
            SimpleImputer(strategy='median'), 
            StandardScaler()
        )
        cat_transformer = make_pipeline(
            SimpleImputer(strategy='most_frequent'),
            OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        )
        
        preprocessor = ColumnTransformer([
            ('num', num_transformer, num_cols),
            ('cat', cat_transformer, cat_cols)
        ])
        
        print("🤖 Creando y entrenando modelo...")
        model = make_pipeline(preprocessor, LogisticRegression(max_iter=1000, random_state=42))
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"✅ Modelo entrenado. Precisión: {acc:.3f}")
        
        joblib.dump(model, MODEL_PATH)
        print(f"💾 Modelo guardado en: {MODEL_PATH}")
        return model
        
    except Exception as e:
        print(f"❌ Error entrenando modelo: {e}")
        return None

def load_model():
    """Carga el modelo si existe, si no lo entrena"""
    try:
        if os.path.exists(MODEL_PATH):
            print(f"📂 Cargando modelo existente desde: {MODEL_PATH}")
            return joblib.load(MODEL_PATH)
        else:
            print("🆕 No existe modelo. Entrenando nuevo modelo...")
            return train_and_save_model()
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return None

_model = None

def get_model():
    """Obtiene el modelo (carga lazy)"""
    global _model
    if _model is None:
        _model = load_model()
    return _model

def index(request):
    """Página principal con el formulario"""
    return render(request, 'titanic/index.html')

@csrf_exempt
def predict(request):
    """Recibe datos del formulario y devuelve predicción"""
    try:
        model = get_model()
        if model is None:
            return JsonResponse({'error': 'El modelo no está disponible. Por favor, intenta recargar la página.'}, status=500)
        
        data = request.POST
        
        # Crear datos de entrada con valores por defecto
        input_data = {
            'pclass': [int(data.get('pclass', 3))],
            'sex': [data.get('sex', 'male')],
            'age': [float(data.get('age', 30))],
            'sibsp': [int(data.get('sibsp', 0))],
            'parch': [int(data.get('parch', 0))],
            'fare': [float(data.get('fare', 10))],
            'embarked': [data.get('embarked', 'S')]
        }
        
        X_new = pd.DataFrame(input_data)
        
        prediction = model.predict(X_new)[0]
        probability = model.predict_proba(X_new)[0][1]
        
        return JsonResponse({
            'survived': int(prediction),
            'probability_survive': float(probability)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)