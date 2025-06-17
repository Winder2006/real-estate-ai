import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import joblib
import os

class PropertyPricePredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_columns = None
        self.target_column = 'Sale_price'
        
    def prepare_features(self, df):
        """Prepare features for the model"""
        # Select relevant features
        features = [
            'FinishedSqft', 'Bedrooms', 'Bathrooms',
            'nbhd', 'PropertyType', 'zipcode'
        ]
        
        # Create feature matrix
        X = df[features].copy()
        
        return X
    
    def create_preprocessor(self, X):
        """Create preprocessing pipeline"""
        numeric_features = ['FinishedSqft', 'Bedrooms', 'Bathrooms']
        categorical_features = ['nbhd', 'PropertyType', 'zipcode']
        
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),  # Fill missing numeric values with median
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),  # Fill missing categorical values with most frequent
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return preprocessor
    
    def train(self, df):
        """Train the price prediction model"""
        # Prepare features
        X = self.prepare_features(df)
        y = df[self.target_column]
        
        # Create and fit preprocessor
        self.preprocessor = self.create_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=0.2, random_state=42
        )
        
        # Initialize and train model
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"MAE: ${mae:,.2f}")
        print(f"RMSE: ${rmse:,.2f}")
        print(f"R2 Score: {r2:.3f}")
        
        # Print feature importance
        feature_names = (self.preprocessor.named_transformers_['num'].get_feature_names_out().tolist() +
                        self.preprocessor.named_transformers_['cat'].get_feature_names_out().tolist())
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return mae, rmse, r2
    
    def predict(self, property_data):
        """Predict price for a single property"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert single property data to DataFrame
        X = pd.DataFrame([property_data])
        
        # Process features
        X_processed = self.preprocessor.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_processed)[0]
        
        return prediction
    
    def save_model(self, path='models/price_predictor.joblib'):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save!")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'preprocessor': self.preprocessor
        }, path)
    
    def load_model(self, path='models/price_predictor.joblib'):
        """Load a trained model"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"No model found at {path}")
        
        saved_data = joblib.load(path)
        self.model = saved_data['model']
        self.preprocessor = saved_data['preprocessor']

class RentPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_columns = None
        self.target_column = 'rent'
        self.mae = None  # Store MAE for confidence intervals
        
    def prepare_features(self, df):
        """Prepare features for the rent prediction model"""
        # Select relevant features
        features = [
            'FinishedSqft', 'Bedrooms', 'Bathrooms',
            'nbhd', 'PropertyType', 'zipcode',
            'BedBath', 'SqftPerBed', 'LogSqft', 'SaleMonth'
        ]
        features = [col for col in features if col in df.columns]
        
        # Create feature matrix
        X = df[features].copy()
        
        return X
    
    def create_preprocessor(self, X):
        """Create preprocessing pipeline for rent prediction"""
        numeric_features = [col for col in ['FinishedSqft', 'Bedrooms', 'Bathrooms', 'BedBath', 'SqftPerBed', 'LogSqft', 'SaleMonth'] if col in X.columns]
        categorical_features = [col for col in ['nbhd', 'PropertyType', 'zipcode'] if col in X.columns]
        
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return preprocessor
    
    def train(self, df):
        """Train the rent prediction model"""
        # Prepare features
        X = self.prepare_features(df)
        y = df[self.target_column]
        
        # Create and fit preprocessor
        self.preprocessor = self.create_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=0.2, random_state=42
        )
        
        # Initialize and train model
        self.model = GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=12,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        self.mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"Rent Model Performance:")
        print(f"MAE: ${self.mae:,.2f}")
        print(f"RMSE: ${rmse:,.2f}")
        print(f"R2 Score: {r2:.3f}")
        
        # Print feature importance
        feature_names = (self.preprocessor.named_transformers_['num'].get_feature_names_out().tolist() +
                        self.preprocessor.named_transformers_['cat'].get_feature_names_out().tolist())
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return self.mae, rmse, r2
    
    def predict(self, property_data):
        """Predict rent for a single property"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert single property data to DataFrame
        X = pd.DataFrame([property_data])
        
        # Process features
        X_processed = self.preprocessor.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_processed)[0]
        
        return prediction
    
    def predict_with_range(self, property_data):
        """Predict rent with confidence interval based on MAE"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        prediction = self.predict(property_data)
        
        # Use MAE to create a confidence interval
        if self.mae is None:
            self.mae = 289.24  # Default MAE from training if not available
        
        lower_bound = max(0, prediction - self.mae)
        upper_bound = prediction + self.mae
        
        return {
            'predicted_rent': prediction,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence_range': self.mae
        }
    
    def save_model(self, path='models/rent_predictor.joblib'):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save!")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'preprocessor': self.preprocessor,
            'mae': self.mae
        }, path)
    
    def load_model(self, path='models/rent_predictor.joblib'):
        """Load a trained model"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"No model found at {path}")
        
        saved_data = joblib.load(path)
        self.model = saved_data['model']
        self.preprocessor = saved_data['preprocessor']
        self.mae = saved_data.get('mae', 289.24)  # Use default MAE if not saved 