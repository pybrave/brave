import { FC } from "react"

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
            img: ({ node, ...props }) => (
              <img
                {...props}
                style={{ maxWidth: '50%', height: 'auto',margin: '1rem auto', display: 'block' }}  
                alt={props.alt || ''}
              />
            )
          }}></ReactMarkdown>

    </>
}

export default Markdown