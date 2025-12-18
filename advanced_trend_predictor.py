import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class AdvancedTrendPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def analyze_performance_patterns(self, trends_df):
        """Phân tích mẫu hình học tập theo thời gian"""
        patterns = {}
        
        # Phân tích theo ngày trong tuần
        trends_df['weekday'] = pd.to_datetime(trends_df['date']).dt.dayofweek
        weekday_stats = trends_df.groupby('weekday').agg({
            'academic_score': 'mean',
            'attendance_rate': 'mean',
            'behavior_score': 'mean',
            'engagement_score': 'mean'
        })
        patterns['weekday_performance'] = weekday_stats.to_dict()
        
        # Phân tích xu hướng dài hạn
        for metric in ['academic_score', 'attendance_rate', 'behavior_score', 'engagement_score']:
            slope, _, r_value, p_value, _ = stats.linregress(
                range(len(trends_df[metric])), trends_df[metric]
            )
            patterns[f'{metric}_trend'] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value
            }
            
        return patterns
    
    def identify_improvement_areas(self, student_data):
        """Xác định các lĩnh vực cần cải thiện và đề xuất giải pháp"""
        improvements = []
        
        # Phân tích điểm số
        if student_data['academic_score'].mean() < 7.0:
            improvements.append({
                'area': 'Học tập',
                'issue': 'Điểm số thấp',
                'recommendations': [
                    'Tham gia các nhóm học tập',
                    'Đặt lịch học cụ thể cho từng môn',
                    'Tìm kiếm sự hỗ trợ từ giáo viên'
                ]
            })
        
        # Phân tích điểm danh
        if student_data['attendance_rate'].mean() < 80:
            improvements.append({
                'area': 'Chuyên cần',
                'issue': 'Tỷ lệ điểm danh thấp',
                'recommendations': [
                    'Lập kế hoạch đi học đều đặn',
                    'Đặt báo thức sớm hơn',
                    'Liên hệ với giáo viên khi có việc đột xuất'
                ]
            })
        
        # Phân tích hành vi
        if student_data['behavior_score'].mean() < 70:
            improvements.append({
                'area': 'Hành vi',
                'issue': 'Điểm hành vi thấp',
                'recommendations': [
                    'Tích cực tham gia hoạt động lớp',
                    'Hoàn thành bài tập đúng hạn',
                    'Tương tác nhiều hơn trong giờ học'
                ]
            })
        
        return improvements
    
    def predict_future_outcomes(self, student_data, weeks_ahead=8):
        """Dự đoán kết quả học tập trong tương lai với độ tin cậy"""
        predictions = {}
        
        # Chuẩn bị dữ liệu
        X = student_data[['week', 'attendance_rate', 
                         'behavior_score', 'engagement_score']].values
        for metric in ['academic_score', 'behavior_score', 'engagement_score']:
            y = student_data[metric].values
            
            # Huấn luyện mô hình
            self.rf_regressor.fit(X, y)
            
            # Tạo dữ liệu tương lai
            future_weeks = np.array(range(student_data['week'].max() + 1,
                                        student_data['week'].max() + weeks_ahead + 1))
            
            # Dự đoán với khoảng tin cậy
            predictions[metric] = []
            for week in future_weeks:
                future_X = X[-1].copy()
                future_X[0] = week
                
                # Dự đoán với nhiều cây trong rừng ngẫu nhiên
                pred = []
                for estimator in self.rf_regressor.estimators_:
                    pred.append(estimator.predict([future_X])[0])
                
                mean_pred = np.mean(pred)
                std_pred = np.std(pred)
                
                predictions[metric].append({
                    'week': week,
                    'prediction': mean_pred,
                    'lower_bound': mean_pred - 1.96 * std_pred,
                    'upper_bound': mean_pred + 1.96 * std_pred,
                    'confidence': 1 - (std_pred / mean_pred)  # Độ tin cậy của dự đoán
                })
        
        return predictions
    
    def generate_personalized_report(self, student_data, predictions):
        """Tạo báo cáo cá nhân hóa với đề xuất cụ thể"""
        report = {
            'current_status': {},
            'predictions': {},
            'recommendations': [],
            'risk_assessment': {}
        }
        
        # Phân tích trạng thái hiện tại
        current_metrics = {
            'academic_score': student_data['academic_score'].iloc[-1],
            'attendance_rate': student_data['attendance_rate'].iloc[-1],
            'behavior_score': student_data['behavior_score'].iloc[-1],
            'engagement_score': student_data['engagement_score'].iloc[-1]
        }
        report['current_status'] = current_metrics
        
        # Đánh giá xu hướng
        metrics_list = list(current_metrics.keys())
        for metric in metrics_list:
            trend = np.polyfit(range(len(student_data[metric])), 
                             student_data[metric], 1)[0]
            report['current_status'][f'{metric}_trend'] = trend
        
        # Dự đoán tương lai
        for metric in predictions.keys():
            future_values = [p['prediction'] for p in predictions[metric]]
            report['predictions'][metric] = {
                'end_value': future_values[-1],
                'trend': np.mean(np.diff(future_values)),
                'confidence': np.mean([p['confidence'] for p in predictions[metric]])
            }
        
        # Đánh giá rủi ro
        risk_factors = []
        if current_metrics['academic_score'] < 6.5:
            risk_factors.append('Điểm số thấp')
        if current_metrics['attendance_rate'] < 70:
            risk_factors.append('Vắng mặt nhiều')
        if current_metrics['behavior_score'] < 65:
            risk_factors.append('Hành vi cần cải thiện')
            
        report['risk_assessment'] = {
            'risk_level': 'Cao' if len(risk_factors) >= 2 else 'Trung bình' if len(risk_factors) == 1 else 'Thấp',
            'risk_factors': risk_factors
        }
        
        # Tạo đề xuất cá nhân hóa
        improvements = self.identify_improvement_areas(student_data)
        report['recommendations'] = improvements
        
        return report
    
    def visualize_predictions(self, student_data, predictions, student_id):
        """Tạo biểu đồ dự đoán với khoảng tin cậy"""
        plt.figure(figsize=(15, 10))
        
        metrics = ['academic_score', 'behavior_score', 'engagement_score']
        for idx, metric in enumerate(metrics, 1):
            plt.subplot(2, 2, idx)
            
            # Dữ liệu lịch sử
            plt.plot(student_data['week'], student_data[metric], 
                    'b-', label='Thực tế')
            
            # Dự đoán
            weeks = [p['week'] for p in predictions[metric]]
            pred_values = [p['prediction'] for p in predictions[metric]]
            lower_bounds = [p['lower_bound'] for p in predictions[metric]]
            upper_bounds = [p['upper_bound'] for p in predictions[metric]]
            
            plt.plot(weeks, pred_values, 'r--', label='Dự đoán')
            plt.fill_between(weeks, lower_bounds, upper_bounds, 
                           color='r', alpha=0.2, label='Khoảng tin cậy 95%')
            
            plt.title(f'Dự đoán {metric}')
            plt.xlabel('Tuần')
            plt.ylabel('Điểm số')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'predictions_{student_id}.png')
        plt.close()

def run_advanced_analysis():
    # Đọc dữ liệu xu hướng
    trends_df = pd.read_csv('student_trends.csv')
    
    # Khởi tạo predictor
    predictor = AdvancedTrendPredictor()
    
    # Phân tích cho từng sinh viên
    for student_id in trends_df['student_id'].unique():
        student_data = trends_df[trends_df['student_id'] == student_id]
        
        # Dự đoán tương lai
        predictions = predictor.predict_future_outcomes(student_data)
        
        # Tạo báo cáo cá nhân
        report = predictor.generate_personalized_report(student_data, predictions)
        
        # Tạo biểu đồ dự đoán
        predictor.visualize_predictions(student_data, predictions, student_id)
        
        # Lưu báo cáo
        with open(f'student_report_{student_id}.txt', 'w', encoding='utf-8') as f:
            f.write(f"=== BÁO CÁO CHI TIẾT SINH VIÊN {student_id} ===\n\n")
            
            f.write("1. Trạng thái hiện tại:\n")
            for metric, value in report['current_status'].items():
                f.write(f"   - {metric}: {value:.2f}\n")
            
            f.write("\n2. Dự đoán tương lai:\n")
            for metric, data in report['predictions'].items():
                f.write(f"   - {metric}:\n")
                f.write(f"     + Giá trị cuối: {data['end_value']:.2f}\n")
                f.write(f"     + Xu hướng: {data['trend']:.2f}\n")
                f.write(f"     + Độ tin cậy: {data['confidence']:.2%}\n")
            
            f.write("\n3. Đánh giá rủi ro:\n")
            f.write(f"   - Mức độ rủi ro: {report['risk_assessment']['risk_level']}\n")
            if report['risk_assessment']['risk_factors']:
                f.write("   - Các yếu tố rủi ro:\n")
                for factor in report['risk_assessment']['risk_factors']:
                    f.write(f"     + {factor}\n")
            
            f.write("\n4. Đề xuất cải thiện:\n")
            for improvement in report['recommendations']:
                f.write(f"   - Lĩnh vực: {improvement['area']}\n")
                f.write(f"   - Vấn đề: {improvement['issue']}\n")
                f.write("   - Đề xuất:\n")
                for rec in improvement['recommendations']:
                    f.write(f"     + {rec}\n")
                f.write("\n")

if __name__ == "__main__":
    run_advanced_analysis()