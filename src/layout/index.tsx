import React, { Suspense, useEffect } from 'react';
import { LaptopOutlined, NotificationOutlined, UserOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Layout, Menu, Skeleton, theme } from 'antd';
import { NavLink, Outlet, useNavigate } from 'react-router';

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
const menus: MenuProps['items'] = [
    {
        key: "/",
        label: "项目"
    }, {
        key: "/sample",
        label: "样本"
    },
]

const Test = ()=>{
    useEffect(()=>{
        console.log("wssssssssssssssssssss")
    },[])
    return <Skeleton active></Skeleton>
}
const App: React.FC = () => {
    const navigate = useNavigate();
    const onMenuClick = (key: string) => {
        console.log(key)
        navigate(key);
    }
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return (
        <Layout
            style={{ padding: '24px 0', background: colorBgContainer, borderRadius: borderRadiusLG }}
        >
            <Sider style={{ background: colorBgContainer }} width={200}>
                <Menu
                    mode="inline"
                    onSelect={k => onMenuClick(k.key)}
                    defaultSelectedKeys={['/']}
                    defaultOpenKeys={['/']}
                    style={{ height: '100%' }}
                    items={menus}
                />
                {/* <nav>
                    <NavLink to="/" end>
                        Home
                    </NavLink>
                    <NavLink to="/sample" end>
                        sample
                    </NavLink>

                </nav> */}

            </Sider>

            <Content style={{ padding: '0 24px', minHeight: 280 }}>
                <Suspense fallback={<Test></Test>}>
                    <Outlet />
                </Suspense>
            </Content>
        </Layout>
    );
};

export default App;