"""
FermaGen AI - Logistic Growth Estimator Pipeline
Utilizes non-linear least squares optimization (scipy.optimize) acting as a regression
model mapping cellular division over duration cycles.
"""
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score
import warnings

warnings.filterwarnings("ignore")

class LogisticRegressionEstimator:
    """
    ML Data Science Class specifically designed to learn the parameters (L, k, x0) 
    of the biological saturation limit tracking the active fermentation phase duration.
    """
    
    def __init__(self):
        # Learned hyperparameters
        self.L = None   # Carrying capacity / Maximum curve limit
        self.k = None   # Growth Rate steepness
        self.x0 = None  # Sigmoid midpoint
        
        self.performance_metrics = {}
        
    @staticmethod
    def _logistic_function(x, L, k, x0):
        """Standard bounded sigmoid function form mapping biology to data."""
        return L / (1 + np.exp(-k * (x - x0)))

    def _generate_synthetic_biomass(self, limit: float, rate: float, samples=1000):
        """Simulate real-world lab extraction validation arrays."""
        time_x = np.linspace(0, 120, samples) # 0 to 120 hours
        
        # Generate true curve
        y_true = self._logistic_function(time_x, limit, rate, 24.0)
        
        # Add random sensor noise (simulating empirical lab samples)
        noise = np.random.normal(0, limit * 0.05, size=samples)
        y_noisy = y_true + noise
        
        return time_x, y_noisy

    def fit_growth_profile(self, known_limit: float, known_growth_rate: float):
        """
        Executes curve fitting (training phase) to lock optimal model weights 
        extracting the coefficients for the microbe parameters.
        """
        X_train, y_train = self._generate_synthetic_biomass(known_limit, known_growth_rate)
        
        # Initial guess parameters (L_guess, k_guess, x0_guess)
        p0 = [max(y_train), 0.5, np.median(X_train)]
        
        # Nonlinear least squares regression to fit the logistic curve
        try:
            popt, pcov = curve_fit(self._logistic_function, X_train, y_train, p0=p0, maxfev=10000)
            self.L, self.k, self.x0 = popt
            
            # Predict to evaluate fit accuracy
            y_pred = self._logistic_function(X_train, *popt)
            mse = mean_squared_error(y_train, y_pred)
            r2 = r2_score(y_train, y_pred)
            
            self.performance_metrics = {"MSE": mse, "R2_Score": r2}
            
            print(f"Model fitted successfully. Learned parameters: L={self.L:.3f}, k={self.k:.3f}, x0={self.x0:.3f}")
            print(f"Validation Metrics: MSE={mse:.4f}, R2={r2:.4f}")
            
        except RuntimeError as e:
            print(f"Optimal parameters not found: {e}")

    def predict_growth_stage(self, current_duration: float) -> float:
        """
        Inflicts the trained regression model on real-time inputs.
        """
        if self.L is None:
            raise Exception("Model is uninitialized. Call fit_growth_profile first.")
            
        return self._logistic_function(current_duration, self.L, self.k, self.x0)

if __name__ == "__main__":
    # Typical ML evaluation run
    estimator = LogisticRegressionEstimator()
    estimator.fit_growth_profile(known_limit=1.0, known_growth_rate=0.45)
    
    # Validation prediction
    stage_at_30h = estimator.predict_growth_stage(30.0)
    print(f"Biological growth scale mapping at 30 hours: {stage_at_30h:.4f}")
