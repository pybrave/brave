import { FC, useState } from "react"
import Markdown from "../../components/markdown"
import { Tabs } from "antd"

import {chinese} from './chinese'
import {english} from './english'
import {introduction} from './introduction'

import {EmbedLLM}  from '../../components/embed-llm'
const Project:FC<any> = ()=>{
    const [data,setData] = useState<any>(introduction)
    const onChange = (value:any)=>{
        if(value =="chinese"){
            setData(chinese)
        }else if(value =="english"){
            setData(english)
        }
    }
    return <div style={{ maxWidth: "1000px", margin: "1rem auto" }}>
        {/* <Tabs onChange={onChange} items={[
            {
                key:"english",
                label:"英文",
            },{
                key:"chinese",
                label:"中文",
            }
        ]}></Tabs> */}
        {/* <EmbedLLM content={"hi"}>LLM</EmbedLLM> */}
        <Markdown data={data}></Markdown>
    </div>
}

export default Project