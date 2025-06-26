// https://reactrouter.com/start/data/installation
import { FC, lazy, useEffect, useState } from "react";
import Layout from "@/layout";
import {
    // createBrowserRouter,
    RouteObject,
    // RouterProvider,
    useRoutes,
} from "react-router";
import { setMenuItems, setSelectedKey } from '../store/menuSlice'


// const router = createBrowserRouter([
//     {
//         path: "/",
//         element: <Layout />,
//         children: [
//             {
//                 path: "/",
//                 Component: Project
//             }, {
//                 path: "/sample",
//                 Component:Sample

//             }
//         ]
//     },
// ]);
// const RenderRouter: FC = () => {

//     return <RouterProvider router={router} />;
// };
const Sample = lazy(() => import('@/pages/sample'));
const Project = lazy(() => import('@/pages/project'));
const Mutation = lazy(() => import('@/pages/assembly-genome/mutation'));
const MutationCompare = lazy(() => import('@/pages/mutation-compare'));
const Abundance = lazy(() => import('@/pages/abundance'));
const Assembly = lazy(() => import('@/pages/assembly-genome/assembly'));
const GenePrediction = lazy(() => import('@/pages/assembly-genome/gene-prediction'));
const GeneAnnotation = lazy(() => import('@/pages/assembly-genome/gene-annotation'));
const GeneExpressison = lazy(() => import('@/pages/assembly-genome/gene-expression'));
const ReadsBasedAbundanceAnalysis = lazy(() => import('@/pages/meta-analysis/reads-based-abundance-analysis'));
const RemoveHost = lazy(() => import('@/pages/meta-analysis/remove-host'));
const AbundanceMeta = lazy(() => import('@/pages/meta-analysis/abundance'));
const RecoveringMag = lazy(() => import('@/pages/meta-analysis/recovering-mag'));
const SampleQC = lazy(() => import('@/pages/sample/sample-qc'));
const FunctionAnalysis = lazy(() => import('@/pages/meta-analysis/function-analysis'));
const PipelineCard = lazy(() => import('@/pages/pipeline-card'));
const AnalysisResult = lazy(() => import('@/pages/analysis-result'));
const Literature = lazy(() => import('@/pages/literature'));

import Pipeline from '@/pages/components/pipeline'
import axios from "axios";
import { Skeleton } from "antd";
import { useDispatch } from "react-redux";


const childern = [
    {
        path: "/",
        element: <Project />
    }, {
        path: "/pipeline-card",
        element: <PipelineCard />
    }, {
        path: "/sample",
        element: <Sample />
    }, {
        path: "/sample-qc",
        element: <SampleQC />
    }, {
        path: "/analysis-result",
        element: <AnalysisResult />
    }, {
        path: "/literature",
        element: <Literature />
    }, {
        path: "/pipeline/:pipelineId",
        element: <Pipeline />
    },

    {
        path: "/:project/meta_genome/reads-based-abundance-analysis",
        element: <ReadsBasedAbundanceAnalysis />
    }, {
        path: "/:project/meta_genome/remove-host",
        element: <RemoveHost />
    }, {
        path: "/:project/meta_genome/recovering-mag",
        element: <RecoveringMag />
    },
    {
        path: "/:project/meta_genome/abundance-meta",
        element: <AbundanceMeta />
    },
    {
        path: "/:project/meta_genome/abundance",
        element: <Abundance />
    }, {
        path: "/:project/meta_genome/function-analysis",
        element: <FunctionAnalysis />
    },

    {
        path: "/:project/single_genome/mutation",
        element: <Mutation />
    }, {
        path: "/:project/single_genome/mutation-compare",
        element: <MutationCompare />
    }, {
        path: "/:project/single_genome/assembly",
        element: <Assembly />
    }, {
        path: "/:project/single_genome/gene-prediction",
        element: <GenePrediction />
    }, {
        path: "/:project/single_genome/gene-annotation",
        element: <GeneAnnotation />
    }, {
        path: "/:project/single_genome/gene-expression",
        element: <GeneExpressison />
    }
]

import {listPipeline} from '@/api/pipeline'
const RenderRouter: FC = () => {
    // const [routes, setRoutes] = useState<RouteObject[] | null>([]);
    // const dispatch = useDispatch()

   
    
    // const loadData = async () => {
    //     const data:any = await listPipeline(dispatch)
    //     const routes = data.flatMap((group:any) =>
    //         group.items.map((item:any) => ({
    //             path: `/${item.path}`,
    //             element: <Pipeline name={item.path} />
    //         }))
    //     );
    //     // console.log(routes)
    //     // const routes = resp.data.pipeline.map((item: any) => {
    //     //     return {
    //     // path: `/:project/${item.path}`,
    //     // element: <Pipeline name={item.path} />
    //     //     }
    //     // })
    //     const router: RouteObject[] = [
    //         {
    //             path: "/",
    //             element: <Layout />,
    //             children: [
    //                 ...routes,
    //                 ...childern,
    //             ]
    //         },
    //     ]
    //     // console.log(router)
    //     setRoutes(router)

    // }
    // useEffect(() => {
    //     loadData()
    //     // console.log("1111111111111111")
    // }, [])
    // const element = routes ? useRoutes(routes) : null;

    const routes: RouteObject[] = [
        {
            path: "/",
            element: <Layout />,
            children: [
                ...childern,
            ]
        },
    ]

    // const element = useRoutes(router);
    const element = useRoutes(routes)

    return element ;
    // return element;
};

export default RenderRouter;