// https://reactrouter.com/start/data/installation
import { FC, lazy } from "react";
import Layout from "@/layout";
import {
    // createBrowserRouter,
    RouteObject,
    // RouterProvider,
    useRoutes,
} from "react-router";


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
const Mutation = lazy(() => import( '@/pages/assembly-genome/mutation'));
const MutationCompare = lazy(() => import( '@/pages/mutation-compare'));
const Abundance = lazy(() => import( '@/pages/abundance'));
const Assembly = lazy(() => import( '@/pages/assembly-genome/assembly'));
const GenePrediction = lazy(() => import( '@/pages/assembly-genome/gene-prediction'));
const GeneAnnotation = lazy(() => import( '@/pages/assembly-genome/gene-annotation'));
const GeneExpressison = lazy(() => import( '@/pages/assembly-genome/gene-expression'));
const ReadsBasedAbundanceAnalysis = lazy(() => import( '@/pages/meta-analysis/reads-based-abundance-analysis'));
const RemoveHost = lazy(() => import( '@/pages/meta-analysis/remove-host'));
const AbundanceMeta = lazy(() => import( '@/pages/meta-analysis/abundance'));
const RecoveringMag = lazy(() => import( '@/pages/meta-analysis/recovering-mag'));
const SampleQC = lazy(() => import( '@/pages/sample/sample-qc'));
const FunctionAnalysis = lazy(() => import( '@/pages/meta-analysis/function-analysis'));

const router: RouteObject[] =[
    {
        path: "/",
        element: <Layout />,
        children: [
            {
                path: "/:project",
                element: <Project/>
            },{
                path: "/:project/sample",
                element:<Sample/>
            },{
                path: "/:project/sample-qc",
                element:<SampleQC/>
            },
            
            {
                path: "/:project/meta_genome/reads-based-abundance-analysis",
                element:<ReadsBasedAbundanceAnalysis/>
            },{
                path: "/:project/meta_genome/remove-host",
                element:<RemoveHost/>
            },{
                path: "/:project/meta_genome/recovering-mag",
                element:<RecoveringMag/>
            },
            {
                path: "/:project/meta_genome/abundance-meta",
                element:<AbundanceMeta/>
            },
            {
                path: "/:project/meta_genome/abundance",
                element:<Abundance/>
            },   {
                path: "/:project/meta_genome/function-analysis",
                element:<FunctionAnalysis/>
            }, 
            
            {
                path: "/:project/single_genome/mutation",
                element:<Mutation/>
            },{
                path: "/:project/single_genome/mutation-compare",
                element:<MutationCompare/>
            },{
                path: "/:project/single_genome/assembly",
                element:<Assembly/>
            },{
                path: "/:project/single_genome/gene-prediction",
                element:<GenePrediction/>
            },{
                path: "/:project/single_genome/gene-annotation",
                element:<GeneAnnotation/>
            },{
                path: "/:project/single_genome/gene-expression",
                element:<GeneExpressison/>
            }
        ]
    },
]
const RenderRouter: FC = () => {
    const element = useRoutes(router);
    return element;
};

export default RenderRouter;