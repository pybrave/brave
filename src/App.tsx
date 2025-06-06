import { FC } from "react"
import RenderRouter from './routes';
import { HashRouter } from "react-router";

const App: FC<any> = () => {

  return <>
    {/* <Suspense fallback={<Skeleton active></Skeleton>}>

    </Suspense> */}
    <HashRouter>
      <RenderRouter></RenderRouter>
    </HashRouter>

  </>
}

export default App
