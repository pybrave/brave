import { FC } from "react"
import {Image} from "antd";

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

const Markdown: FC<any> = ({data}) => {

    return <>
        <ReactMarkdown  
        children={data} 
        rehypePlugins={[rehypeKatex]} 
        remarkPlugins={[remarkGfm, remarkMath]}
        components={{
            img: ({ node,src, ...props }) => (
              // <>{JSON.stringify({...props})}</>
              <Image
                // {...props}
                src={src}
                style={{ maxWidth: '50%', height: 'auto',margin: '1rem auto', display: 'block' }}  
                alt={props.alt || ''}
              ></Image>
            )
          }}></ReactMarkdown>

    </>
}

export default Markdown