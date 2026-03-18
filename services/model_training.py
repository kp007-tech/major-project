import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_all_models(X, y):
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    }

    results = {}

    for name, model in models.items():
        model.fit(X, y)
        preds = model.predict(X)

        mse = mean_squared_error(y, preds)

        results[name] = {
            "model": model,
            "mae": float(mean_absolute_error(y, preds)),
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "r2": float(r2_score(y, preds)),
        }

    return results


def get_best_model(results):
    best_name = max(results, key=lambda k: results[k]["r2"])
    return best_name, results[best_name]