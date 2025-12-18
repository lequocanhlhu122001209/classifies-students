import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class StudentTrendAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.trend_model = LinearRegression()
        
    def create_time_series(self, df, start_date='2025-01-01'):
        """Tạo dữ liệu chuỗi thời gian từ dữ liệu sinh viên"""
        # Tạo các mốc thời gian
        start = datetime.strptime(start_date, '%Y-%m-%d')
        dates = [start + timedelta(days=i*7) for i in range(16)]  # 16 tuần học
        
        # Tạo dữ liệu xu hướng cho từng sinh viên
        trends_data = []
        
        for _, student in df.iterrows():
            base_scores = {
                'academic': (student['midterm_score'] + student['final_score'] + student['homework_score']) / 3,
                'attendance': student['attendance_rate_100'],
                'behavior': student['behCTior_score_100'],
                'engagement': student['participation_score'] * 10
            }
            
            # Tạo xu hướng với nhiễu ngẫu nhiên
            for week, date in enumerate(dates):
                noise = np.random.normal(0, 0.5)
                weekly_data = {
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'date': date,
                    'week': week + 1,
                    'academic_score': min(10, max(0, base_scores['academic'] + noise)),
                    'attendance_rate': min(100, max(0, base_scores['attendance'] + noise)),
                    'behavior_score': min(100, max(0, base_scores['behavior'] + noise)),
                    'engagement_score': min(100, max(0, base_scores['engagement'] + noise))
                }
                trends_data.append(weekly_data)
                
        return pd.DataFrame(trends_data)
    
    def analyze_trends(self, trends_df, student_id=None):
        """Phân tích xu hướng học tập"""
        if student_id:
            student_data = trends_df[trends_df['student_id'] == student_id]
        else:
            student_data = trends_df
            
        # Tính toán xu hướng các chỉ số
        metrics = ['academic_score', 'attendance_rate', 'behavior_score', 'engagement_score']
        trends = {}
        
        for metric in metrics:
            X = student_data['week'].values.reshape(-1, 1)
            y = student_data[metric].values
            
            self.trend_model.fit(X, y)
            trend = self.trend_model.coef_[0]
            trends[metric] = {
                'slope': trend,
                'direction': 'Tăng' if trend > 0.1 else 'Giảm' if trend < -0.1 else 'Ổn định',
                'average': np.mean(y)
            }
            
        return trends
    
    def predict_future_performance(self, trends_df, student_id, weeks_ahead=4):
        """Dự đoán kết quả trong tương lai"""
        student_data = trends_df[trends_df['student_id'] == student_id]
        last_week = student_data['week'].max()
        
        predictions = {}
        metrics = ['academic_score', 'attendance_rate', 'behavior_score', 'engagement_score']
        
        for metric in metrics:
            X = student_data['week'].values.reshape(-1, 1)
            y = student_data[metric].values
            
            self.trend_model.fit(X, y)
            
            future_weeks = np.array(range(last_week + 1, last_week + weeks_ahead + 1))
            future_predictions = self.trend_model.predict(future_weeks.reshape(-1, 1))
            
            predictions[metric] = {
                'values': future_predictions.tolist(),
                'weeks': future_weeks.tolist()
            }
            
        return predictions
    
    def generate_trend_report(self, trends_df, student_id=None):
        """Tạo báo cáo xu hướng với biểu đồ"""
        if student_id:
            data = trends_df[trends_df['student_id'] == student_id]
            title_suffix = f"của sinh viên {data['name'].iloc[0]}"
        else:
            data = trends_df
            title_suffix = "của toàn bộ sinh viên"
            
        plt.figure(figsize=(15, 10))
        
        # Biểu đồ xu hướng điểm số
        plt.subplot(2, 2, 1)
        sns.lineplot(data=data, x='week', y='academic_score', ci=None)
        plt.title(f'Xu hướng điểm học tập {title_suffix}')
        plt.xlabel('Tuần')
        plt.ylabel('Điểm')
        
        # Biểu đồ điểm danh
        plt.subplot(2, 2, 2)
        sns.lineplot(data=data, x='week', y='attendance_rate', ci=None)
        plt.title(f'Tỷ lệ điểm danh {title_suffix}')
        plt.xlabel('Tuần')
        plt.ylabel('Tỷ lệ (%)')
        
        # Biểu đồ hành vi
        plt.subplot(2, 2, 3)
        sns.lineplot(data=data, x='week', y='behavior_score', ci=None)
        plt.title(f'Điểm hành vi {title_suffix}')
        plt.xlabel('Tuần')
        plt.ylabel('Điểm')
        
        # Biểu đồ tham gia
        plt.subplot(2, 2, 4)
        sns.lineplot(data=data, x='week', y='engagement_score', ci=None)
        plt.title(f'Mức độ tham gia {title_suffix}')
        plt.xlabel('Tuần')
        plt.ylabel('Điểm')
        
        plt.tight_layout()
        
        if student_id:
            plt.savefig(f'trend_report_{student_id}.png')
        else:
            plt.savefig('overall_trend_report.png')
        
        # Phân tích xu hướng
        trends = self.analyze_trends(data)
        
        return {
            'trends': trends,
            'plot_path': f'trend_report_{student_id}.png' if student_id else 'overall_trend_report.png'
        }
    
    def identify_at_risk_students(self, trends_df, threshold_weeks=3):
        """Xác định sinh viên có nguy cơ dựa trên xu hướng gần đây"""
        recent_data = trends_df[trends_df['week'] > trends_df['week'].max() - threshold_weeks]
        
        at_risk_students = []
        for student_id in recent_data['student_id'].unique():
            student_data = recent_data[recent_data['student_id'] == student_id]
            trends = self.analyze_trends(student_data)
            
            risk_factors = []
            if trends['academic_score']['slope'] < -0.2:
                risk_factors.append('Điểm số giảm')
            if trends['attendance_rate']['average'] < 70:
                risk_factors.append('Điểm danh thấp')
            if trends['behavior_score']['slope'] < -0.2:
                risk_factors.append('Hành vi xấu đi')
            if trends['engagement_score']['average'] < 60:
                risk_factors.append('Tham gia kém')
                
            if risk_factors:
                at_risk_students.append({
                    'student_id': student_id,
                    'name': student_data['name'].iloc[0],
                    'risk_factors': risk_factors,
                    'trend_scores': trends
                })
                
        return at_risk_students

def run_trend_analysis():
    # Đọc dữ liệu gốc
    df = pd.read_csv('student_classification_supabase_ready_final.csv')
    
    # Khởi tạo analyzer
    analyzer = StudentTrendAnalyzer()
    
    # Tạo dữ liệu chuỗi thời gian
    trends_df = analyzer.create_time_series(df)
    
    # Tạo báo cáo xu hướng tổng thể
    overall_report = analyzer.generate_trend_report(trends_df)
    
    # Xác định sinh viên có nguy cơ
    at_risk = analyzer.identify_at_risk_students(trends_df)
    
    # In báo cáo
    print("\n=== BÁO CÁO XU HƯỚNG HỌC TẬP ===")
    print("\nXu hướng tổng thể:")
    for metric, data in overall_report['trends'].items():
        print(f"\n{metric}:")
        print(f"- Xu hướng: {data['direction']}")
        print(f"- Trung bình: {data['average']:.2f}")
    
    print("\nSinh viên có nguy cơ:")
    for student in at_risk:
        print(f"\n{student['name']} ({student['student_id']}):")
        print(f"Các yếu tố rủi ro: {', '.join(student['risk_factors'])}")
        
    # Lưu dữ liệu xu hướng
    trends_df.to_csv('student_trends.csv', index=False)
    print("\nDữ liệu xu hướng đã được lưu vào 'student_trends.csv'")
    print(f"Biểu đồ xu hướng đã được lưu vào '{overall_report['plot_path']}'")

if __name__ == "__main__":
    run_trend_analysis()