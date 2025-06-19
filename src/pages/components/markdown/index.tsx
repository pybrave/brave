import { FC } from "react"

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

const Markdown: FC<any> = ({data}) => {

    return <>
        <ReactMarkdown children={data} rehypePlugins={[rehypeKatex]} remarkPlugins={[remarkGfm, remarkMath]}></ReactMarkdown>

    </>
}

export default Markdown