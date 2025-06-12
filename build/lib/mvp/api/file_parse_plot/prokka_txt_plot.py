import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd

def parse_data(request_param):
    file_path = request_param['file_path']
    data = {}
    with open(file_path, "r") as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(":", 1)
                key = key.strip()
                value = value.strip()
                # 只保留数值项用于画图
                if value.isdigit():
                    data[key] = int(value)
    return {"data":data}

def parse_plot(data ,request_param):
    data = data['data']
    plot_data = {k:v for k,v in data.items() if k not in ['contigs','bases','gene','repeat_region']}
    # 饼图标签和数值
    labels = list(plot_data.keys())
    sizes = list(plot_data.values())

    # 可选颜色（自动分配也可以）
    colors = plt.cm.Paired.colors

    # 绘图
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    plt.title("Genome Feature Composition")
    plt.axis('equal')  # 保证圆形
    plt.tight_layout()
    return plt
    # plt.show()
    # 保存到内存并转 base64
    # buf = BytesIO()
    # plt.savefig(buf, format='png', bbox_inches='tight')
    # plt.close()  # 关闭图像以释放内存
    # buf.seek(0)

    # img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # return "data:image/png;base64," + img_base64

