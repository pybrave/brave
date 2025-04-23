import { Skeleton } from "antd"
import { FC, Suspense } from "react"
import { Outlet } from "react-router"

const Layout: FC<any> = () => {
    return <>
        <Suspense fallback={<Skeleton active></Skeleton>}>
            <Outlet />
        </Suspense>
    </>
}

export default Layout