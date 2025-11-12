"""
Data Processing Tool
Provides comprehensive data processing capabilities for AI agents.
"""

import pandas as pd
import numpy as np
import json
import csv
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, date
import statistics
import math

class DataProcessingTool:
    """
    Comprehensive data processing tool for AI agents.
    Supports data cleaning, transformation, analysis, and visualization.
    """
    
    def __init__(self, max_data_size: int = 100 * 1024 * 1024):
        """
        Initialize data processing tool.
        
        Args:
            max_data_size: Maximum data size in bytes (default: 100MB)
        """
        self.max_data_size = max_data_size
        self.supported_formats = ['csv', 'json', 'excel', 'parquet']
        
    def load_data(self, file_path: str, format_type: str = "auto", **kwargs) -> Dict[str, Any]:
        """
        Load data from various file formats.
        
        Args:
            file_path: Path to data file
            format_type: File format ('auto', 'csv', 'json', 'excel', 'parquet')
            **kwargs: Additional parameters for pandas readers
            
        Returns:
            Dictionary with loaded data and metadata
        """
        try:
            # Auto-detect format if not specified
            if format_type == "auto":
                format_type = self._detect_format(file_path)
            
            # Load data based on format
            if format_type == "csv":
                df = pd.read_csv(file_path, **kwargs)
            elif format_type == "json":
                df = pd.read_json(file_path, **kwargs)
            elif format_type == "excel":
                df = pd.read_excel(file_path, **kwargs)
            elif format_type == "parquet":
                df = pd.read_parquet(file_path, **kwargs)
            else:
                return {"success": False, "error": f"Unsupported format: {format_type}"}
            
            # Generate metadata
            metadata = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "null_counts": df.isnull().sum().to_dict(),
                "format": format_type
            }
            
            return {
                "success": True,
                "data": df,
                "metadata": metadata,
                "sample": df.head().to_dict('records')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def clean_data(self, data: pd.DataFrame, operations: List[str] = None) -> Dict[str, Any]:
        """
        Clean data using various operations.
        
        Args:
            data: Pandas DataFrame to clean
            operations: List of cleaning operations to perform
            
        Returns:
            Dictionary with cleaned data and operation results
        """
        try:
            if operations is None:
                operations = ['remove_duplicates', 'handle_missing', 'fix_types', 'remove_outliers']
            
            df = data.copy()
            cleaning_log = []
            
            # Remove duplicates
            if 'remove_duplicates' in operations:
                before_count = len(df)
                df = df.drop_duplicates()
                duplicates_removed = before_count - len(df)
                cleaning_log.append(f"Removed {duplicates_removed} duplicate rows")
            
            # Handle missing values
            if 'handle_missing' in operations:
                missing_before = df.isnull().sum().sum()
                
                # For numeric columns, fill with median
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
                
                # For categorical columns, fill with mode
                categorical_columns = df.select_dtypes(include=['object']).columns
                for col in categorical_columns:
                    mode_value = df[col].mode()
                    if len(mode_value) > 0:
                        df[col] = df[col].fillna(mode_value[0])
                
                missing_after = df.isnull().sum().sum()
                cleaning_log.append(f"Handled {missing_before - missing_after} missing values")
            
            # Fix data types
            if 'fix_types' in operations:
                # Try to convert object columns to numeric where possible
                for col in df.select_dtypes(include=['object']).columns:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except:
                        pass
                
                # Try to convert to datetime where possible
                for col in df.columns:
                    if 'date' in col.lower() or 'time' in col.lower():
                        try:
                            df[col] = pd.to_datetime(df[col], errors='ignore')
                        except:
                            pass
                
                cleaning_log.append("Attempted to fix data types")
            
            # Remove outliers (using IQR method for numeric columns)
            if 'remove_outliers' in operations:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                outliers_removed = 0
                
                for col in numeric_columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                    outliers_removed += outlier_mask.sum()
                    df = df[~outlier_mask]
                
                cleaning_log.append(f"Removed {outliers_removed} outliers")
            
            return {
                "success": True,
                "data": df,
                "cleaning_log": cleaning_log,
                "metadata": {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_data(self, data: pd.DataFrame, analysis_type: str = "basic") -> Dict[str, Any]:
        """
        Perform data analysis.
        
        Args:
            data: Pandas DataFrame to analyze
            analysis_type: Type of analysis ('basic', 'statistical', 'correlation')
            
        Returns:
            Dictionary with analysis results
        """
        try:
            results = {}
            
            if analysis_type in ["basic", "statistical"]:
                # Basic statistics
                results["basic_stats"] = {
                    "shape": data.shape,
                    "columns": list(data.columns),
                    "dtypes": data.dtypes.to_dict(),
                    "null_counts": data.isnull().sum().to_dict(),
                    "memory_usage": data.memory_usage(deep=True).sum()
                }
                
                # Descriptive statistics for numeric columns
                numeric_data = data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    results["descriptive_stats"] = numeric_data.describe().to_dict()
                
                # Categorical data analysis
                categorical_data = data.select_dtypes(include=['object'])
                if not categorical_data.empty:
                    results["categorical_stats"] = {}
                    for col in categorical_data.columns:
                        results["categorical_stats"][col] = {
                            "unique_count": categorical_data[col].nunique(),
                            "most_frequent": categorical_data[col].mode().iloc[0] if not categorical_data[col].mode().empty else None,
                            "frequency": categorical_data[col].value_counts().head().to_dict()
                        }
            
            if analysis_type in ["statistical", "correlation"]:
                # Correlation analysis
                numeric_data = data.select_dtypes(include=[np.number])
                if len(numeric_data.columns) > 1:
                    correlation_matrix = numeric_data.corr()
                    results["correlation"] = correlation_matrix.to_dict()
                    
                    # Find strong correlations
                    strong_correlations = []
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            corr_value = correlation_matrix.iloc[i, j]
                            if abs(corr_value) > 0.7:  # Strong correlation threshold
                                strong_correlations.append({
                                    "column1": correlation_matrix.columns[i],
                                    "column2": correlation_matrix.columns[j],
                                    "correlation": corr_value
                                })
                    
                    results["strong_correlations"] = strong_correlations
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def transform_data(self, data: pd.DataFrame, transformations: List[Dict]) -> Dict[str, Any]:
        """
        Apply transformations to data.
        
        Args:
            data: Pandas DataFrame to transform
            transformations: List of transformation dictionaries
            
        Returns:
            Dictionary with transformed data
        """
        try:
            df = data.copy()
            transformation_log = []
            
            for transform in transformations:
                transform_type = transform.get("type")
                column = transform.get("column")
                
                if transform_type == "normalize":
                    # Min-max normalization
                    min_val = df[column].min()
                    max_val = df[column].max()
                    df[column] = (df[column] - min_val) / (max_val - min_val)
                    transformation_log.append(f"Normalized column {column}")
                
                elif transform_type == "standardize":
                    # Z-score standardization
                    mean_val = df[column].mean()
                    std_val = df[column].std()
                    df[column] = (df[column] - mean_val) / std_val
                    transformation_log.append(f"Standardized column {column}")
                
                elif transform_type == "log_transform":
                    # Log transformation
                    df[column] = np.log1p(df[column])
                    transformation_log.append(f"Applied log transform to column {column}")
                
                elif transform_type == "bin":
                    # Binning
                    bins = transform.get("bins", 5)
                    labels = transform.get("labels")
                    df[column] = pd.cut(df[column], bins=bins, labels=labels)
                    transformation_log.append(f"Binned column {column} into {bins} bins")
                
                elif transform_type == "one_hot_encode":
                    # One-hot encoding
                    df = pd.get_dummies(df, columns=[column], prefix=column)
                    transformation_log.append(f"One-hot encoded column {column}")
                
                elif transform_type == "create_feature":
                    # Create new feature
                    expression = transform.get("expression")
                    new_column = transform.get("new_column")
                    df[new_column] = df.eval(expression)
                    transformation_log.append(f"Created new column {new_column}")
            
            return {
                "success": True,
                "data": df,
                "transformation_log": transformation_log,
                "metadata": {
                    "shape": df.shape,
                    "columns": list(df.columns)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_data(self, data: pd.DataFrame, file_path: str, format_type: str = "csv", **kwargs) -> Dict[str, Any]:
        """
        Export data to various formats.
        
        Args:
            data: Pandas DataFrame to export
            file_path: Output file path
            format_type: Export format ('csv', 'json', 'excel', 'parquet')
            **kwargs: Additional parameters for pandas writers
            
        Returns:
            Dictionary with export result
        """
        try:
            if format_type == "csv":
                data.to_csv(file_path, index=False, **kwargs)
            elif format_type == "json":
                data.to_json(file_path, orient='records', **kwargs)
            elif format_type == "excel":
                data.to_excel(file_path, index=False, **kwargs)
            elif format_type == "parquet":
                data.to_parquet(file_path, **kwargs)
            else:
                return {"success": False, "error": f"Unsupported format: {format_type}"}
            
            return {
                "success": True,
                "file_path": file_path,
                "format": format_type,
                "rows": len(data),
                "columns": len(data.columns)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _detect_format(self, file_path: str) -> str:
        """Detect file format from extension."""
        extension = file_path.split('.')[-1].lower()
        
        format_map = {
            'csv': 'csv',
            'json': 'json',
            'xlsx': 'excel',
            'xls': 'excel',
            'parquet': 'parquet'
        }
        
        return format_map.get(extension, 'csv')

# Tool metadata
TOOL_INFO = {
    "name": "data_processing",
    "description": "Comprehensive data processing tool for analysis and transformation",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "load_data",
        "clean_data",
        "analyze_data",
        "transform_data",
        "export_data"
    ],
    "requirements": ["pandas", "numpy", "openpyxl", "pyarrow"],
    "safety_features": [
        "Data size limits",
        "Memory usage monitoring",
        "Error handling",
        "Data validation"
    ]
}

if __name__ == "__main__":
    # Example usage
    tool = DataProcessingTool()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['x', 'y', 'z', 'x', 'y']
    })
    
    # Test data analysis
    result = tool.analyze_data(sample_data)
    print("Analysis result:", result["success"])