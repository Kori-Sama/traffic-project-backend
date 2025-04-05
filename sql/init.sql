-- 确保 PostGIS 扩展已启用
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS road (
    link_id BIGINT PRIMARY KEY,               -- 路段ID，主键，自增
    link_length int NOT NULL,    -- 路段长度
    road_geom GEOMETRY(LINESTRING, 4326) NOT NULL, -- 路段几何信息，使用 LINESTRING 类型
    road_name VARCHAR(255) NOT NULL,      -- 路段名称
    direction INT NOT NULL               -- 路段方向
);


CREATE TABLE IF NOT EXISTS traffic_event (
    event_id SERIAL PRIMARY KEY,                -- 事件ID，主键，自增
    event_type VARCHAR(50) NOT NULL,      -- 事件类型
    description TEXT,                     -- 事件描述（可为空）
    start_time TIMESTAMP NOT NULL,        -- 事件开始时间
    end_time TIMESTAMP,                   -- 事件结束时间（可为空
    create_time TIMESTAMP DEFAULT NOW()   -- 创建时间，默认为当前时间
);


CREATE TABLE IF NOT EXISTS road_to_event (
    id SERIAL PRIMARY KEY,                -- 主键，自增
    link_id BIGINT NOT NULL,             -- 路段ID
    event_id INTEGER NOT NULL,            -- 事件ID
    FOREIGN KEY (link_id) REFERENCES road(link_id), -- 外键约束
    FOREIGN KEY (event_id) REFERENCES traffic_event(event_id)  -- 外键约束
);

CREATE TABLE IF NOT EXISTS road_condition (
    condition_id SERIAL PRIMARY KEY,                -- 唯一标识路况数据
    date DATE NOT NULL,                   -- 日期
    link_id BIGINT NOT NULL,             -- 路段ID
    daily_10min TIMESTAMP NOT NULL,         -- 时间段（以10分钟为单位）
    real_speed DOUBLE PRECISION NOT NULL, -- 实际车速
    free_speed DOUBLE PRECISION NOT NULL, -- 自由流速
    idx DOUBLE PRECISION NOT NULL,        -- 流畅度（r/f）
    FOREIGN KEY (link_id) REFERENCES road(link_id), -- 外键约束
    UNIQUE (link_id, daily_10min) -- 联合唯一索引
);

CREATE TABLE IF NOT EXISTS traffic_status (
    status_id SERIAL PRIMARY KEY,                -- 唯一标识交通状态
    link_id BIGINT NOT NULL,             -- 路段ID
    daily_10min TIMESTAMP NOT NULL,         -- 时间段（以10分钟为单位）
    status VARCHAR(50) NOT NULL,          -- 交通状态（IDX判断）
    create_time TIMESTAMP DEFAULT NOW(),  -- 创建时间，默认为当前时间
    FOREIGN KEY (link_id) REFERENCES road(link_id) -- 外键约束
);

CREATE TABLE IF NOT EXISTS speed_limit_policy (
    policy_id SERIAL PRIMARY KEY,                -- 唯一标识限速策略
    link_id BIGINT NOT NULL,             -- 路段ID
    speed_limit DOUBLE PRECISION NOT NULL,-- 限速值
    start_time TIMESTAMP NOT NULL,        -- 限速开始时间
    end_time TIMESTAMP,                   -- 限速结束时间（可为空）
    create_time TIMESTAMP DEFAULT NOW(),  -- 创建时间，默认为当前时间
    FOREIGN KEY (link_id) REFERENCES road(link_id) -- 外键约束
);

-- 创建门架表
CREATE TABLE IF NOT EXISTS gantry (
    gantry_id SERIAL PRIMARY KEY,                 -- 门架ID，主键，自增
    sequence_number INT NOT NULL,                 -- 顺序编号
    unique_number INT NOT NULL,                   -- 唯一编号
    gantry_code VARCHAR(20) NOT NULL UNIQUE,      -- 门架编号
    gantry_name VARCHAR(100) NOT NULL,            -- 门架名称
    toll_station VARCHAR(50),                     -- 所属收费站
    subcenter VARCHAR(50),                        -- 所属分中心
    longitude DOUBLE PRECISION NOT NULL,          -- 经度
    latitude DOUBLE PRECISION NOT NULL,           -- 纬度
    stake_number VARCHAR(20),                     -- 桩号
    direction INT NOT NULL,                       -- 方向：1表示上行，2表示下行
    location GEOMETRY(POINT, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED
);

-- 创建车辆通行记录表
CREATE TABLE IF NOT EXISTS vehicle_passage (
    passage_id SERIAL PRIMARY KEY,                -- 通行记录ID，主键，自增
    gantry_id INT NOT NULL,                       -- 门架ID，外键
    passage_time TIMESTAMP NOT NULL,              -- 通过时间
    vehicle_plate VARCHAR(20) NOT NULL,           -- 车牌号
    vehicle_type INT NOT NULL,                    -- 车辆类型
    FOREIGN KEY (gantry_id) REFERENCES gantry(gantry_id)
);

-- 创建索引以提高查询效率
CREATE INDEX idx_vehicle_passage_gantry_id ON vehicle_passage(gantry_id);
CREATE INDEX idx_vehicle_passage_passage_time ON vehicle_passage(passage_time);
CREATE INDEX idx_vehicle_passage_vehicle_plate ON vehicle_passage(vehicle_plate);
CREATE INDEX idx_gantry_location ON gantry USING GIST(location);