from datetime import datetime
def filtered_data(start_date, end_date, df):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    chart_data = df[(df['dischargeDate'] >= start_date) &
                     (df['dischargeDate'] <= end_date)]
    return chart_data
    