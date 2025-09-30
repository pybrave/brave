import asyncio
import aiohttp
from Bio import Entrez
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

async def get_pmc_fulltext(pmcid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc",
        "id": pmcid,
        "rettype": "full",
        "retmode": "xml",
        "api_key": "b4761f644bab9143a8bbef4c1d124227d208"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            print(f"查询全文: {pmcid}")
            text = await resp.text()

            try:
                root = ElementTree.fromstring(text)
                # 提取<body>内所有<p>内容，和之前的同步例子类似
                ns = ''
                if root.tag.startswith('{'):
                    ns = root.tag.split('}')[0] + '}'

                body = root.find(f".//{ns}body")
                if body is None:
                    print("未找到<body>节点，返回空全文")
                    fulltext = ""
                else:
                    paragraphs = []
                    def recursive_extract(element):
                        for child in element:
                            if child.tag == f"{ns}p":
                                paragraphs.append(''.join(child.itertext()).strip())
                            else:
                                recursive_extract(child)
                    recursive_extract(body)
                    fulltext = "\n\n".join(paragraphs)

                return fulltext
            except Exception as e:
                print(f"解析全文XML出错，返回内容:\n{text}")
                raise e