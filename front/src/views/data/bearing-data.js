// 轴承库数据 - 电机常用轴承规格
// 字段说明：
//   model:         轴承型号（唯一标识）
//   series:        所属系列（6200/6300/6000/6400/NU200/UCP200/7000）
//   bearing_type:  轴承类型
//   d:             内径 mm
//   D:             外径 mm
//   B:             宽度 mm
//   r:             倒角 mm
//   dynamic_load:  基本额定动载荷 N
//   static_load:   基本额定静载荷 N
//   limit_speed:   极限转速 r/min（脂润滑）
//   weight:        重量 kg
//   frame_no:      对应机座号（WE电机常用关联）
//   position:      安装位置（前端/后端）
//   note:          备注

export const bearingSeriesList = ['6200', '6300', '6000', '6400', 'NU200', 'UCP200', '7000'];

export const bearingData = [
  // ===== 6200 系列（深沟球轴承 - 轻宽，电机主力）=====
  { model:'6200', series:'6200', bearing_type:'深沟球轴承', d:10, D:30, B:9,  r:0.6, dynamic_load:5100,  static_load:2390,  limit_speed:26000, weight:0.037, frame_no:'',           position:'',       note:'标准开式' },
  { model:'6201', series:'6200', bearing_type:'深沟球轴承', d:12, D:32, B:10, r:0.6, dynamic_load:7280,  static_load:3100,  limit_speed:24000, weight:0.047, frame_no:'',           position:'',       note:'标准开式' },
  { model:'6202', series:'6200', bearing_type:'深沟球轴承', d:15, D:35, B:11, r:0.6, dynamic_load:7650,  static_load:3350,  limit_speed:20000, weight:0.058, frame_no:'',           position:'',       note:'标准开式' },
  { model:'6203', series:'6200', bearing_type:'深沟球轴承', d:17, D:40, B:12, r:0.6, dynamic_load:9580,  static_load:4020,  limit_speed:18000, weight:0.076, frame_no:'WE4-80',     position:'前端/后端', note:'标准开式' },
  { model:'6204', series:'6200', bearing_type:'深沟球轴承', d:20, D:47, B:14, r:1.0, dynamic_load:12800, static_load:5520,  limit_speed:16000, weight:0.106, frame_no:'WE4-90',     position:'前端/后端', note:'标准开式' },
  { model:'6205', series:'6200', bearing_type:'深沟球轴承', d:25, D:52, B:15, r:1.0, dynamic_load:14000, static_load:6200,  limit_speed:14000, weight:0.128, frame_no:'WE4-100',    position:'前端/后端', note:'标准开式' },
  { model:'6206', series:'6200', bearing_type:'深沟球轴承', d:30, D:62, B:16, r:1.0, dynamic_load:19500, static_load:8300,  limit_speed:13000, weight:0.193, frame_no:'WE4-112/132',position:'前端/后端', note:'标准开式' },
  { model:'6207', series:'6200', bearing_type:'深沟球轴承', d:35, D:72, B:17, r:1.1, dynamic_load:27000, static_load:15300, limit_speed:13000, weight:0.385, frame_no:'WE4-160',    position:'前端',     note:'SKF 6207-2RS1常用' },
  { model:'6208', series:'6200', bearing_type:'深沟球轴承', d:40, D:80, B:18, r:1.1, dynamic_load:32500, static_load:19800, limit_speed:12000, weight:0.448, frame_no:'WE4-180',    position:'前端',     note:'标准开式' },
  { model:'6209', series:'6200', bearing_type:'深沟球轴承', d:45, D:85, B:19, r:1.1, dynamic_load:33800, static_load:21200, limit_speed:11000, weight:0.493, frame_no:'WE4-200',    position:'前端',     note:'标准开式' },
  { model:'6210', series:'6200', bearing_type:'深沟球轴承', d:50, D:90, B:20, r:1.1, dynamic_load:36500, static_load:24100, limit_speed:10000, weight:0.543, frame_no:'WE4-225',    position:'前端',     note:'标准开式' },
  { model:'6211', series:'6200', bearing_type:'深沟球轴承', d:55, D:100,B:21, r:1.5, dynamic_load:43200, static_load:29200, limit_speed:9500,  weight:0.756, frame_no:'',           position:'',         note:'标准开式' },
  { model:'6212', series:'6200', bearing_type:'深沟球轴承', d:60, D:110,B:22, r:1.5, dynamic_load:47500, static_load:32800, limit_speed:8500,  weight:0.91,  frame_no:'',           position:'',         note:'标准开式' },
  { model:'6213', series:'6200', bearing_type:'深沟球轴承', d:65, D:120,B:23, r:1.5, dynamic_load:57000, static_load:38500, limit_speed:8000,  weight:1.08,  frame_no:'',           position:'',         note:'标准开式' },
  { model:'6214', series:'6200', bearing_type:'深沟球轴承', d:70, D:125,B:24, r:1.5, dynamic_load:60500, static_load:41800, limit_speed:7500,  weight:1.26,  frame_no:'',           position:'',         note:'标准开式' },
  { model:'6215', series:'6200', bearing_type:'深沟球轴承', d:75, D:130,B:25, r:1.5, dynamic_load:64000, static_load:45500, limit_speed:7000,  weight:1.39,  frame_no:'',           position:'',         note:'标准开式' },
  { model:'6216', series:'6200', bearing_type:'深沟球轴承', d:80, D:140,B:26, r:2.0, dynamic_load:72000, static_load:52500, limit_speed:6700,  weight:1.69,  frame_no:'',           position:'',         note:'标准开式' },
  { model:'6217', series:'6200', bearing_type:'深沟球轴承', d:85, D:150,B:28, r:2.0, dynamic_load:81500, static_load:60000, limit_speed:6300,  weight:2.0,   frame_no:'',           position:'',         note:'标准开式' },
  { model:'6218', series:'6200', bearing_type:'深沟球轴承', d:90, D:160,B:30, r:2.0, dynamic_load:88000, static_load:68500, limit_speed:6000,  weight:2.42,  frame_no:'',           position:'',         note:'标准开式' },

  // ===== 6300 系列（深沟球轴承 - 中宽，重载）=====
  { model:'6304', series:'6300', bearing_type:'深沟球轴承', d:20, D:52, B:15, r:1.1, dynamic_load:15900, static_load:7800,  limit_speed:15000, weight:0.14,  frame_no:'', position:'', note:'标准开式' },
  { model:'6305', series:'6300', bearing_type:'深沟球轴承', d:25, D:62, B:17, r:1.1, dynamic_load:22500, static_load:11600, limit_speed:13000, weight:0.23,  frame_no:'', position:'', note:'标准开式' },
  { model:'6306', series:'6300', bearing_type:'深沟球轴承', d:30, D:72, B:19, r:1.1, dynamic_load:27000, static_load:15800, limit_speed:12000, weight:0.345, frame_no:'', position:'', note:'标准开式' },
  { model:'6307', series:'6300', bearing_type:'深沟球轴承', d:35, D:80, B:21, r:1.5, dynamic_load:33500, static_load:20800, limit_speed:11000, weight:0.46,  frame_no:'', position:'', note:'标准开式' },
  { model:'6308', series:'6300', bearing_type:'深沟球轴承', d:40, D:90, B:23, r:1.5, dynamic_load:41000, static_load:27200, limit_speed:10000, weight:0.63,  frame_no:'', position:'', note:'标准开式' },
  { model:'6309', series:'6300', bearing_type:'深沟球轴承', d:45, D:100,B:25, r:1.5, dynamic_load:49500, static_load:33800, limit_speed:9000,  weight:0.83,  frame_no:'', position:'', note:'标准开式' },
  { model:'6310', series:'6300', bearing_type:'深沟球轴承', d:50, D:110,B:27, r:2.0, dynamic_load:58500, static_load:41200, limit_speed:8500,  weight:1.08,  frame_no:'', position:'', note:'标准开式' },
  { model:'6311', series:'6300', bearing_type:'深沟球轴承', d:55, D:120,B:29, r:2.0, dynamic_load:67500, static_load:49200, limit_speed:7500,  weight:1.37,  frame_no:'', position:'', note:'标准开式' },
  { model:'6312', series:'6300', bearing_type:'深沟球轴承', d:60, D:130,B:31, r:2.0, dynamic_load:76000, static_load:57800, limit_speed:7000,  weight:1.72,  frame_no:'', position:'', note:'标准开式' },

  // ===== 6000 系列（深沟球轴承 - 轻窄）=====
  { model:'6005', series:'6000', bearing_type:'深沟球轴承', d:25, D:47, B:12, r:0.6, dynamic_load:8800,  static_load:4550,  limit_speed:17000, weight:0.077, frame_no:'', position:'', note:'标准开式' },
  { model:'6006', series:'6000', bearing_type:'深沟球轴承', d:30, D:55, B:13, r:1.0, dynamic_load:11500, static_load:5900,  limit_speed:15000, weight:0.112, frame_no:'', position:'', note:'标准开式' },
  { model:'6007', series:'6000', bearing_type:'深沟球轴承', d:35, D:62, B:14, r:1.0, dynamic_load:15300, static_load:8150,  limit_speed:14000, weight:0.148, frame_no:'', position:'', note:'标准开式' },
  { model:'6008', series:'6000', bearing_type:'深沟球轴承', d:40, D:68, B:15, r:1.0, dynamic_load:17500, static_load:9700,  limit_speed:13000, weight:0.185, frame_no:'', position:'', note:'标准开式' },
  { model:'6009', series:'6000', bearing_type:'深沟球轴承', d:45, D:75, B:16, r:1.0, dynamic_load:20800, static_load:11800, limit_speed:12000, weight:0.232, frame_no:'', position:'', note:'标准开式' },
  { model:'6010', series:'6000', bearing_type:'深沟球轴承', d:50, D:80, B:16, r:1.0, dynamic_load:21500, static_load:13200, limit_speed:11000, weight:0.252, frame_no:'', position:'', note:'标准开式' },
  { model:'6011', series:'6000', bearing_type:'深沟球轴承', d:55, D:90, B:18, r:1.1, dynamic_load:26000, static_load:15600, limit_speed:10000, weight:0.353, frame_no:'', position:'', note:'标准开式' },
  { model:'6012', series:'6000', bearing_type:'深沟球轴承', d:60, D:95, B:18, r:1.1, dynamic_load:27000, static_load:16300, limit_speed:9500,  weight:0.38,  frame_no:'', position:'', note:'标准开式' },

  // ===== 6400 系列（深沟球轴承 - 重宽）=====
  { model:'6405', series:'6400', bearing_type:'深沟球轴承', d:25, D:80, B:21, r:1.5, dynamic_load:38500, static_load:20800, limit_speed:11000, weight:0.51,  frame_no:'', position:'', note:'标准开式' },
  { model:'6406', series:'6400', bearing_type:'深沟球轴承', d:30, D:90, B:23, r:1.5, dynamic_load:43000, static_load:24200, limit_speed:10000, weight:0.68,  frame_no:'', position:'', note:'标准开式' },
  { model:'6407', series:'6400', bearing_type:'深沟球轴承', d:35, D:100,B:25, r:1.5, dynamic_load:51500, static_load:29800, limit_speed:9000,  weight:0.95,  frame_no:'', position:'', note:'标准开式' },
  { model:'6408', series:'6400', bearing_type:'深沟球轴承', d:40, D:110,B:27, r:2.0, dynamic_load:56000, static_load:33800, limit_speed:8500,  weight:1.15,  frame_no:'', position:'', note:'标准开式' },
  { model:'6409', series:'6400', bearing_type:'深沟球轴承', d:45, D:120,B:29, r:2.0, dynamic_load:62000, static_load:37800, limit_speed:7500,  weight:1.5,   frame_no:'', position:'', note:'标准开式' },
  { model:'6410', series:'6400', bearing_type:'深沟球轴承', d:50, D:130,B:31, r:2.0, dynamic_load:71000, static_load:45000, limit_speed:7000,  weight:1.85,  frame_no:'', position:'', note:'标准开式' },

  // ===== NU 系列（圆柱滚子轴承，大功率电机后端）=====
  { model:'NU205', series:'NU200', bearing_type:'圆柱滚子轴承', d:25, D:52, B:15, r:1.0, dynamic_load:25500, static_load:15000, limit_speed:12000, weight:0.14,  frame_no:'',          position:'后端', note:'内圈可分离' },
  { model:'NU206', series:'NU200', bearing_type:'圆柱滚子轴承', d:30, D:62, B:16, r:1.0, dynamic_load:32500, static_load:18800, limit_speed:11000, weight:0.21,  frame_no:'',          position:'后端', note:'内圈可分离' },
  { model:'NU207', series:'NU200', bearing_type:'圆柱滚子轴承', d:35, D:72, B:17, r:1.1, dynamic_load:39000, static_load:23800, limit_speed:10000, weight:0.285, frame_no:'WE4-160',   position:'后端', note:'内圈可分离' },
  { model:'NU208', series:'NU200', bearing_type:'圆柱滚子轴承', d:40, D:80, B:18, r:1.1, dynamic_load:47500, static_load:30500, limit_speed:9500,  weight:0.365, frame_no:'WE4-180',   position:'后端', note:'内圈可分离' },
  { model:'NU209', series:'NU200', bearing_type:'圆柱滚子轴承', d:45, D:85, B:19, r:1.1, dynamic_load:51500, static_load:34500, limit_speed:8500,  weight:0.41,  frame_no:'WE4-200',   position:'后端', note:'内圈可分离' },
  { model:'NU210', series:'NU200', bearing_type:'圆柱滚子轴承', d:50, D:90, B:20, r:1.1, dynamic_load:57000, static_load:39000, limit_speed:8000,  weight:0.48,  frame_no:'WE4-225',   position:'后端', note:'内圈可分离' },
  { model:'NU211', series:'NU200', bearing_type:'圆柱滚子轴承', d:55, D:100,B:21, r:1.5, dynamic_load:64000, static_load:44500, limit_speed:7500,  weight:0.6,   frame_no:'',          position:'后端', note:'内圈可分离' },
  { model:'NU212', series:'NU200', bearing_type:'圆柱滚子轴承', d:60, D:110,B:22, r:1.5, dynamic_load:74000, static_load:52000, limit_speed:7000,  weight:0.79,  frame_no:'',          position:'后端', note:'内圈可分离' },

  // ===== UCP 系列（外球面球轴承带座）=====
  { model:'UCP204', series:'UCP200', bearing_type:'外球面球轴承', d:20, D:47, B:31, r:1.0, dynamic_load:12800, static_load:6650,  limit_speed:14000, weight:0.36, frame_no:'', position:'', note:'带P座' },
  { model:'UCP205', series:'UCP200', bearing_type:'外球面球轴承', d:25, D:52, B:34, r:1.0, dynamic_load:14000, static_load:7850,  limit_speed:12000, weight:0.46, frame_no:'', position:'', note:'带P座' },
  { model:'UCP206', series:'UCP200', bearing_type:'外球面球轴承', d:30, D:62, B:38, r:1.0, dynamic_load:19500, static_load:10800, limit_speed:11000, weight:0.65, frame_no:'', position:'', note:'带P座' },
  { model:'UCP207', series:'UCP200', bearing_type:'外球面球轴承', d:35, D:72, B:42, r:1.1, dynamic_load:25500, static_load:14200, limit_speed:10000, weight:0.85, frame_no:'', position:'', note:'带P座' },
  { model:'UCP208', series:'UCP200', bearing_type:'外球面球轴承', d:40, D:80, B:46, r:1.1, dynamic_load:30000, static_load:17800, limit_speed:9000,  weight:1.05, frame_no:'', position:'', note:'带P座' },

  // ===== 7000 系列（角接触球轴承）=====
  { model:'7205B', series:'7000', bearing_type:'角接触球轴承', d:25, D:52, B:15, r:1.0, dynamic_load:14000, static_load:7100,  limit_speed:15000, weight:0.13, frame_no:'', position:'', note:'40°接触角' },
  { model:'7206B', series:'7000', bearing_type:'角接触球轴承', d:30, D:62, B:16, r:1.0, dynamic_load:18500, static_load:9300,  limit_speed:13000, weight:0.21, frame_no:'', position:'', note:'40°接触角' },
  { model:'7207B', series:'7000', bearing_type:'角接触球轴承', d:35, D:72, B:17, r:1.1, dynamic_load:25000, static_load:12500, limit_speed:12000, weight:0.31, frame_no:'', position:'', note:'40°接触角' },
  { model:'7208B', series:'7000', bearing_type:'角接触球轴承', d:40, D:80, B:18, r:1.1, dynamic_load:30500, static_load:15800, limit_speed:11000, weight:0.4,  frame_no:'', position:'', note:'40°接触角' },
];
