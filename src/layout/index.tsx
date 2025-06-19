import React, { Suspense, useEffect, useState } from 'react';
import { LaptopOutlined, NotificationOutlined, UserOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Breadcrumb, Layout, Menu, Skeleton, theme } from 'antd';
import { NavLink, Outlet, useLocation, useNavigate, useParams } from 'react-router';
import { Header } from 'antd/es/layout/layout';
import { useSelector } from 'react-redux';

const { Content, Sider } = Layout;



const items2: MenuProps['items'] = [UserOutlined, LaptopOutlined, NotificationOutlined].map(
    (icon, index) => {
        const key = String(index + 1);

        return {
            key: `sub${key}`,
            icon: React.createElement(icon),
            label: `subnav ${key}`,
            children: Array.from({ length: 4 }).map((_, j) => {
                const subKey = index * 4 + j + 1;
                return {
                    key: subKey,
                    label: `option${subKey}`,
                };
            }),
        };
    },
);


const Test = () => {
    // useEffect(() => {
    //     console.log("wssssssssssssssssssss")
    // }, [])
    return <Skeleton active></Skeleton>
}
const App: React.FC = () => {
    const { project } = useParams()

    const navigate = useNavigate();
    const location = useLocation();
    const [leftMenus, setLeftMenus] = useState<any>([])

    const onMenuClick = (key: string) => {
        console.log(key)
        navigate(key);
    }
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const menu0: MenuProps['items'] = [
        {
            key: `${project}`,
            label: "项目介绍"
        }, {
            key: `${project}/sample`,
            label: "检测样本"
        }, {
            key: `${project}/pipeline-card`,
            label: "流程管道"
        }, {
            key: `${project}/analysis-result`,
            label: "分析结果"
        }
    ]
    const menu1: MenuProps['items'] = [
        {
            key: `${project}/sample-qc`,
            label: "样本质控"
        }, {
            key: `${project}/meta_genome/remove-host`,
            label: "去宿主"
        }, {
            key: `${project}/meta_genome/reads-based-abundance-analysis`,
            label: "基于Reads的丰度分析"
        }, {
            key: `${project}/meta_genome/recovering-mag`,
            label: "重构MAG"
        }, {
            key: `${project}/meta_genome/abundance-meta`,
            label: "丰度分析"
        }, {
            key: `${project}/meta_genome/function-analysis`,
            label: "功能分析"
        }, {
            key: `${project}/meta_genome/abundance`,
            label: "old丰度分析"
        }
    ]
    // individual meta
    const menu2: any = [
        // {
        //     key: `${project}/single_genome`,
        //     label: "项目介绍"
        // }, {
        //     key: `${project}/single_genome/sample`,
        //     label: "检测样本"
        // }, 
        {
            key: `${project}/single_genome/assembly`,
            label: "单菌组装"
        }, {
            key: `${project}/single_genome/gene-prediction`,
            label: "基因预测"
        }, {
            key: `${project}/single_genome/gene-annotation`,
            label: "基因注释"
        }, , {
            key: `${project}/single_genome/gene-expression`,
            label: "基因表达"
        },
        {
            key: `${project}/single_genome/mutation`,
            label: "突变检测"
        }, {
            key: `${project}/single_genome/mutation-compare`,
            label: "突变比较"
        }
    ]
    useEffect(() => {
        setLeftMenus(menu1)
        // console.log("2222222222222222")
        // console.log(menuItems)
    }, [])
    const items = [
        {
            key: "menu0",
            label: "实验设计"
        }, {
            key: "menu1",
            label: "宏基因组"
        }, {
            key: "menu2",
            label: "单菌基因组"
        },
    ]
    return (
        <Layout>
            <Header style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ color: "#fff",marginRight:"1rem" }} >BRAVE</div>
                {/* 单菌组装数据挖掘(lactobacillus murinus) */}
                <Menu
                    theme="dark"
                    mode="horizontal"
                    defaultSelectedKeys={['1']}

                    // onSelect={(k) => {
                    //     if (k.key == "menu0") {
                    //         setLeftMenus(menu0)
                    //         navigate(`${project}`);
                    //     }
                    //     if (k.key == "menu1") {
                    //         setLeftMenus(menu1)
                    //         navigate(`${project}/meta_genome/remove-host`);
                    //     } else if (k.key == "menu2") {
                    //         setLeftMenus(menu2)
                    //         navigate(`${project}/single_genome/assembly`);
                    //     }
                    //     console.log(k.key)
                    // }}
                    items={menu0}
                    onSelect={k => onMenuClick(k.key)}
                    style={{ flex: 1, minWidth: 0 }}
                />
            </Header>
            <Layout
                style={{ padding: '24px 0', background: colorBgContainer, borderRadius: borderRadiusLG }}
            >
                {/* <Sider style={{ background: colorBgContainer }} width={120}>
                    <Menu
                        mode="inline"
                        onSelect={k => onMenuClick(k.key)}
           
                        style={{ height: '100%' }}
                        items={leftMenus}
                    />
                 

                </Sider> */}

                <Content style={{ padding: '0 24px', minHeight: "100vh" }}>
                    <Suspense key={location.key} fallback={<Test></Test>}>
                        <Outlet />
                    </Suspense>
                </Content>
            </Layout>
        </Layout>

    );
};

export default App;