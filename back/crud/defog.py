from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
import PyPDF2
import docx
import io

from model import QueryRequest

defog = APIRouter(prefix="/defog", tags=["技术准备生成"])

embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key="sk-18f6c9127c2048ad9eb5abab82e9e1bf"
)

feature_vectorstore = Chroma(
    persist_directory="D:/rag_db",
    embedding_function=embeddings,
    collection_name="feature",
)

llm = ChatTongyi(
    model="qwen3.7-max",
    dashscope_api_key="sk-18f6c9127c2048ad9eb5abab82e9e1bf"
)

prompts_template = """
你是一个讲中文的电机技术配置提取器，请严格根据以下规则处理用户输入:
1. 用户输入是一段电机技术要求或订单描述。
2. 你的任务是从中**识别出明确提及的非默认配置项**。
3. **只能输出{feature_context}中的合法值（大小写敏感，格式严格）**：
4. 输出规则：
   - 仅输出一行
   - 多个值用英文逗号分隔（,）
   - 不要：解释、编号、多余文字、随机资料、与电机本体无关的包装信息、海拔高度、环境温度、标志色、漆膜（工艺相关）
   - 如果没有匹配项，输出空字符串（即什么都不写）
注意：
- “面漆”相关必须输出为“面漆:色号”格式，如“面漆:RAL5012”
示例输出：
F,SKF,V1,中英文铭牌,堵头,面漆:B05
用户问题：
{question}
回答：
"""
prompt = ChatPromptTemplate.from_template(prompts_template)
chain = prompt | llm


@defog.post("/question")
async def rag_query(request: Request):
    """RAG查询，支持纯文本或带文件"""
    try:
        content_type = request.headers.get('content-type', '')
        file = None

        # 解析请求
        if 'multipart/form-data' in content_type:
            form = await request.form()
            query = form.get('query', '')
            file = form.get('file')
        else:
            body = await request.json()
            query_request = QueryRequest(**body)
            query = query_request.query

        # 如果有文件，解析并合并到query
        if file and hasattr(file, 'filename') and file.filename:
            content = await file.read()
            text = ''

            if file.filename.endswith('.pdf'):
                pdf_file = io.BytesIO(content)
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            elif file.filename.endswith('.docx') or file.filename.endswith('.doc'):
                doc_file = io.BytesIO(content)
                doc = docx.Document(doc_file)
                text = '\n'.join([para.text for para in doc.paragraphs])

            if text.strip():
                query = query + '\n' + text

        feature_docs = feature_vectorstore.get()['documents']

        feature_context = "\n\n".join(feature_docs)

        _query = query + '//上述是订单的要求，请回答我完整的技术准备资料'

        response = chain.invoke({
            "feature_context": feature_context,
            "question": _query
        })

        return {
            "code": 200,
            "message": "查询成功",
            "output": response.content.strip(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")