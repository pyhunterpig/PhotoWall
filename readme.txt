配置说明

1.配置文件为遵循json格式
2.下面为主要配置
a.活动主题
"event_title":"PyCon 2011 China"
b.头像格式
"avatar_format":"png"
c.照片墙列数，每张照片都为正方形
"wall_cols":15
d.照片墙刷新速度，单位微秒
"bg_change_speed":3000
e.抽奖头像刷新速度，单位微秒
"lottery_change_speed":78
f.中间部分主logo显示配置，postion的单位为每个小图片宽度，配置分别为x,y和宽度，bg_color为背景色配置
"main_logo": {"postion":[6, 3, 4], "bg_color":"#eee"
g.抽奖人名显示配置，font_size：字体大小，postion为相对于中间图片的坐标，font_color为字体颜色
"lottery_people_name": {"font_size": 30, "position":[90, 280], "font_color":"#fff"}

3.抽奖按空格，照片墙滚动按回车
4.产生抽奖结果后，按s建保存