import os
import pandas as pd
import joblib
import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def entrenar_modelos():
    """
    Pipeline de Machine Learning que entrena y compara múltiples modelos
    cumpliendo con el estándar IEE 2.1.1 de la pauta.
    """
    logging.info("Iniciando entrenamiento de Modelos de Machine Learning...")

    # 1. Cargar el dataset procesado
    ruta_datos = os.path.join("data", "processed", "pacientes_ml.csv")
    df = pd.read_csv(ruta_datos)

    # Definir variables predictoras (X) y la variable a predecir (y)
    X = df[['edad', 'genero', 'peso_kg', 'estatura_cm']]
    y = df['clasificacion_imc']

    # 2. División de datos: 80% para entrenar, 20% para probar (Estratificado)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Creación del Preprocesador (Pipeline)
    # Justificación técnica: Escalamos los datos numéricos para mejorar la regresión
    # y usamos OneHotEncoder para transformar el texto (género) en ceros y unos.
    numeric_features = ['edad', 'peso_kg', 'estatura_cm']
    numeric_transformer = StandardScaler()

    categorical_features = ['genero']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # 4. Definición de Modelos a comparar
    logging.info("Configurando modelos: Regresión Logística vs Random Forest...")
    
    # Modelo 1: Random Forest (Algoritmo de Árboles de Decisión Múltiples)
    rf_pipeline = Pipeline(steps=[('preprocesador', preprocessor),
                                  ('clasificador', RandomForestClassifier(random_state=42))])
    
    # Modelo 2: Regresión Logística (Algoritmo Lineal Multiclase)
    lr_pipeline = Pipeline(steps=[('preprocesador', preprocessor),
                                  ('clasificador', LogisticRegression(max_iter=1000, random_state=42))])

    # 5. Configuración de hiperparámetros (Tuning) para Random Forest
    param_grid_rf = {
        'clasificador__n_estimators': [50, 100],  # Cantidad de árboles
        'clasificador__max_depth': [None, 10, 20] # Profundidad máxima
    }

    logging.info("Ejecutando GridSearchCV para optimizar Random Forest...")
    grid_rf = GridSearchCV(rf_pipeline, param_grid_rf, cv=3, scoring='accuracy', n_jobs=-1)
    grid_rf.fit(X_train, y_train)
    
    # Entrenar Regresión Logística (modelo base para comparar)
    lr_pipeline.fit(X_train, y_train)

    # 6. Evaluación y Comparación de Métricas
    pred_rf = grid_rf.predict(X_test)
    pred_lr = lr_pipeline.predict(X_test)

    acc_rf = accuracy_score(y_test, pred_rf)
    acc_lr = accuracy_score(y_test, pred_lr)

    print("\n" + "="*50)
    print("🏆 RESULTADOS DE LA COMPARACIÓN DE MODELOS 🏆")
    print("="*50)
    print(f"Precisión Global (Accuracy) - Regresión Logística: {acc_lr:.2f}")
    print(f"Precisión Global (Accuracy) - Random Forest:       {acc_rf:.2f}")
    print("\n[Justificación Técnica]: Random Forest suele manejar mejor las relaciones")
    print("no lineales complejas (como la proporción peso/estatura al cuadrado) frente a")
    print("modelos puramente lineales como la Regresión Logística.")
    print("-" * 50)
    
    print("\nReporte Detallado del Mejor Modelo (Random Forest):")
    print(classification_report(y_test, pred_rf))

    # 7. Guardar el mejor modelo para su uso en la API
    os.makedirs("models", exist_ok=True)
    ruta_modelo = os.path.join("models", "mejor_modelo_nhanes.pkl")
    
    # Guardamos el pipeline completo de Random Forest ya optimizado
    joblib.dump(grid_rf.best_estimator_, ruta_modelo)
    logging.info(f"Mejor modelo guardado con éxito en: {ruta_modelo}")

if __name__ == "__main__":
    entrenar_modelos()