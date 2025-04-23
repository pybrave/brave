// https://reactrouter.com/start/data/installation
import { FC, lazy } from "react";
import Layout  from "@/layout";
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router";

const Sample = lazy(() => import(/* webpackChunkName: "sample-list" */ '@/pages/sample'));
const Project = lazy(() => import(/* webpackChunkName: "project-list" */ '@/pages/project'));

const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout/>,
        children:[
            {
                path:"/",
                element:<Project/>
            },{
                path:"/sample",
                element:<Sample/>
            }
        ]
    },
]);

// const RenderRouter: FC = () => {
//     const element = useRoutes(router);

//     return element;
// };
const RenderRouter: FC = () => {

    return <RouterProvider router={router} />;
};
export default RenderRouter;