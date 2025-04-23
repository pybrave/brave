import { FC, Suspense } from "react"
import RenderRouter from './routes';
import { Skeleton } from "antd";

const App: FC<any> = () => {

  return <>
    {/* <Suspense fallback={<Skeleton active></Skeleton>}>

    </Suspense> */}
    
    <RenderRouter></RenderRouter>

  </>
}

export default App
