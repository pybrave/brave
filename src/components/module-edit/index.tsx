import { message, Modal } from "antd"
import axios from "axios"
import { FC, useEffect, useState } from "react"
import { message as $message } from 'antd';
import TextArea from "antd/es/input/TextArea";
import Typography from "antd/es/typography/Typography";
const ModuleEdit: FC<any> = ({ visible, onClose, params, callback }) => {
    if (!visible) return null;
    const [data, setData] = useState<any>()
    const [messageApi, contextHolder] = message.useMessage();

    const getModuleContent = async (params: any) => {
        try {
            const resp = await axios.post("/get-module-content", params)
            console.log(resp)
            setData(resp.data)
        } catch (error: any) {
            messageApi.error(`${error.response.data.detail}`)
        }


    }
    useEffect(() => {
        getModuleContent(params)
    }, [JSON.stringify(params)])
    return <>
        {contextHolder}
        <Modal title="查看文件" open={visible} onClose={onClose} onCancel={onClose}>
            {/* {JSON.stringify(data)} */}
            <ul>
                <li>module:{data?.module}</li>
                <li>path:{data?.path}</li>
            </ul>
            <Typography>
                <pre>
                    {data?.content}
                </pre>
            </Typography>

            {/* <TextArea value={data?.content} disabled rows={10}>
            </TextArea> */}
        </Modal>
    </>
}

export default ModuleEdit