from dataclasses import dataclass
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

model = load_model('lstm/traffic_model.h5')


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


@dataclass
class PredictInputData:
    road_id: int
    start_time: str
    end_time: str
    traffic_volume: int


def run(
    inputs: list[PredictInputData]
):
    # # 加载数据
    # df = pd.read_csv('test.txt', sep='\t', header=0, names=[
    #     'roadid', 'start_time', 'end_time', 'traffic_volume'])

    df = pd.DataFrame([vars(i) for i in inputs])

    # 将时间字符串转换为 datetime 对象
    df['time'] = pd.to_datetime(df['start_time'])

    # 添加节假日特征 从2023年12月1日到2024年4月30日的所有节假日日期
    holidays = [
        '2023-12-25', '2023-12-26',  # 圣诞节
        '2023-12-30', '2023-12-31', '2024-01-01',  # 元旦
        '2024-02-09', '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13', '2024-02-14', '2024-02-15',
        '2024-02-16', '2024-02-17',  # 春节
        '2024-04-04', '2024-04-05', '2024-04-06'  # 清明节
    ]

    # 将节假日日期转换为 datetime 对象
    holidays = pd.to_datetime(holidays)

    # 创建一个新列，判断日期是否为节假日
    df['is_holiday'] = df['time'].isin(holidays).astype(int)

    # 提取时间特征
    df['weekday'] = df['time'].dt.weekday  # 周一为0，周日为6
    df['hour'] = df['time'].dt.hour
    df['is_weekend'] = df['weekday'].isin([5, 6]).astype(int)  # 周末为1，非周末为0
    # df['is_lowpeak_hour'] = df['hour'].isin([18,19,20]).astype(int)  # 设定高峰时段

    # 特征选择
    features = df[['traffic_volume', 'weekday',
                   'hour', 'is_weekend',  'is_holiday']]

    # 归一化流量数据
    scaler_traffic = MinMaxScaler()
    df['traffic_volume_normalized'] = scaler_traffic.fit_transform(
        df[['traffic_volume']])

    # 对其他特征进行归一化
    scaler_features = MinMaxScaler()
    df[['weekday', 'hour', 'is_weekend',  'is_holiday']] = scaler_features.fit_transform(
        df[['weekday', 'hour', 'is_weekend',  'is_holiday']])

    # 合并归一化后的数据
    features_normalized = df[['traffic_volume_normalized',
                              'weekday', 'hour', 'is_weekend', 'is_holiday']].values

    # 创建序列数据
    look_back = 6

    # 进行未来1小时的预测
    # 使用最后的look_back个历史数据作为初始输入
    last_sequence = features_normalized[-look_back:]

    # 创建一个存储预测值的列表
    predicted_traffic = []

    # 预测未来6个5分钟的流量
    for _ in range(6):
        # 使用当前的last_sequence进行预测
        next_traffic = model.predict(last_sequence.reshape(1, look_back, 5))
        predicted_traffic.append(next_traffic[0, 0])

        # 更新last_sequence，移除第一个元素，添加预测值
        last_sequence = np.append(last_sequence[1:], [
            [next_traffic[0, 0], last_sequence[-1, 1], last_sequence[-1, 2], last_sequence[-1, 3], last_sequence[-1, 4]]],
            axis=0)

    # 反归一化预测值并取整
    predicted_traffic_inverse = scaler_traffic.inverse_transform(
        np.array(predicted_traffic).reshape(-1, 1))
    predicted_traffic_rounded = np.round(
        predicted_traffic_inverse).astype(int)  # 取整并转换为整数类型

    # 保存预测结果到txt文件
    future_times = pd.date_range(
        # 未来的时间序列
        start=df['time'].iloc[-1] + pd.Timedelta(minutes=5), periods=6, freq='5T')
    predictions_df = pd.DataFrame({
        'time': future_times,
        'predicted_traffic_volume': predicted_traffic_rounded.flatten()  # 使用取整后的流量
    })

    return predictions_df.to_dict(orient='records')
    # predictions_df.to_csv('future_traffic_predictions.txt',
    #                       sep='\t', index=False, header=True)
    # print('未来30min的交通流预测（取整后）已保存到future_traffic_predictions.txt')


if __name__ == "__main__":
    df = pd.read_csv('test.txt', sep='\t', header=0, names=[
        'road_id', 'start_time', 'end_time', 'traffic_volume'])

    input_data = [PredictInputData(**i) for i in df.to_dict(orient='records')]
    output = run(input_data)
    print(output)
