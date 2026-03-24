# 工具返回与文档编写规范

## 1. 成功返回值标准

- 只返回完成当前显式任务所必需的数据。
- 不返回内部执行信息，比如 `taskId`。
- 不返回敏感或不必要的访问字段，比如 `token`。
- 不返回调试或旁路状态，比如 `shareLinkError`。
- 不回显请求参数，除非该字段本身就是用户完成当前任务所必需的结果。
- 对于会生成新结果文档的工具，只要后端返回了 `resultDocumentId`，就应始终返回。
- `shareUrl` 可以返回，因为它直接服务于“下载结果文件”这个任务。
- `expiresAt` 只有接口确实提供时才返回。

## 2. `resultDocumentId` 的判断标准

如果生成出来的是一个新的结果文档，而且这个结果文档后续还可能继续被别的 tool 使用，那么 `resultDocumentId` 属于必要返回。

这不是多余回显，而是链式操作的必要依赖。

因此，当前对转换类、创建类工具的成功返回字段标准为：

- `success`
- `message`
- `resultDocumentId`
- `shareUrl`
- `expiresAt`

## 3. 说明文档标准

- 保留关键前置说明，特别是 `CRITICAL PREREQUISITE`。
- 保留 `Workflow`，因为这能说明字段来源和调用顺序。
- `Returns` 里要准确写最小返回字段，不多写已经删掉的字段。
- 如果某个字段之所以保留，是因为后续操作必须用到，就在 `Returns` 里直接说明原因。
- 不强制写 `Privacy behavior` 段落；只要实际返回已经收紧，并且必要依赖写清楚，就足够。
- 文档缩进必须干净，`Returns` 下的各项保持同一级，不要出现假嵌套。

## 4. 输入字段处理标准

- 输入参数可以保留，因为 tool 本身需要它们执行。
- 但输入参数一般不应在成功返回里原样回显。
- 特别是 `url`、文件名、页面范围、尺寸、格式这类参数，默认不回显。
- 如果某个输入字段可能带用户信息、查询参数、session 信息，就更不应该回显。

## 5. 错误返回标准

- 继续保留现有统一错误格式。
- 当前主要收紧的是成功返回，不是去改整套异常协议。

## 6. MCP Tool Annotations 基线

`readOnlyHint` 与 `destructiveHint` 必须对每个已注册的 MCP tool 显式设置为布尔值，不能省略，也不能依赖默认值。（https://modelcontextprotocol.io/legacy/concepts/tools#tool-annotations）

判定原则：

- `readOnlyHint=true`：工具只读取、查询、展示，不创建、不删除、不修改任何文档或远端状态。
- `readOnlyHint=false`：工具会创建、上传、生成结果文档、创建分享链接，或以任何方式修改系统状态。
- `destructiveHint=true`：工具会直接删除、覆盖、清空或永久破坏现有资源本身。
- `destructiveHint=false`：工具虽然会写入或生成结果，但如果原文档/原资源仍然保留、只是产出一个新的派生结果，就不应标记为破坏性。

## 7. Tool Annotations 清单

### A. `readOnlyHint=true`, `destructiveHint=false`

- `get_pdf_properties`
	理由：仅读取并返回 PDF 属性与元数据，不创建、不删除、不修改文档。
- `show_pdf_viewer`
	理由：仅返回 viewer widget 展示信息，不修改任何文档或服务端状态。
- `show_pdf_tools`
	理由：仅返回上传工具 widget 展示信息，本身不执行上传、删除或转换。

### B. `readOnlyHint=false`, `destructiveHint=true`

- `delete_document`
	理由：永久删除云端文档，直接破坏现有资源本身。

### C. `readOnlyHint=false`, `destructiveHint=false`

- `upload_document`
	理由：上传会新增文档资源，但不会破坏已有资源。
- `create_share_link`
	理由：创建分享链接属于新增状态，不删除、不覆盖文档。
- `pdf_compare`
	理由：生成新的对比结果文档，不破坏输入文档。
- `pdf_to_word`
	理由：生成新的 Word 结果文档，不修改原 PDF。
- `pdf_to_excel`
	理由：生成新的 Excel 结果文档，不修改原 PDF。
- `pdf_to_ppt`
	理由：生成新的 PowerPoint 结果文档，不修改原 PDF。
- `pdf_to_text`
	理由：生成新的文本结果文档，不修改原 PDF。
- `pdf_to_html`
	理由：生成新的 HTML 结果文档，不修改原 PDF。
- `pdf_to_image`
	理由：生成新的图片结果文档，不修改原 PDF。
- `pdf_from_word`
	理由：根据 Word 创建新 PDF，不破坏输入文档。
- `pdf_from_excel`
	理由：根据 Excel 创建新 PDF，不破坏输入文档。
- `pdf_from_ppt`
	理由：根据 PowerPoint 创建新 PDF，不破坏输入文档。
- `pdf_from_text`
	理由：根据文本创建新 PDF，不破坏输入文档。
- `pdf_from_image`
	理由：根据图片创建新 PDF，不破坏输入文档。
- `pdf_from_html`
	理由：根据 HTML 创建新 PDF，不破坏输入文档。
- `pdf_from_url`
	理由：根据 URL 抓取并生成新 PDF，不删除或覆盖既有资源。
- `pdf_merge`
	理由：生成合并后的新 PDF，不修改原始输入文档。
- `pdf_split`
	理由：生成拆分结果 ZIP，不修改原始输入文档。
- `pdf_extract_pages`
	理由：生成新的抽取结果 PDF，不修改原始输入文档。
- `pdf_extract_text`
	理由：生成新的文本结果文档，不修改原始输入文档。
- `pdf_compress`
	理由：生成新的压缩结果 PDF，不删除、不覆盖原始文档。
- `pdf_flatten`
	理由：虽然输出文档被压平，但它是新的派生结果，原始文档仍保留，因此不属于对现有资源的破坏性更新。
- `pdf_linearize`
	理由：生成新的线性化结果 PDF，不破坏原始文档。
- `pdf_manipulate`
	理由：即使包含删除页等操作，当前实现也是生成新的结果文档并返回 `resultDocumentId`，不直接修改原文档，因此不标记为破坏性。
- `pdf_delete_pages`
	理由：删除页发生在新生成的结果文档中，原始输入文档仍保留，因此不属于破坏现有资源。
- `pdf_rotate_pages`
	理由：生成新的旋转结果 PDF，不删除页面，也不破坏原始输入文档。
- `pdf_reorder_pages`
	理由：生成新的重排结果 PDF，不删除页面，也不破坏原始输入文档。
- `pdf_remove_password`
	理由：虽然输出结果变为无密码版本，但这是新的派生文档，原受保护文档仍保留，因此不属于破坏现有资源。

## 8. 维护要求

- 新增 MCP tool 时，必须在实现中显式填写 `annotations`，并同步更新本清单。
- `destructiveHint` 应基于工具是否直接破坏现有资源来判断；如果只是生成一个语义上“删改后”的新文档，而原文档不变，通常仍应为 `false`。
- 若后续工具行为发生变化，必须同时更新代码中的 `annotations` 与本 POLICY 文档中的理由说明。