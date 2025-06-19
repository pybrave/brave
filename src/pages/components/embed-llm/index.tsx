import { FC, useState } from "react"
import { Ollama } from 'ollama/browser'
import { Button, Spin } from "antd"

export const EmbedLLM: FC<{ content: any,children:any }> = ({  content,children }) => {
    // let url = "https://mbiolance.com/cloud-gateway/service-deepseek/"
    // let url="http://10.110.1.11:11434"
    let model = "llama3.2:1b"
    // if (import.meta.env.DEV) {
    //     url = "http://192.168.10.176:8889/"
    //     model = "llama3.2:1b"
    // }
    const [result, setResult] = useState('');
    const [think, setThink] = useState('');
    const [content0, setContent] = useState('');

    const [loading, setLoading] = useState<boolean>(false)

    // const ollama = new Ollama({ host: url, headers: { "Authorization": `Bearer ${localStorage.getItem('Authorization')}` } })
    const ollama = new Ollama({ host: window.location.origin, headers: { "Authorization": `Bearer ${localStorage.getItem('Authorization')}` } })

    const chat = async () => {
        const response = await ollama.chat({
            model: model,
            messages: [{ role: 'user', content: content }],
            stream: true
        })
        for await (const part of response) {
            // process.stdout.write(part.message.content)
            console.log(part.message.content)
            // controller.enqueue(encoder.encode(part.message.content)); // 将内容写入流
        }
    }
    const chat2 = async () => {
        if(!content){
            // message.error(`该报告没有生成提示词，请联系管理员配置!`)
            return
        }
        setResult("")
        setThink('')
        setContent('')
        const encoder = new TextEncoder();
        const readableStream = new ReadableStream({
            async start(controller) {
                // controller.enqueue(encoder.encode("aaaaaaaaaaa"));
                setLoading(true)
                // controller.enqueue(encoder.encode("done"));
                const response = await ollama.chat({
                    model: model,
                    messages: [{ role: 'user', content: content }],//[{ role: 'user', content: 'Why is the sky blue?' }],
                    stream: true
                })
                let isThink = true
                for await (const part of response) {
                    // process.stdout.write(part.message.content)
                    console.log(part.message.content)
                    // controller.enqueue(encoder.encode(part.message.content)); // 将内容写入流
                    // const chunk = decoder.decode(value);
                    let chunk = part.message.content
                    if (chunk == "<think>") {
                        chunk = ""
                        // setThink()
                        isThink = true
                    }
                    if (chunk == "</think>") {
                        chunk = ""
                        isThink = false
                    }
                    if (isThink) {
                        setThink(prev => prev + chunk);

                    } else {
                        setResult(prev => prev + chunk);
                    }
                    setContent(prev => prev + chunk)
                }
                controller.close();
                setLoading(false)

            },
        });
        return new Response(readableStream);
    }

    // const md = markdownit({ html: false })
    // const result = 

    return <>
        <Button type="link" onClick={chat2}> {loading ? "生成中..." : children}</Button>
        <Spin size="small" spinning={loading} style={{ display: "inline" }}>

        </Spin>

        <div>
            {/* {result} */}
            {/* {think && <div className="think" dangerouslySetInnerHTML={{ __html: md.render(think) }} />}
            {<div dangerouslySetInnerHTML={{ __html: md.render(result) }} />} */}
            {think}
            {result}
        </div>
      

    </>
}
// http://localhost:11434/api/generate
// http://10.110.1.12:11434/api/chat
// curl http://10.110.1.11:5174/api/chat -d '{
//        "model": "llama3.2:1b",
//        "prompt":"Why is the sky blue?"
//      }'
// curl http://10.110.1.11:5174/api/generate -d 
// '{
//     "model": "deepseek-r1:7b",
//     "messages": [
//         {
//             "role": "user",
//             "content": "你好"
//         }
//     ],
//     "stream": true
// }'
export default EmbedLLM