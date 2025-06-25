import { Modal } from "antd"
import { FC } from "react"

const CreatePipeline:FC<any> = ({open,setOpen,data,createType})=>{


    return <>
        <Modal title="创建流程" open={open} onClose={()=>setOpen(false)} onCancel={()=>setOpen(false)}>
            {JSON.stringify(data)}
        </Modal>
    </>
}

export default CreatePipeline