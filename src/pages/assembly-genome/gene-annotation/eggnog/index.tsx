import { Button, Form, Input, InputNumber } from "antd"
import { FC } from "react"
import { formatUrl } from '@/utils/utils'
const Eggnog: FC<any> = ({ record, plot }) => {
    return <>
        {record && <>
            <Button type="primary" onClick={() => {
                plot({
                    name:"查看注释结果",
                    saveAnalysisMethod:"print_gggnog",
                    moduleName: "eggnog",
                    params: { "file_path": record.content.annotations,
                        "input_faa": record.content.input_faa
                     },
                    tableDesc: `
| 列                      | 含义                                 |
| ---------------------- | ---------------------------------- |
| #query                 | 查询序列的 ID                           |
| seed\_eggNOG\_ortholog | 种子同源物（最匹配的 EggNOG 同源群）             |
| seed\_ortholog\_evalue | 种子同源物的比对 E 值                       |
| seed\_ortholog\_score  | 比对分数                               |
| eggNOG\_OGs            | 所属的 EggNOG 同源群（多个可能）               |
| max\_annot\_lvl        | 最大注释等级（例如 arCOG, COG, NOG 等）       |
| COG\_category          | 功能分类（一个或多个字母，详见 EggNOG 分类）         |
| Preferred\_name        | 推荐的基因名称                            |
| GOs                    | GO（Gene Ontology）注释                |
| EC                     | 酶编号（Enzyme Commission number）      |
| KEGG\_ko               | KEGG 通路编号                          |
| KEGG\_Pathway          | KEGG 所属路径                          |
| KEGG\_Module           | KEGG 功能模块                          |
| KEGG\_Reaction         | KEGG 化学反应编号                        |
| KEGG\_rclass           | KEGG 反应类别                          |
| BRITE                  | KEGG BRITE 分类信息                    |
| KEGG\_TC               | KEGG Transporter Classification 编号 |
| CAZy                   | 碳水化合物活性酶分类                         |
| BiGG\_Reaction         | BiGG 化学反应编号                        |
| PFAMs                  | 蛋白结构域信息（来自 Pfam 数据库）               |

                    `
                })
                
            }}> 查看注释结果</Button >
            <Button type="primary" onClick={() => {
                plot({
                    saveAnalysisMethod:"eggnog_kegg_table",
                    moduleName: "eggnog_kegg",
                    params: { "file_path": record.content.annotations },
                    tableDesc: `
                    `,
                    name:"提取KEGG注释结果"
                })

            }}>提取KEGG注释结果</Button>
        </>

        }

    </>
}

export default Eggnog